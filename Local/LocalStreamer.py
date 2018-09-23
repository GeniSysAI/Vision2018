############################################################################################
#
# The MIT License (MIT)
# 
# TASS Local Streamer
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
# Title:         TASS Local Streamer
# Description:   Connects to the local server camera, processes and streams the modified stream.
# Configuration: required/confs.json
# Last Modified: 2018-09-09
#
# Example Usage:
#
#   $ python3.5 Local.py
#
############################################################################################

import os, sys, time, getopt, zmq, cv2, dlib, imutils, jsonpickle, cv2, base64

import numpy              as np
import JumpWayMQTT.Device as JWDevice

from datetime          import datetime
from skimage.transform import resize
from imutils           import face_utils
from mvnc              import mvncapi as mvnc
from flask             import Flask, request, Response

from tools.Helpers     import Helpers
from tools.Logging     import Logging
from tools.OpenCV      import OpenCV
from tools.Facenet     import Facenet
from tools.MySql       import MySql

app = Flask(__name__)

class TASS():
    
    def __init__(self):
        
        
        self.OCVframe   = None
        self.tassSocket = None
        self.movidius   = None
        self.fgraph     = None
        self.fgraphfile = None

        self.Helpers    = Helpers()
        self.Logging    = Logging()
        self.OpenCV     = OpenCV()
        self.MySql      = MySql()

        self._confs     = self.Helpers.loadConfigs()
        self.LogFile    = self.Logging.setLogFile(self._confs["AI"]["Logs"]+"/local")   

        self.Facenet    = Facenet(self._confs)

        self.font       = cv2.FONT_HERSHEY_SIMPLEX
        self.fontColor  = (255,255,255)
        self.fontScale  = 1
        self.lineType   = 1
        self.identified = 0
        
        self.Logging.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "TASS Initiating")
        
        self.Logging.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "TASS Modules Ready")
        
        self.Logging.logMessage(
			self.LogFile,
            "TASS",
            "INFO",
            "TASS Configs Ready")

        self.startMQTT()

        self.validDir    = self._confs["ClassifierSettings"]["NetworkPath"] + self._confs["ClassifierSettings"]["ValidPath"]
        self.testingDir  = self._confs["ClassifierSettings"]["NetworkPath"] + self._confs["ClassifierSettings"]["TestingPath"]

        self.devices, self.device = self.CheckDevices()
        self.loadRequirements("Facenet")
        self.connectToCamera()
        self.configureSocket()
        
        self.detector   = dlib.get_frontal_face_detector()
        self.predictor  = dlib.shape_predictor(self._confs["ClassifierSettings"]["Dlib"])
        self.validDir   = self._confs["ClassifierSettings"]["NetworkPath"] + self._confs["ClassifierSettings"]["ValidPath"]
        self.testingDir = self._confs["ClassifierSettings"]["NetworkPath"] + self._confs["ClassifierSettings"]["TestingPath"]
        
        self.Logging.logMessage(
			self.LogFile,
            "TASS",
            "INFO",
            "TASS Ready")
        
    def startMQTT(self):
        
        try:
            
            self.JumpWayCL = JWDevice.DeviceConnection({
                "locationID": self._confs["IoTJumpWay"]["Location"],
                "zoneID": self._confs["IoTJumpWay"]["Zone"],
                "deviceId": self._confs["IoTJumpWay"]["Device"],
                "deviceName": self._confs["IoTJumpWay"]["DeviceName"],
                "username": self._confs["IoTJumpWayMQTT"]["MQTTUsername"],
                "password": self._confs["IoTJumpWayMQTT"]["MQTTPassword"]})
                
        except Exception as e:
            print(str(e))
            sys.exit()
            
        self.JumpWayCL.connectToDevice()
        
        self.Logging.logMessage(
			self.LogFile,
            "TASS",
            "INFO",
            "iotJumpWay Ready")

    def CheckDevices(self):

        #mvnc.SetGlobalOption(mvnc.GlobalOption.LOGLEVEL, 2)
        devices = mvnc.EnumerateDevices()

        if len(devices) == 0:
            
            self.Logging.logMessage(
                self.LogFile,
                "TASS",
                "INFO",
                "No Movidius Devices")
                
            self.Logging.logMessage(
                self.LogFile,
                "TASS",
                "INFO",
                "TASS Exiting")

            quit()

        self.movidius = mvnc.Device(devices[0])
        self.movidius.OpenDevice()
        
        self.Logging.logMessage(
			self.LogFile,
            "TASS",
            "INFO",
            "Connected To Movidius")

        return devices, devices[0]

    def loadRequirements(self, graphID):

        if graphID == "Facenet":

            with open(self._confs["ClassifierSettings"]["NetworkPath"] + self._confs["ClassifierSettings"]["Graph"], mode='rb') as f:
                self.fgraphfile = f.read()

            self.allocateGraph(
                self.fgraphfile,
                "Facenet")
                
            self.Logging.logMessage(
                self.LogFile,
                "TASS",
                "INFO",
                "Loaded TASS Requirements")

    def allocateGraph(self, graphfile, graphID):

        if graphID == "Facenet":

            self.fgraph = self.movidius.AllocateGraph(graphfile)
            
            self.Logging.logMessage(
                self.LogFile,
                "TASS",
                "INFO",
                "TASS Facenet Graph Allocated")
        
    def connectToCamera(self):
        
        self.OCVframe = cv2.VideoCapture(0)
        
        self.Logging.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "Connected To Camera")
        
    def configureSocket(self):

        self.tassSocket = zmq.Context().socket(zmq.PUB)
        self.tassSocket.connect('tcp://localhost:8956')
        
    def saveImage(self, nump):
    
        imgSaveStart  = time.time()

        cv2.imwrite(
            "data/captured/"+str(imgSaveStart)+'.png',
            cv2.imdecode(nump, cv2.IMREAD_UNCHANGED))

        imgSaveEnd    = (imgSaveStart - time.time())
        
        self.Logging.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "TASS Saved Image In " + str(imgSaveEnd) + " Seconds")

        return imgSaveStart

    def loadImage(self, imgID):
    
        imgLoadStart  = time.time()

        img = cv2.imread("data/captured/"+str(imgID)+'.png')

        imgLoadEnd    = (imgLoadStart - time.time())
        
        self.Logging.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "Image Loaded Into TASS In " + str(imgLoadTime) + " Seconds")

        return img
        
TASS = TASS()

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
                            TASS._confs["IoTJumpWay"]["Location"], 
                            0, 
                            TASS._confs["IoTJumpWay"]["Zone"], 
                            TASS._confs["IoTJumpWay"]["Device"], 
                             )
		
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
                            }
                        )

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
                            }
                        )

                        cv2.putText(
                            frame,
                            "Unknown " + str(confidence), 
                            (x,y), 
                            TASS.font, 
                            TASS.fontScale,
                            TASS.fontColor,
                            TASS.lineType)

                    cv2.imwrite("testProcessed.jpg", frame)
                    cv2.imwrite("testProcessedFull.jpg", currentFace)
 
        encoded, buffer = cv2.imencode('.jpg', frame)
        TASS.tassSocket.send(base64.b64encode(buffer))

    except KeyboardInterrupt:
        TASS.OCVframe.release()
        cv2.destroyAllWindows()
        break