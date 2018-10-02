############################################################################################
#
# The MIT License (MIT)
# 
# GeniSys TASS OpenCV Helpers
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
# Title:         GeniSys TASS OpenCV Helpers
# Description:   OpenCV helpers functions for GeniSys TASS devices and applications.
# Configuration: required/confs.json
# Last Modified: 2018-10-02
#
############################################################################################

import os, json, cv2
import numpy as np
from datetime import datetime

class OpenCV():

    def __init__(self):

		###############################################################
		#
		# Nothing to do
		#
		###############################################################
        pass

    def saveImage(self,networkPath,frame):

        ###############################################################
        #
        # Saves an image
        #
        ###############################################################

        timeDirectory =  networkPath + "data/captures/"+datetime.now().strftime('%Y-%m-%d')+'/'+datetime.now().strftime('%H')

        if not os.path.exists(timeDirectory):
            os.makedirs(timeDirectory)

        currentImage=timeDirectory+'/'+datetime.now().strftime('%M-%S')+'.jpg'
        print(currentImage)
        print("")

        cv2.imwrite(currentImage, frame)

        return currentImage

    def loadImage(self, imgID):

        ###############################################################
        #
        # Loads an image
        #
        ###############################################################
    
        imgLoadStart  = time.time()

        img = cv2.imread("data/captured/"+str(imgID)+'.png')

        imgLoadEnd    = (imgLoadStart - time.time())
        
        self.Helpers.logMessage(
            self.LogFile,
            "TASS",
            "INFO",
            "Image Loaded Into TASS In " + str(imgLoadTime) + " Seconds")

        return img

    def rect_to_bb(self, rect):

        ###############################################################
        #
        # Take a bounding predicted by dlib and convert it to the 
        # format (x, y, w, h) as we would normally do with OpenCV
        #
        ###############################################################
        
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        
        return (x, y, w, h)

    def shape_to_np(self, shape, dtype="int"):

        ###############################################################
        #
        # Initialize the list of (x, y)-coordinates
        #
        ###############################################################
        
        coords = np.zeros((68, 2), dtype=dtype)
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
            
        return coords

    def whiten(self, source_image):

        ###############################################################
        #
        # Creates a whitened image
        #
        ###############################################################

        source_mean = np.mean(source_image)
        source_standard_deviation = np.std(source_image)
        std_adjusted = np.maximum(source_standard_deviation, 1.0 / np.sqrt(source_image.size))
        whitened_image = np.multiply(np.subtract(source_image, source_mean), 1 / std_adjusted)
        return whitened_image

    def preprocess(self, src):

        ###############################################################
        #
        # Scale an image
        #
        ###############################################################
        
        NETWORK_WIDTH = 160
        NETWORK_HEIGHT = 160
        preprocessed_image = cv2.resize(src, (NETWORK_WIDTH, NETWORK_HEIGHT))

        #convert to RGB
        preprocessed_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB)

        #whiten
        preprocessed_image = self.whiten(preprocessed_image)

        # return the preprocessed image
        return preprocessed_image