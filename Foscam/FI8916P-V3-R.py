############################################################################################
#
# The MIT License (MIT)
# 
# GeniSys Foscam FI8916P V3 Receiver Device
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
# Title:         GeniSys Foscam FI8916P V3 Receiver Device
# Description:   Connects to the stream from a Foscam FI8916P V3, processes and streams the 
#                modified stream.
# Configuration: required/confs.json
# Last Modified: 2018-10-07
#
# Example Usage:
#
#   $ python3.5 FI8916P-V3-R.py
#
############################################################################################

import time, getopt, cv2, dlib, imutils, zmq, base64, json, time, urllib.request, threading 

import JumpWayMQTT.Device as jumpWayCL
import numpy              as np

from datetime          import datetime
from skimage.transform import resize
from imutils           import face_utils
from flask             import Flask, request

from tools.Helpers     import Helpers 
from tools.JumpWay     import JumpWay
from tools.OpenCV      import OpenCV

from imutils           import face_utils
from imutils.video     import WebcamVideoStream
from imutils.video     import FPS
from skimage.transform import resize

from http.server       import HTTPServer, BaseHTTPRequestHandler
from socketserver      import ThreadingMixIn
from io                import BytesIO
from PIL               import Image

app = Flask(__name__)

class Receiver():
    
    def __init__(self):

        ###############################################################
        #
        # Sets up all default requirements and placeholders 
        # needed for the NLU engine to run. 
        #
        ###############################################################
        
        self.Helpers       = Helpers()
        self._confs        = self.Helpers.loadConfigs()
        self.LogFile       = self.Helpers.setLogFile(self._confs["aiCore"]["Logs"]+"/Foscam") 

        self.OpenCV        = OpenCV()
        self.OpenCVCapture = None

        self.configureSocket()
        
    def configureSocket(self):

        ###############################################################
        #
        # Configures and connects to the socket. 
        #
        ###############################################################
        
        context = zmq.Context()
        self.tassSocket = context.socket(zmq.SUB)
        self.tassSocket.bind("tcp://*:"+str(self._confs["Socket"]["port"]))
        self.tassSocket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

        self.Helpers.logMessage(
                            self.LogFile,
                            "Streamer",
                            "INFO",
                            "Connected To Socket: tcp://"+self._confs["Socket"]["host"]+":"+str(self._confs["Socket"]["port"]))
            
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
        
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            count = 0
                
            while True:

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

def main():
    
    global Receiver
    
    Receiver = Receiver()
    
    try:
        server = ThreadedHTTPServer((Receiver._confs["Cameras"][0]["Stream"], Receiver._confs["Cameras"][0]["StreamPort"]), CamHandler)
        print("-- Server started on "+Receiver._confs["Cameras"][0]["Stream"]+":"+str(Receiver._confs["Cameras"][0]["StreamPort"]))
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
        Receiver.tassSocket.close()
        
if __name__ == '__main__':
    main()