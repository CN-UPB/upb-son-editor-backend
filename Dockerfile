FROM python:3

#install son-cli tools
RUN git clone https://github.com/CN-UPB/son-cli
WORKDIR /son-cli
RUN python3 setup.py build
RUN python3 setup.py install
WORKDIR ..

#install son-editor-backend
RUN git clone https://github.com/CN-UPB/upb-son-editor-backend#

#set git a dummy user to be enable stashing the config file
RUN git config user.email dummy@user.com
RUN git config user.name "Dummy User"

# Set the default directory where CMD will execute
WORKDIR /upb-son-editor-backend

# copy config with secrets into docker image
ADD src/config.yaml src/config.yaml
#install the son-editor
RUN python3 setup.py build
RUN python3 setup.py install

# expose ports
#son-editor-backend
EXPOSE 5000
#github-webhook
EXPOSE 5050

#make sure entrypoint is executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]