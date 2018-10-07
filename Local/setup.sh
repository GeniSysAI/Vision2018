#!/bin/sh

echo "SHELL|INFO: Location core"
pip3 install --upgrade pip --user
pip3 install -r requirements.txt --user 
echo "SHELL|OK: Installed Requirements"

if [ ! -f "model/20170512-110547.zip" ]
then
    echo "SHELL|INFO: Downloading Facenet"
    rm -f ./cookies.txt
    touch ./cookies.txt
    wget --load-cookies ./cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies ./cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5MzpY9kBtDVZ2RpVDYwWmxoSUk' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=0B5MzpY9kBtDVZ2RpVDYwWmxoSUk" -O model/20170512-110547.zip && rm -rf ./cookies.txt
    echo "SHELL|OK: Facenet Downloaded"
else
    echo "SHELL|OK: Facenet Exists"
fi

if [ ! -f "model/20170512-110547" ]
then
    echo "SHELL|INFO: Unzipping Facenet"
    cd model
    echo "SHELL|INFO: Location model"
    unzip 20170512-110547.zip
    echo "SHELL|OK: Unzipped Facenet"
    cd ../
    echo "SHELL|INFO: Location core"
else
    echo "SHELL|OK: Facenet Unzipped"
fi

if [ ! -f "model/inception_resnet_v1.py" ]
then
    echo "SHELL|INFO: Downloading Inception Resnet"
    cd model
    echo "SHELL|INFO: Location model"
    wget -c --no-cache -P . https://raw.githubusercontent.com/davidsandberg/facenet/361c501c8b45183b9f4ad0171a9b1b20b2690d9f/src/models/inception_resnet_v1.py -O inception_resnet_v1.py
    echo "SHELL|OK: Downloaded Inception Resnet"
	sed -i 's/\r//' *.py
	chmod +x *.py
    cd ../
    echo "SHELL|INFO: Location core"
else
    echo "SHELL|OK: Inception Resnet Exists"
fi

cd model/20170512-110547
echo "SHELL|INFO: Location model/20170512-110547"

if [ ! -e facenet_celeb.data-00000-of-00001 ]
then 
    echo "SHELL|INFO: Moving Data"
    mv model-20170512-110547.ckpt-250000.data-00000-of-00001 facenet_celeb.data-00000-of-00001
    echo "SHELL|OK: Moved Data"
else 
    echo "SHELL|OK: Data Exists"
fi

if [ ! -e facenet_celeb.index ]
then 
    echo "SHELL|INFO: Moving Index File"
    mv  model-20170512-110547.ckpt-250000.index facenet_celeb.index
    echo "SHELL|OK: Moved Index File"
else 
    echo "SHELL|OK: Index File Exists"
fi

if [ ! -e facenet_celeb.meta ]
then 
    echo "SHELL|INFO: Moving Meta File"
    mv model-20170512-110547.meta facenet_celeb.meta
    echo "SHELL|OK: Moved Meta File"
else 
    echo "SHELL|OK: Index Meta Exists"
fi

if [ ! -e facenet_celeb_ncs ]
then
    echo "SHELL|INFO: Converting facenet_celeb"
    python3 ../convert_facenet.py model_base=facenet_celeb
    echo "SHELL|OK: Converting facenet_celeb"
else
    echo "SHELL|OK: facenet_celeb Exists"
fi

cd ../../
echo "SHELL|INFO: Location core"

if [ -e tass.graph ]
then
    echo "SHELL|OK: Graph Exists"
    echo "SHELL|OK: Setup Completed"
else
    echo "SHELL|INFO: Compiling Graph"
    cd model/20170512-110547/facenet_celeb_ncs
    echo "SHELL|INFO: Location model/20170512-110547/facenet_celeb_ncs"

    mvNCCompile  facenet_celeb_ncs.meta -w facenet_celeb_ncs -s 12 -in input -on output -o tass.graph
    cp tass.graph ../..
    echo "SHELL|INFO: Compiled Graph"

    cd ../../../
    echo "SHELL|INFO: Location core"
    echo "SHELL|OK: Setup Completed"
fi

