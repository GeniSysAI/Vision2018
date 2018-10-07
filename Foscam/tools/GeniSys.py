############################################################################################
#
# The MIT License (MIT)
# 
# GeniSys Foscam FI8916P V3 TASS Device GeniSys Helpers
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
# Title:         GeniSys Foscam FI8916P V3 TASS Device GeniSys Helpers
# Description:   iotJumpWay helper functions for GeniSys GeniSys Foscam FI8916P V3 TASS Device.
# Configuration: required/confs.json
# Last Modified: 2018-09-29
#
############################################################################################

import os, sys, time, requests, json, hashlib, hmac, base64, urllib

import JumpWayMQTT.Device as jumpWayDevice

from datetime      import datetime
from requests.auth import HTTPBasicAuth

from tools.Helpers import Helpers

class GeniSys():
    
    def __init__(self):

        ###############################################################
        #
        # Sets up all default requirements and placeholders 
        # needed for the NLU engine to run. 
        #
        # - Helpers: Useful global functions
        # - Logging: Logging class
        #
        ###############################################################
        
        self.Helpers = Helpers()
        self._confs  = self.Helpers.loadConfigs()
        self.LogFile = self.Helpers.setLogFile(self._confs["aiCore"]["Logs"]+"GeniSys/")

    def createHashMac(self, secret, data):

        ###############################################################
        #
        # Creates a hash
        #
        ###############################################################

        return hmac.new(bytearray(secret.encode("utf-8")), data.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    
    def restApiCall(self, apiUrl, data, headers):
        
        self.Helpers.logMessage(
            self.LogFile,
            "GENISYS",
            "INFO",
            "Sending GeniSys REST Request")
            
        response = requests.post(
                        apiUrl, 
                        data=json.dumps(data), 
                        headers=headers, 
                        auth=HTTPBasicAuth(
                                    str(self._confs["iotJumpWay"]["App"]), 
                                    self.createHashMac(
                                                self._confs["iotJumpWay"]["API"]["key"],
                                                self._confs["iotJumpWay"]["API"]["key"])))
                               
        output = json.loads(response.text)
        self.Helpers.logMessage(
            self.LogFile,
            "GENISYS",
            "INFO",
            "GeniSys REST Response Received: " + str(output))
    
        return output

    def getHuman(self, name): 
        
        return self.restApiCall(
                    self._confs["GeniSys"]["RestEndpoint"], 
                    {
                        "Call":"getHumanID",
                        "Data": {
                            "name":name
                        }
                    }, 
                    {
                        'content-type': 'application/json'
                    })

    def trackHuman(self, uid, lid, fid, zid, did): 
        
         return self.restApiCall(
                    self._confs["GeniSys"]["RestEndpoint"], 
                    {
                        "Call":"trackHuman",
                        "Data": {
                            "uid":uid,
                            "lid":lid,
                            "fid":fid,
                            "zid":zid,
                            "did":did
                        }
                    }, 
                    {
                        'content-type': 'application/json'
                    })