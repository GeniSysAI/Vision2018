############################################################################################
#
# The MIT License (MIT)
# 
# TASS Facenet WebCam Receiver
# Copyright (C) 2018 Adam Milton-Barker (AdamMiltonBarker.com)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Title:         TASS Facenet WebCam Receiver
# Description:   Uses the Facenet Receiver to classify frames of a live feed.
# Configuration: required/confs.json
# Last Modified: 2018-08-17
#
# Example Usage:
#
#   $ python3.5 WebCam.py
#
############################################################################################

import os, sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import time, getopt, cv2, dlib, imutils, zmq, base64, json, time, urllib.request, threading 
import numpy as np

import JumpWayMQTT.Device as JWMQTTdevice
from tools.Helpers import Helpers
from tools.OpenCV import OpenCV as OpenCV
from tools.Facenet import Facenet as Facenet

from mvnc import mvncapi as mvnc
from imutils import face_utils
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from skimage.transform import resize

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver  import ThreadingMixIn
from io import BytesIO
from PIL import Image
from datetime import datetime

capture=None

class Receiver():
    
    def __init__(self):
        
        self.Helpers = Helpers()
        self._confs  = self.Helpers.loadConfigs()
        self.LogFile = self.Helpers.setLogFile(self._confs["aiCore"]["Logs"]+"/Local")  

        self.OpenCV  = OpenCV()

        self.configureSocket()
        
    def configureSocket(self):

        ###############################################################
        #
        # Configures the socket we will stream the frames to
        #
        ###############################################################
        
        context = zmq.Context()
        self.tassSocket = context.socket(zmq.SUB)
        self.tassSocket.bind("tcp://*:"+str(self._confs["Socket"]["port"]))
        self.tassSocket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        self.Helpers.logMessage(
                            self.LogFile,
                            "TASS",
                            "INFO",
                            "Connected To Socket: tcp://"+self._confs["Socket"]["host"]+":"+str(self._confs["Socket"]["port"]))
        
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            frameWait = 0
            fps = FPS().start()
            
            try:
                
                while True:
                    # grab the frame from the threaded video stream and resize it
                    # to have a maximum width of 400 pixels
                    frame = Receiver.tassSocket.recv_string()
                    frame = cv2.imdecode(np.fromstring(base64.b64decode(frame), dtype=np.uint8), 1)
                    
                    imgRGB=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = BytesIO()
                    jpg.save(tmpFile,'JPEG')
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.getbuffer().nbytes))
                    self.end_headers()
                    self.wfile.write( tmpFile.getvalue() )
                    #time.sleep(0.05)
                    fps.update()
                    frameWait = frameWait + 1
                    
            except:
                return
            return
            
        if self.path.endswith('.html'):
            src = '<img src="http://'+Receiver._confs["Cameras"][0]["Stream"]+':'+str(Receiver._confs["Cameras"][0]["StreamPort"])+'/cam.mjpg" />'
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode())
            self.wfile.write(src.encode())
            self.wfile.write('</body></html>'.encode())
            return
            
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global Receiver
	global Facenet
	Receiver = Receiver()
	Facenet = Facenet()

	try:
		server = ThreadedHTTPServer((Receiver._confs["Cameras"][0]["Stream"], Receiver._confs["Cameras"][0]["StreamPort"]), CamHandler)
		print("-- Server started on "+Receiver._confs["Cameras"][0]["Stream"]+":"+str(Receiver._confs["Cameras"][0]["StreamPort"]))
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()

if __name__ == '__main__':
	main()