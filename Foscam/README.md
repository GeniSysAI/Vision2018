# GeniSys Foscam TASS Device
[![RealSense TASS Device](../images/GeniSys.png)](https://github.com/GeniSysAI/NLU)

[![UPCOMING RELEASE](https://img.shields.io/badge/UPCOMING%20RELEASE-0.0.1-blue.svg)](https://github.com/GeniSysAI/NLU/tree/0.0.1)

# About GeniSys Foscam TASS Device

GeniSys AI is an open source Artificial Intelligence Assistant Network using Computer Vision, Natural Linguistics and the Internet of Things. GeniSys uses a system based on [TASS A.I](https://github.com/TASS-AI/TASS-Facenet "TASS A.I") for [vision](https://github.com/GeniSysAI/Vision "vision"), an [NLU engine](https://github.com/GeniSysAI/NLU "NLU engine") for natural language understanding, in browser speech synthesis and speech recognition for speech and hearing, all homed on a dedicated Linux server in your home and managed via a secure UI.

# About GeniSys Foscam TASS Device

The **GeniSys Foscam TASS Device** uses Siamese Neural Networks and [Triplet Loss](https://towardsdatascience.com/lossless-triplet-loss-7e932f990b24 "Triplet Loss") to classify known and unknown faces. GeniSys Foscam TASS Device is homed on an UP2 (You can also any Linux device or RPI etc), and connects to the stream of a Foscam IP camera.

# Siamese Neural Networks & Triplet Loss
 
As mentioned above, GeniSys Foscam TASS Device uses Siamese Neural Networks & Triplet Loss, but what exactly are they?

Siamese Neural Networks basically are made up of 2 neural networks that are exactly the same, hence the name Siamese Neural Networks. Given two images, we use the identical networks to calculate the similarity between the two images. Basically Siamese Neural Networks learn how to differentiate between objects, or in this case, faces. 

Triplet Loss reduces the difference between an anchor (an image) and a positive sample from the same class, and increases the difference between the ancher and a negative sample from an opposite class. Basically this means that 2 images with the same class (in this case, the same person) will have a smaller distance than two images from different classes (or 2 different people). 

## How GeniSys Foscam TASS Device Works

The main program runs in the background and connects to the stream from the Foscam camera and also connects to the iotJumpWay, it processes each frame alerting the iotJumpWay of the classification (Only that there was a positive or negative classification). Each time a known person is identified the location in their user account is updated based on the configuration of the TASS device, then the frame is updated with bounding boxes and names, and finally the modified stream is streamed on a publicly accesible stream, security updates will be following shortly. You are also able to set rules on the iotJumpWay allowing autonomous communication with other IoT devices and applications in the event of identifications or intruders.

The project uses an **UP2 (Up Squared)** (A regular Linux desktop or Raspberry 3 and above will also work) the **Intel Movidius** for inference and the [iotJumpWay](https://www.iotjumpway.tech "iotJumpWay") for IoT connectivity. You can manage your GeniSys Foscam TASS Device from the server UI.

## Avoiding The Open Set Recognition Issue

With previous versions of TASS built using Tensorflow, **TASS Movidius Inception V3 Classifier**, the model had issues with the [Openset Recognition Issue](https://www.wjscheirer.com/projects/openset-recognition/ "Openset Recognition Issue"). **GeniSys Foscam TASS Device** uses a directory of known images and when presented with a new image, will loop through each image basically measuring the distance between the known image and the presented image, it seems to overcome the issue so far in small testing environments of one or more people. In a large scenario this method will not be scalable, but is fine for small home projects etc. 

Combining **TASS Movidius Inception V3 Classifier** (prone to open set recognition issues) and **GeniSys Foscam TASS Device** allows us to catch false positives and verify positive classifications using the name/ID of that prediction to quickly index into the images and make a single calculation to determine if Inception classified the person correctly or not using Facenet and making the project more scalable. The latest Inception version of the classifier will be uploaded to this repository soon.

# What Will We Do?

1. Install the [Intel® NCSDK](https://github.com/movidius/ncsdk "Intel® NCSDK") on a Linux development device.
2. Clone & set up the repo.
3. Install and download all requirements.
4. Prepare your known and testing faces datasets.
5. Test the **GeniSys Foscam TASS Device** on the testing dataset.
6. Run **GeniSys Foscam TASS Device** on a live webcam
7. Install the [Intel® NCSDK API](https://github.com/movidius/ncsdk "Intel® NCSDK API") on a Raspberry Pi 3 / UP 2.
8. Upload and run the program on an **UP2** or **Raspberry Pi 3**

# Python Versions

- Tested in Python 3.5

# Software Requirements

- [Intel® NCSDK](https://github.com/movidius/ncsdk "Intel® NCSDK")
- [Tensorflow 1.4.0](https://www.tensorflow.org/install "Tensorflow 1.4.0")
- [iotJumpWay MQTT Client](https://github.com/iotJumpway/JumpWayMQTT "iotJumpWay MQTT Client")

# Hardware Requirements

- 1 x [Intel® Movidius](https://www.movidius.com/ "Intel® Movidius")
- 1 x Linux Desktop for Movidius development (Full SDK)
- 1 x Raspberry Pi 3 / UP Squared for the classifier / servers

# UFW Firewall

UFW firewall is used to protect the ports of your TASS device. 

```
 $ sudo ufw status
   Status: inactive
```
If you are using this system on the same device as your GeniSys server, the local firewall has already been set up when you set up the server all you need to do is open the ports that you decide to use for this project.

The ports are specified in **required/confs.json**. The default settings are set to **8080** for the streaming port and **8181** for the socket port. **FOR YOUR SECURITY YOU SHOULD CHANGE THESE!**.

```
"Cameras": [
    {
        "ID": 0,
        "URL": "",
        "RTSPuser": "",
        "RTSPpass": "",
        "RTSPip": "",
        "RTSPport": 0,
        "RTSPendpoint": "",
        "Name": "",
        "Stream": "",
        "StreamAccess": "",
        "StreamPort": 8080,
        "SocketPort": 8181 
    }
]
```

To allow access to the ports use the following command for each of your ports:

```
 $ sudo ufw allow 8080
 $ sudo ufw allow 8181
 $ sudo ufw status
```

```
 Status: active

 To                         Action      From
 --                         ------      ----
 22                         ALLOW       Anywhere
 8080                       ALLOW       Anywhere
 8181                       ALLOW       Anywhere
 22 (v6)                    ALLOW       Anywhere (v6)
 8080 (v6)                  ALLOW       Anywhere (v6)
 8181 (v6)                  ALLOW       Anywhere (v6)
```

# Install NCSDK On Development Device

![Intel® Movidius](images/movidius.jpg)

Now install the **NCSDK** on your development device.

```
 $ mkdir -p ~/workspace
 $ cd ~/workspace
 $ wget https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/ncsdk-01_12_00_01-full/ncsdk-1.12.00.01.tar.gz 
 $ tar -xvf ncsdk-1.12.00.01.tar.gz  
 $ cd ~/workspace/ncsdk-1.12.00.01
 $ make install
```

The above is a temporary way of getting the version we need as NCSDK Github is currently offline as they move towards an entirely open source project. Once this is fixed you will use the follwoing as normal:

```
 $ git clone https://github.com/movidius/ncsdk.git
 $ cd ~/workspace/ncsdk
 $ make install
```

Then plug your Movidius into your device and issue the following commands:

```
 $ cd ~/workspace/ncsdk
 $ make examples
```

# Cloning The Repo

You will need to clone this repository to a location on your development terminal. Navigate to the directory you would like to download it to and issue the following commands.
```
  $ git clone https://github.com/GeniSysAI/Vision.git
```

Once you have the repo, you will find the related files in the [Foscam](https://github.com/GeniSysAI/Vision/Foscam "Foscam") directory.

# Setup

Now you need to setup the software required for the classifier to run. The setup.sh script is a shell script that you can run on both your development device and Raspberry Pi 3 / UP Squared device. 

Make sure you have installed the **NCSDK** on your developement machine, the following command assumes you are located in the [Foscam](https://github.com/GeniSysAI/Vision/Foscam "Foscam") directory.

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

## iotJumpWay Device Connection Credentials & Settings

Setup an iotJumpWay Location Device for IDC Classifier, ensuring you set up a camera node, as you will need the ID of the dummy camera for the project to work. Once your create your device add the location ID and Zone ID to the **IoTJumpWay** details in the confs file located at **required/confs.json**, also add the device ID and device name exactly, add the MQTT credentials to the **IoTJumpWayMQTT** .

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

## Preparing Dataset

You need to set up two very small datasets. As we are using a pretrained Facenet model there is no training to do in this tutorial and we only need one image per known person. You should see the **known** and **testing** folders in the **data** directory, this is where you will store 1 image of each person you want to be identified by the network, and also a testing dataset that can include either known or unknown faces for testing. When you store the known data, you should name each image with the name you want them to be identified as in the system, in my testing I used images of me and two other random people, the 1 image used to represent myself in the known folder was named Adam

## Foscam Stream

**Foscam.py** connects to the stream of the Foscam on your device, processes the frames and streams them to a local server. Be sure to update your configuration with your RTSP details for the Foscam stream. The ports are specified in **required/confs.json**. The default settings are set to **8080** for the streaming port and **8181** for the socket port. **FOR YOUR SECURITY YOU SHOULD CHANGE THESE!**.

```
"Cameras": [
    {
        "ID": 0,
        "URL": "",
        "RTSPuser": "",
        "RTSPpass": "",
        "RTSPip": "",
        "RTSPport": "",
        "RTSPendpoint": "",
        "Name": "",
        "Stream": "",
        "StreamAccess": "",
        "StreamPort": 8080 
    }
],
```
```
"Socket":{
    "host" : "localhost",
    "port" : 8181
}
```

# Recognition / Identification

The program uses a **dlib** model to recognize faces in the frames / mark the facial points on the frame, and **Facenet** to determine whether they are a known person or not. Below are the outputs around the time that the above photo was taken. You will see that the program publishes to the **Warnings** channel of the iotJumpWay, this is currently the name for the channel that handles device to device communication via rules but will change in the near future so something more appropriate.

```
-- Saved frame
-- Total Difference is: 1.0537698864936829
-- MATCH
-- Published: 30
-- Published to Device Warnings Channel
```

# Install NCSDK On UP Squared / Raspberry Pi 3

![UP2](images/UPSquared.jpg)

If you would like to use the IDC Classifier on the IoT, this tutorial has been tested on the **UP2** and the **Raspberry Pi**. You can install the **NCSDK** on your **UP Squared** / **Raspberry Pi 3** device, this will be used by the classifier to carry out inference on local images or images received via the API we will create. Make sure you have the Movidius plugged in to the device and follow the guide below:

```
 $ mkdir -p ~/workspace && cd ~/workspace
 $ wget https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/ncsdk-01_12_00_01-full/ncsdk-1.12.00.01.tar.gz 
 $ tar -xvf ncsdk-1.12.00.01.tar.gz  
 $ cd ~/workspace/ncsdk-1.12.00.01/api/src
 $ make
 $ sudo make install
```

The above is a temporary way of getting the version we need as NCSDK Github is currently offline as they move towards an entirely open source project. Once this is fixed you will use the follwoing as normal:

```
 $ mkdir -p ~/workspace && cd ~/workspace
 $ git clone https://github.com/movidius/ncsdk.git
 $ cd ~/workspace/ncsdk/api/src
 $ make
 $ sudo make install
 
 $ cd ~/workspace
 $ git clone https://github.com/movidius/ncappzoo
 $ cd ncappzoo/apps/hello_ncs_py
 $ python3 hello_ncs.py
```

# Upload File Structure To UP Squared / Raspberry Pi 3

Now you need to upload the required files to the UP Squared / Raspberry Pi 3. Copy the **Foscam** directory from your **development machine** to your **UP Squared / Raspberry Pi 3** then navigate to the home directory of the project.

# Use GeniSys Foscam TASS Device

**FI8916P-V3.py** connects to the Foscam stream, processes the frames and sends them to a local server. Be sure to edit the **ID** and **Name** values of the **Cameras** section of **required/confs.json** section using the details provided when setting up the configs, and add the URL of the IP of your device ie: http://192.168.1.200 to the **Stream** value and you can change **StreamPort** to whatever you want. These two fields will determine the address that you access your camera on, using the previous IP (Stream) and the StreamPort as 8080 the address would be **http://192.168.1.200:8080/index.html**.

You can use the **GeniSys Foscam TASS Device** on **UP Squared** / **Raspberry Pi 3** by entering the following command in the [Foscam](https://github.com/GeniSysAI/Vision/Foscam "Foscam") directory of your **UP Squared** / **Raspberry Pi 3**:

```
 $ python3.5 FI8916P-V3.py
```

You can connect to the socket stream using FI8916P-V3-R.py. This program connects to the socket stream with OpenCV,  processes each frame, updating the frames with bounding boxes and classification results, and then streams the modified frames as an mjpg stream.

# Acknowledgements

- Uses code from Intel® **movidius/ncsdk** ([movidius/ncsdk Github](https://github.com/movidius/ncsdk "movidius/ncsdk Github"))
- Uses code from Intel® **davidsandberg/facenet** ([davidsandberg/facenet Github](https://github.com/davidsandberg/facenet "davidsandberg/facenet"))

# Useful Links

Links to related articles that helped at various stages of the project for research / code examples:

- [Open Set Recognition Issue](https://www.wjscheirer.com/projects/openset-recognition/ "Open Set Recognition Issue")
- [PyImageSearch](https://www.pyimagesearch.com/ "PyImageSearch")

# Contributing
Please read [CONTRIBUTING.md](https://github.com/GeniSysAI/Vision/blob/master/CONTRIBUTING.md "CONTRIBUTING.md") for details on our code of conduct, and the process for submitting pull requests to me.

# Versioning
I use SemVer for versioning. For the versions available, see [GeniSysAI/Vision/releases](https://github.com/GeniSysAI/Vision/releases "GeniSysAI/Vision/releases").

# License
This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/GeniSysAI/Vision/blob/master/LICENSE "LICENSE") file for details.

# Bugs/Issues
I use the [repo issues](https://github.com/GeniSysAI/Vision/issues "repo issues") to track bugs and general requests related to using this project. 

# Author
[![Adam Milton-Barker: BigFinte IoT Network Engineer & Intel® Software Innovator](images/Adam-Milton-Barker.jpg)](https://github.com/AdamMiltonBarker)



