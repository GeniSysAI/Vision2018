# GeniSys TASS Devices & Applications
[![GeniSys TASS Devices & Applications](images//GeniSys.png)](https://github.com/GeniSysAI/Vision)

[![UPCOMING RELEASE](https://img.shields.io/badge/UPCOMING%20RELEASE-0.0.1-blue.svg)](https://github.com/GeniSysAI/Vision/tree/0.0.1)

# About GeniSys AI

GeniSys AI is an open source Artificial Intelligence Assistant Network using Computer Vision, Natural Linguistics and the Internet of Things. GeniSys uses a system based on [TASS A.I](https://github.com/TASS-AI/TASS-Facenet "TASS A.I") for [vision](https://github.com/GeniSysAI/Vision "vision"), an [NLU engine](https://github.com/GeniSysAI/NLU "NLU engine") for natural language understanding, in browser speech synthesis and speech recognition for speech and hearing, all homed on a dedicated Linux server in your home and managed via a secure UI.

# About GeniSys TASS Devices & Applications

The **GeniSys TASS Devices & Applications** uses Siamese Neural Networks and Triplet Loss to classify known and unknown faces, basically this calculates the distance between an image it is presented and a folder of images of known faces. The local engine is homed on your GeniSys server and connects to your server webcam, this is one of the reasons why the UI is designed to be used on the local network, as if you connect from any where other than in front of the local camera then GeniSys will not be able to see you.

# Siamese Neural Networks & Triplet Loss
 
As mentioned above, GeniSys TASS Devices & Applications uses Siamese Neural Networks & Triplet Loss, but what exactly are they?

Siamese Neural Networks basically are made up of 2 neural networks that are exactly the same, hence the name Siamese Neural Networks. Given two images, we use the identical networks to calculate the similarity between the two images. Basically Siamese Neural Networks learn how to differentiate between objects, or in this case, faces. 

Triplet Loss reduces the difference between an anchor (an image) and a positive sample from the same class, and increases the difference between the ancher and a negative sample from an opposite class. Basically this means that 2 images with the same class (in this case, the same person) will have a smaller distance than two images from different classes (or 2 different people). 

# How It Works

There are currently three different versions of GeniSys TASS devices: local, Foscam and Realsense (Foscam and Realsense are in development). Each device connects to a stream of one kind or another, processes the frames and streams the modified frames. 

- [Local](https://github.com/GeniSysAI/Vision/tree/master/Local "Local")
- [Foscam](https://github.com/GeniSysAI/Vision/tree/master/Foscam "Foscam")
- [RealSense](https://github.com/GeniSysAI/Vision/tree/master/RealSense "RealSense")

# Acknowledgements

- Uses code from Intel® **movidius/ncsdk** ([movidius/ncsdk Github](https://github.com/movidius/ncsdk "movidius/ncsdk Github"))
- Uses code from Intel® **davidsandberg/facenet** ([davidsandberg/facenet Github](https://github.com/davidsandberg/facenet "davidsandberg/facenet"))

# Useful Links

Links to related articles that helped at various stages of the project for research / code examples:

- [Open Set Recognition Issue](https://www.wjscheirer.com/projects/openset-recognition/ "Open Set Recognition Issue")
- [PyImageSearch](https://www.pyimagesearch.com/ "PyImageSearch")

# Contributing
Please read [CONTRIBUTING.md](https://github.com/GeniSysAI/Vision/blob/master/CONTRIBUTING.md "CONTRIBUTING.md") for details on our code of conduct, and the process for submitting pull requests to us.

# Versioning
We use SemVer for versioning. For the versions available, see [GeniSysAI/Vision/releases](https://github.com/GeniSysAI/Vision/releases "GeniSysAI/Vision/releases").

# License
This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/GeniSysAI/Vision/blob/master/LICENSE "LICENSE") file for details.

# Bugs/Issues
We use the [repo issues](https://github.com/GeniSysAI/Vision/issues "repo issues") to track bugs and general requests related to using this project. 

# Author
[![Adam Milton-Barker: BigFinte IoT Network Engineer & Intel® Software Innovator (IoT, AI, VR)](images/Adam-Milton-Barker.jpg)](https://github.com/AdamMiltonBarker)



