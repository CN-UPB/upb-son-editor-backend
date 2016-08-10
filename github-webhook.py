from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
# http://pymotw.com/2/hmac/
import hmac
import hashlib
# http://techarena51.com/index.php/how-to-install-python-3-and-flask-on-linux/
import subprocess
import os
import traceback
import requests
from threading import Thread
# https://pythonhosted.org/Flask-Mail/
import logging
# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='deployment.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger("github-webhook")

app = Flask(__name__)

def verify_hmac_hash(data, signature):
    github_secret = bytes('slkjhsdfvjasdvffaskldfkasn23o423kl', 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)


@app.route("/payload", methods=['POST'])
def github_payload():
    try:
        signature = request.headers.get('X-Hub-Signature')
        data = request.data
        if verify_hmac_hash(data, signature):
            if request.headers.get('X-GitHub-Event') == "ping":
                return jsonify({'msg': 'Ok'})
            if request.headers.get('X-GitHub-Event') == "push":
                payload = request.get_json()
                if payload['commits'][0]['distinct'] == True:
                    try:
                        logger.info(str(request))
                        redeploy()
                        return Response("started deploying!", mimetype='text/plain')
                    except subprocess.CalledProcessError as error:
                        print("Code deployment failed:"+ error.output)
                        return jsonify({'msg': str(error.output)})
                else:
                    return jsonify({'msg': 'nothing to commit'})

        else:
            return jsonify({'msg': 'invalid hash'})
    except Exception as err:
        traceback.print_exc()

def redeploy():
    logger.info("shutting down son-editor")
    res = requests.get('http://localhost:5000/shutdown')
    logger.info("Response was:" +res.text)
    logger.info("starting deployment")
    runProcess(['git','pull'])
    runProcess(['python', 'setup.py', 'build'])
    runProcess(['python', 'setup.py', 'install'])
    runInBackground(['son-editor'])

def runInBackground(exe):
    subprocess.Popen(exe)

def runProcess(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      logger.info(line)
      if(retcode is not None):
        break

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5050)
