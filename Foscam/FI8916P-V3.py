############################################################################################
#
# The MIT License (MIT)
# 
# GeniSys Foscam FI8916P V3 TASS Device
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
# Title:         GeniSys Foscam FI8916P V3 TASS Device
# Description:   Connects to the stream from a Foscam FI8916P V3, processes and streams the 
#                modified stream.
# Configuration: required/confs.json
# Last Modified: 2018-10-02
#
# Example Usage:
#
#   $ python3.5 FI8916P-V3.py
#
############################################################################################

import os, sys, time, zmq, cv2, dlib, imutils, base64

import JumpWayMQTT.Device as JWDevice

from datetime          import datetime
from skimage.transform import resize
from imutils           import face_utils
from flask             import Flask, request

from tools.Helpers     import Helpers 
from tools.JumpWay     import JumpWay
from tools.MySql       import MySql
from tools.OpenCV      import OpenCV
from tools.Facenet     import Facenet

app = Flask(__name__)

class TASS():
    
    def __init__(self):

        ###############################################################
        #
        # Sets up all default requirements and placeholders 
        # needed for the NLU engine to run. 
        #
        ###############################################################

        self.Helpers     = Helpers()
        self._confs      = self.Helpers.loadConfigs()
        self.LogFile     = self.Helpers.setLogFile(self._confs["aiCore"]["Logs"]+"/Foscam")  
        
        self.MySql       = MySql()
        
        self.OpenCV      = OpenCV()
        self.OCVframe    = None
        self.font        = cv2.FONT_HERSHEY_SIMPLEX
        self.fontColor   = (255,255,255)
        self.fontScale   = 1
        self.lineType    = 1
        self.identified  = 0

        self.Facenet     = Facenet()

        self.movidius, self.devices, self.device = self.Facenet.CheckDevices()
        self.fgraph,  self.fgraphfile            = self.Facenet.loadGraph("Facenet", self.movidius)

        self.validDir    = self._confs["Classifier"]["NetworkPath"] + self._confs["Classifier"]["ValidPath"]
        self.testingDir  = self._confs["Classifier"]["NetworkPath"] + self._confs["Classifier"]["TestingPath"]
        
        self.detector    = dlib.get_frontal_face_detector()
        self.predictor   = dlib.shape_predictor(self._confs["Classifier"]["Dlib"])

        self.connectToCamera()

        self.tassSocket  = None
        self.configureSocket()

        self.JumpWay    = JumpWay()
        self.JumpWayCL  = self.JumpWay.startMQTT()
        
        self.Helpers.logMessage(
                            self.LogFile,
                            "TASS",
                            "INFO",
                            "TASS Ready")
        
    def connectToCamera(self):

        ###############################################################
        #
        # Connects to the Foscam device using the configs in 
        # required/confs.json
        #
        ###############################################################
        
        self.OCVframe = cv2.VideoCapture("rtsp://"+self._confs["Cameras"][0]["RTSPuser"]+":"+self._confs["Cameras"][0]["RTSPpass"]+"@"+self._confs["Cameras"][0]["RTSPip"]+":"+self._confs["Cameras"][0]["RTSPport"]+"/"+self._confs["Cameras"][0]["RTSPendpoint"])
        
        self.Helpers.logMessage(
                            self.LogFile,
                            "TASS",
                            "INFO",
                            "Connected To Camera")
        
    def configureSocket(self):

        ###############################################################
        #
        # Configures the socket we will stream the frames to
        #
        ###############################################################

        self.tassSocket = zmq.Context().socket(zmq.PUB)
        self.tassSocket.connect("tcp://"+self._confs["Socket"]["host"]+":"+str(self._confs["Socket"]["port"]))

        self.Helpers.logMessage(
                            self.LogFile,
                            "TASS",
                            "INFO",
                            "Connected To Socket")
        
TASS = TASS()

###############################################################
#
# The meat of the program, reads the frames from the Foscam 
# stream, processes them and streams the modified stream. On 
# identification or detection of intruder, the program will 
# send a message through to the iotJumpWay.
#
###############################################################

while True:
    try:

        _, frame = TASS.OCVframe.read()
        frame    = cv2.resize(frame, (640, 480)) 
        rawFrame = frame.copy()

        gray     = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects    = TASS.detector(gray, 0)
            
        for (i, rect) in enumerate(rects):
            
            shape = face_utils.shape_to_np(
                TASS.predictor(
                    gray,
                    rect))
            
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            
            cv2.rectangle(
                frame, 
                (x, y), 
                (x + w, y + h), 
                (0, 255, 0), 
                2)
                
            for (x, y) in shape:
                
                cv2.circle(
                    frame, 
                    (x, y), 
                    1, 
                    (0, 255, 0), 
                    -1)
                    
            currentFace = rawFrame[
                max(0, rect.top()-100): min(rect.bottom()+100, 480),
                max(0, rect.left()-100): min(rect.right()+100, 640)]

            if currentFace is None:
                continue 
            
            for valid in os.listdir(TASS.validDir):
                
                if valid.endswith('.jpg') or valid.endswith('.jpeg') or valid.endswith('.png') or valid.endswith('.gif'):
                    
                    inferStart = time.time()
                    
                    known, confidence = TASS.Facenet.match(
                        TASS.Facenet.infer(
                                        cv2.imread(TASS.validDir+valid), 
                                        TASS.fgraph),
                                        TASS.Facenet.infer(
                                                        cv2.flip(currentFace, 1), 
                                                        TASS.fgraph))

                    user = valid.rsplit(".", 1)[0].title()
                    inferEnd = (inferStart - time.time())
                    
                    if (known==True):
                        
                        TASS.identified = TASS.identified + 1

                        TASS.MySql.trackHuman(
                                        TASS.MySql.getHuman(user), 
                                        TASS._confs["iotJumpWay"]["Location"], 
                                        0, 
                                        TASS._confs["iotJumpWay"]["Zone"], 
                                        TASS._confs["iotJumpWay"]["Device"])
		
                        TASS.Logging.logMessage(
                                            TASS.LogFile,
                                            "TASS",
                                            "INFO",
                                            "TASS Identified " + user + " In " + str(inferEnd) + " Seconds With Confidence Of " + str(confidence))

                        TASS.JumpWayCL.publishToDeviceChannel(
                                                            "TASS",
                                                            {
                                                                "WarningType":"SECURITY",
                                                                "WarningOrigin": TASS._confs["Cameras"][1]["ID"],
                                                                "WarningValue": "RECOGNISED",
                                                                "WarningMessage": "RECOGNISED"
                                                            })

                        cv2.putText(
                            frame, 
                            user, 
                            (x,y), 
                            TASS.font, 
                            TASS.fontScale,
                            TASS.fontColor,
                            TASS.lineType)
                        break

                    else:
		
                        TASS.Logging.logMessage(
                                            TASS.LogFile,
                                            "TASS",
                                            "INFO",
                                            "TASS Identified Unknown Human In " + str(inferEnd) + " Seconds With Confidence Of " + str(confidence))

                        TASS.JumpWayCL.publishToDeviceChannel(
                                                            "TASS",
                                                            {
                                                                "WarningType": "SECURITY",
                                                                "WarningOrigin": TASS._confs["Cameras"][1]["ID"],
                                                                "WarningValue": "INTRUDER",
                                                                "WarningMessage": "INTRUDER"
                                                            })

                        cv2.putText(
                                frame,
                                "Unknown " + str(confidence), 
                                (x,y), 
                                TASS.font, 
                                TASS.fontScale,
                                TASS.fontColor,
                                TASS.lineType)
 
        encoded, buffer = cv2.imencode('.jpg', frame)
        TASS.tassSocket.send(base64.b64encode(buffer))

    except KeyboardInterrupt:
        TASS.OCVframe.release()
        cv2.destroyAllWindows()
        break