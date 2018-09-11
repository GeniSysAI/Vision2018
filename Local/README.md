# GeniSys Local TASS Engine
[![GeniSys Local TASS Engine](../images/GeniSys.png)](https://github.com/GeniSysAI/NLU)

[![UPCOMING RELEASE](https://img.shields.io/badge/UPCOMING%20RELEASE-0.0.1-blue.svg)](https://github.com/GeniSysAI/NLU/tree/0.0.1)

# About GeniSys AI

GeniSys AI is an open source Artificial Intelligence Assistant Network using Computer Vision, Natural Linguistics and the Internet of Things. GeniSys uses a system based on [TASS A.I](https://github.com/TASS-AI/TASS-Facenet "TASS A.I") for [vision](https://github.com/GeniSysAI/Vision "vision"), an [NLU engine](https://github.com/GeniSysAI/NLU "NLU engine") for natural language understanding, in browser speech synthesis and speech recognition for speech and hearing, all homed on a dedicated Linux server in your home and managed via a secure UI.

# About GeniSys Local TASS Engine

GeniSys AI is an open source Artificial Intelligence Assistant Network using Computer Vision, Natural Linguistics and the Internet of Things. GeniSys uses a system based on [TASS A.I](https://github.com/TASS-AI/TASS-Facenet "TASS A.I") for [vision](https://github.com/GeniSysAI/Vision "vision"), an [NLU engine](https://github.com/GeniSysAI/NLU "NLU engine") for natural language understanding, in browser speech synthesis and speech recognition for speech and hearing, all homed on a dedicated Linux server in your home and managed via a secure UI.

# About GeniSys TASS Engine

The **GeniSys TASS Engine** uses Siamese Neural Networks and Triplet Loss to classify known and unknown faces, basically this means it calculates the distance between an image it is presented and a folder of known faces. The local engine is homed on your GeniSys server and connects to your server webcam, this is one of the reasons why the UI is designed to be used on the local network, as if you connect from any where other than in front of the local camera then GeniSys will not be able to see you.

## How It Works

The main program runs in the background and connects to the camera stream and also to the iotJumpWay, it processes each frame alerting the iotJumpWay of the classification and then updates the frame and streams the modified frame to a stream allowing other devices and applications to connect to the feed. You are able to set rules on the iotJumpWay allowing autonomous communication with other IoT devices and applications in the event of identifications or intruders.

When using the GeniSys Local TASS Engine as it is designed to be used, you will be able to ask your AI who you are and they will be able to identify you, in the background logic helps keep track of where known users or intruders are etc.

The project uses an **UP2 (Up Squared)** (A regular Linux desktop or Raspberry 3 and above will also work) the **Intel Movidius** for inference and the [iotJumpWay](https://www.iotjumpway.tech "iotJumpWay") for IoT connectivity. 

## Avoiding The Open Set Recognition Issue

With previous versions of TASS built using Tensorflow, **TASS Movidius Inception V3 Classifier**, the model had issues with the [Openset Recognition Issue](https://www.wjscheirer.com/projects/openset-recognition/ "Openset Recognition Issue"). **TASS Facenet Classifier** uses a directory of known images and when presented with a new image, will loop through each image basically measuring the distance between the known image and the presented image, it seems to overcome the issue so far in small testing environments of one or more people. In a large scenario this method will not be scalable, but is fine for small home projects etc. 

Combining **TASS Movidius Inception V3 Classifier** (prone to open set recognition issues) and **TASS Facenet Classifier** allows us to catch false positives and verify positive classifications using the name/ID of that prediction to quickly index into the images and make a single calculation to determine if Inception classified the person correctly or not using Facenet and making the project more scalable. The latest Inception version of the classifier will be uploaded to this repository soon.

# What Will We Do?

1. Install the [Intel® NCSDK](https://github.com/movidius/ncsdk "Intel® NCSDK") on a [GeniSys Server](https://github.com/GeniSysAI/Server "GeniSys Server").
2. Clone & set up the repo.
3. Install and download all requirements.
4. Prepare your known and testing faces datasets.
5. Test the **TASS Facenet Classifier** on the testing dataset.
6. Run **TASS Facenet Classifier** on a live webcam
7. Install the [Intel® NCSDK API](https://github.com/movidius/ncsdk "Intel® NCSDK API") on a Raspberry Pi 3 / UP 2.
8. Upload and run the program on an **UP2** or **Raspberry Pi 3**

# Python Versions

- Tested in Python 3

# Software Requirements

- [Intel® NCSDK](https://github.com/movidius/ncsdk "Intel® NCSDK")
- [Tensorflow 1.4.0](https://www.tensorflow.org/install "Tensorflow 1.4.0")
- [iotJumpWay MQTT Client](https://github.com/iotJumpway/JumpWayMQTT "iotJumpWay MQTT Client")
- [GrovePi](https://github.com/DexterInd/GrovePi "GrovePi") (OPTIONAL)

# Hardware Requirements

- 1 x [Intel® Movidius](https://www.movidius.com/ "Intel® Movidius")
- 1 x [GeniSys Server](https://github.com/GeniSysAI/Server "GeniSys Server")

# Install NCSDK On GeniSys Server

![Intel® Movidius](../images/movidius.jpg)

The first thing you will need to do is to install the **NCSDK** on your development device.

```
 $ mkdir -p ~/workspace
 $ cd ~/workspace
 $ git clone https://github.com/movidius/ncsdk.git
 $ cd ~/workspace/ncsdk
 $ make install
```

Next plug your Movidius into your device and issue the following commands:

```
 $ cd ~/workspace/ncsdk
 $ make examples
```

# Cloning The Repo

You will need to clone this repository to a location on your GeniSys Server. Navigate to the /home/USERNAME/Core/Vision directory (create it if it doesn't exist) and issue the following commands.

    $ git clone https://github.com/GeniSysAI/Vision.git

Once you have the repo, you will need to find the files in this folder located in the [Local](https://github.com/GeniSysAI/Vision/tree/master/Local "Local") directory, this is the project root for the GeniSys Local TASS Engine.

# Setup

Now you need to setup the software required for the classifier to run. The setup.sh script is a shell script that you can run on your GeniSys Server. 

Make sure you have installed the **NCSDK** on your developement machine, the following command assumes you are located in the [Local](https://github.com/GeniSysAI/Vision/tree/master/Local "Local") directory.

The setup.sh file is an executable shell script that will do the following:

- Install the required packages named in **requirements.txt**
- Downloads the pretrained Facenet model (**davidsandberg/facenet**)
- Downloads the pretrained **Inception V3** model
- Converts the **Facenet** model to a model that is compatible with the **Intel® Movidius**

To execute the script, enter the following command:

```
 $ sh setup.sh
```

If you have problems running the above program and have errors try run the following command before executing the shell script. You may be getting errors due to the shell script having been edited on Windows, the following command will clean the setup file.

```
 $ sed -i 's/\r//' setup.sh
 $ sh setup.sh
```

# iotJumpWay Device Connection Credentials & Settings

Setup an iotJumpWay Location Device for IDC Classifier, ensuring you set up a camera node, as you will need the ID of the camera for the project to work. Once your create your device add the location ID and Zone ID to the **IoTJumpWay** details in the confs file located at **required/confs.json**, also add the device ID and device name exactly, add the MQTT credentials to the **IoTJumpWayMQTT** .

You will need to edit your device and add the rules that will allow it to communicate autonomously with the other devices and applications on the network, but for now, these are the only steps that need doing at this point.

Follow the [iotJumpWay Dev Program Location Device Doc](https://www.iotjumpway.tech/developers/getting-started-devices "iotJumpWay Dev Program Location Device Doc") to set up your devices.

```
{
    "IoTJumpWay": {
        "Location": 0,
        "Zone": 0,
        "Device": 0,
        "DeviceName" : "",
        "App": 0,
        "AppName": ""
    },
    "Actuators": {},
    "Cameras": [
        {
            "ID": 0,
            "URL": 0,
            "Name": "",
            "Stream": "",
            "StreamPort": 8080
        }
    ],
    "Sensors": {},
	"IoTJumpWayMQTT": {
        "MQTTUsername": "",
        "MQTTPassword": ""
    },
    "ClassifierSettings":{
        "NetworkPath":"",
        "Graph":"model/tass.graph",
        "Dlib":"model/dlib/shape_predictor_68_face_landmarks.dat",
        "dataset_dir":"model/train/",
        "TestingPath":"data/testing/",
        "ValidPath":"data/known/",
        "Threshold": 1.20
    }
}
```

# Preparing Dataset

You need to set up two very small datasets. As we are using a pretrained Facenet model there is no training to do in this tutorial and we only need one image per known person. You should see the **known** and **testing** folders in the **data** directory, this is where you will store 1 image of each person you want to be identified by the network, and also a testing dataset that can include either known or unknown faces for testing. When you store the known data, you should name each image with the name you want them to be identified as in the system, in my testing I used images of me and two other random people, the 1 image used to represent myself in the known folder was named Adam .

# Run GeniSys Local TASS Engine

Make sure you have set up you GeniSys Server and NLU Engine and use the  [NGINX configuration](https://github.com/GeniSysAI/Server/blob/master/etc/nginx/sites-available/default "NGINX configuration") provided. To set up your server you can follow [GeniSys Server](https://github.com/GeniSysAI/Server/ "GeniSys Server") and to set up your NLU engine you can follow [GeniSys NLU](https://github.com/GeniSysAI/Server/ "GeniSys NLU").

Now comes the good part, realtime facial recognition and identification. 

![TASS Facenet Classifier](../images/capture.jpg)

**LocalStreamer.py** should connect to the local webcam on your GeniSys Server, process the frames and send them to a socket that is started by this same program. Be sure to edit the **ID** and **Name** values of the **Cameras** section of **required/confs.json** section using the details provided when setting up the configs.

```
"Cameras": [
{
    "ID": 0,
    "URL": 0,
    "RTSPuser": "",
    "RTSPpass": "",
    "RTSPip": "",
    "RTSPport": "",
    "RTSPendpoint": "",
    "Name": "",
    "Stream": "192.168.1.200",
    "StreamAccess": "",
    "StreamPort": 8080,
    "SocketPort": 8181 
}
```

Add the URL of the IP of your device ie: http://192.168.1.200 to the **Stream** value and you can change **StreamPort** & **SocketPort** to whatever you want. These two fields will determine the port that streams your camera to the network and the port that streams your camera via sockets, using the previous IP (Stream) and the StreamPort as 8080 and SocketPort as 8181 the address to access your feed would be **http://192.168.1.200:8080/i.html** or **http://192.168.1.200:8080/i.mjpg**, the system will internally take care of the sockets providing you set up your configuration correctly. 

**LocalReceiver.py** connects to the socket stream and streams it as an mjpg. 

If you used the provided [NGINX configuration](https://github.com/GeniSysAI/Server/blob/master/etc/nginx/sites-available/default "NGINX configuration") of the [GeniSys Server](https://github.com/GeniSysAI/Server/ "GeniSys Server") guide:

```
server_name Subdomain.Domain.TLD;

location ~ ^/tasslocal/ {
    proxy_pass http://###.###.#.###:8080/$uri$is_args$args;
}
```

you will now be able to access your feed by visiting **http://www.YourDomain.com/tasslocal/i.html** or **http://www.YourDomain.com/tasslocal/i.mjpg**.

The program uses a **dlib** model to recognize faces in the frames / mark the facial points on the frame, and **Facenet** to determine whether they are a known person or not. Below are the outputs around the time that the above photo was taken. You will see that the program publishes to the **TASS** channel of the iotJumpWay, this is the name for the channel that handles device to device communication for TASS devices via rules that you can set up in the iotJumpWay console.

```
2018-09-11 15:41:09|TASS|INFO: Calculated Distance 1.000346302986145
2018-09-11 15:41:09|TASS|OK: TASS Identified Adam In 0.2891969680786133 Seconds With Confidence Of 1.000346302986145
-- Published: 8174
-- Published to Device TASS Channel
```

# Acknowledgements

- Uses code from Intel® **movidius/ncsdk** ([movidius/ncsdk Github](https://github.com/movidius/ncsdk "movidius/ncsdk Github"))<br />
- Uses code from Intel® **davidsandberg/facenet** ([davidsandberg/facenet Github](https://github.com/davidsandberg/facenet "davidsandberg/facenet"))

# Contributing
Please read [CONTRIBUTING.md](https://github.com/GeniSysAI/NLU/blob/master/CONTRIBUTING.md "CONTRIBUTING.md") for details on our code of conduct, and the process for submitting pull requests to us.

# Versioning
We use SemVer for versioning. For the versions available, see the tags on this repository and [RELEASES.md](https://github.com/GeniSysAI/NLU/blob/master/RELEASES.md "RELEASES.md").

# License
This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/GeniSysAI/NLU/blob/master/LICENSE "LICENSE") file for details.

# Bugs/Issues
We use the [repo issues](https://github.com/GeniSysAI/NLU/issues "repo issues") to track bugs and general requests related to using this project. 

# Author
[![Adam Milton-Barker: BigFinte IoT Network Engineer & Intel® Software Innovator (IoT, AI, VR)](../images/Adam-Milton-Barker.jpg)](https://github.com/AdamMiltonBarker)



