#!/bin/bash
#初次部署先安装pip环境：
#python3 -m pip install -r requirements.txt
#并需初始化数据库以及admin账户：
#python3 manage.py makemigrations app
#python3 manage.py migrate
#python3 manage.py createsuperuser
ps -aux | grep manage.py |awk '{print $2}'|xargs kill -9
ps -aux | grep server.py |awk '{print $2}'|xargs kill -9
nohup python3 -u manage.py runserver_plus --cert 3865446_www.geecat.cn.pem --key-file 3865446_www.geecat.cn.key 0.0.0.0:8080  > django.log 2>&1 &
nohup python3 -u server.py  > socket.log 2>&1 &
