############################################################################################
#
# The MIT License (MIT)
# 
# TASS Facent Helpers
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
# Title:         TASS Facent Helpers
# Description:   Facenet helper functions for TASS.
# Configuration: required/confs.json
# Last Modified: 2018-08-09
#
############################################################################################

import os, json, cv2
import numpy as np
from datetime import datetime
from tools.OpenCV import OpenCV
from tools.Logging import Logging

class Facenet():
    
    def __init__(self):
        
        self.Logging = Logging()
        self.OpenCV = OpenCV()
        
    def infer(self, image_to_classify, facenet_graph):
        
        resized_image = self.preprocess(image_to_classify)
        facenet_graph.LoadTensor(resized_image.astype(np.float16), None)
        output, userobj = facenet_graph.GetResult()

        return output

    def match(self, face1_output, face2_output):

        if (len(face1_output) != len(face2_output)):
            self.Logging.logMessage(
                "TASS",
                "ERROR",
                "Distance Missmatch"
            )
            return False

        total_diff = 0
        for output_index in range(0, len(face1_output)):

            this_diff = np.square(face1_output[output_index] - face2_output[output_index])
            total_diff += this_diff

        self.Logging.logMessage(
            "TASS",
            "INFO",
            "Calculated Distance " + str(total_diff)
        )

        if (total_diff < 1.3):
            return True, total_diff
        else:
            return False, total_diff

    def preprocess(self, src):
        
        NETWORK_WIDTH = 160
        NETWORK_HEIGHT = 160
        preprocessed_image = cv2.resize(src, (NETWORK_WIDTH, NETWORK_HEIGHT))
        preprocessed_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB)
        preprocessed_image = self.OpenCV.whiten(preprocessed_image)
        
        return preprocessed_image