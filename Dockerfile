FROM python:3

#install son-cli tools
RUN git clone https://github.com/CN-UPB/son-cli
WORKDIR /son-cli
RUN python bootstrap.py
RUN bin/buildout
WORKDIR ..

#install son-editor-backend
RUN git clone https://github.com/CN-UPB/upb-son-editor-backend

# Set the default directory where CMD will execute
WORKDIR /upb-son-editor-backend

# copy config with secrets into docker image
ADD src/config.yaml src/config.yaml

#install the son-editor
RUN python3 setup.py build
RUN python3 setup.py install

# Expose ports
EXPOSE 5000 #son-editor-backend
EXPOSE 5050 #github-webhook

# Set the default command to execute
CMD son-editor & github-webhook &