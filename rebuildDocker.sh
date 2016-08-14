#!/bin/bash

sudo docker stop son-editor-instance
sudo docker rm son-editor-instance
sudo docker build --no-cache -t son-editor-img .
sudo docker run -dit --name son-editor-instance  -p 5000:5000 -p 5050:5050 son-editor-img
sudo docker exec -it son-editor-instance bash
