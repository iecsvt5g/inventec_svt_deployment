#!/usr/bin/sh

yum install git -y
sleep 1
yum install vim -y
sleep 1
yum install epel-release -y
sleep 1
yum install python36 python36-libs python36-devel python36-pip -y
sleep 1
pip3 install --upgrade pip
sleep 1
echo "alias python='/usr/bin/python3.6'" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc
source ~/.bashrc
python -V
sleep 1
python -m pip -V
sleep 1
pip install pymysql
sleep 1
pip install influxdb
sleep 1
pip install paramiko
sleep 1
pip install requests
sleep 1
pip install pyinstaller
