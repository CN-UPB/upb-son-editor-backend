import hashlib
import hmac
import logging
import subprocess
import traceback

import requests
from flask import url_for
from pkg_resources import Requirement, resource_filename
import yaml
from threading import Thread
from flask import Flask, request, jsonify, Response

# configFileName = resource_filename(Requirement.parse("sonata_editor"), "deployment.yml")
CONFIG = yaml.safe_load(open("deployment.yml"))
DEPLOYMENT_DIVIDER = "##########################################################"

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.INFO,
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
    github_secret = bytes(CONFIG['github-secret'], 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)


@app.route("/latest_build_log")
def show_latest_log():
    with open("deployment.log") as logfile:
        return logfile.read().split(DEPLOYMENT_DIVIDER)[-1].replace("\n", "<br/>")


@app.route("/payload", methods=['POST'])
def github_payload():
    logger.info(DEPLOYMENT_DIVIDER)
    build_log_url = url_for("show_latest_log", _external=True)
    try:
        signature = request.headers.get('X-Hub-Signature')
        data = request.data
        if verify_hmac_hash(data, signature):
            if 'X-GitHub-Event' in request.headers:
                if request.headers.get('X-GitHub-Event') == "ping":
                    return jsonify({'msg': 'Ok'})
                if request.headers.get('X-GitHub-Event') == "deployment":
                    payload = request.get_json()
                    logger.debug(str(payload))
                    Thread(target=redeploy, args=(payload, build_log_url)).start()
                    return Response("Starting deployment", mimetype='text/plain')
                else:
                    logger.warn(request.headers.get('X-GitHub-Event'))
                    return jsonify({'msg': 'ok thanks for letting me know!'})
            else:
                return jsonify({'msg': 'hmmm somthing is wrong'}), 500
        else:
            return jsonify({'msg': 'invalid hash'})
    except Exception as err:
        traceback.print_exc()


def redeploy(payload, build_log_url):
    logger.info("Starting redeployment script")
    for command in CONFIG['deployment-script']:
        required = True
        if 'required' in command:
            required = command['required']

        if 'update-status' in command:
            update_deployment_status(payload, "pending", command['update-status'], build_log_url)
        elif 'request' in command:
            if command['request'] is not None:
                logger.info(command['request'])
            try:
                res = None
                if command['method'] == 'GET':
                    res = requests.get(command['url'])
                elif command['method'] == 'POST':
                    res = requests.post(command['url'])
                if res is not None:
                    logger.info("Response was:" + res.text)
            except Exception as err:
                if required:
                    logger.exception("Code deployment failed")
                    update_deployment_status(payload, "failure", "Deployment failed, see log for details",
                                             build_log_url)
                    return
                else:
                    update_deployment_status(payload, "error", "Deployment failed, see log for details", build_log_url)
                    logger.exception("Code deployment had an error")
        elif 'run' in command:
            if command['run'] is not None:
                logger.info(command['run'])
            try:
                if 'sync' in command:
                    runProcess(command['sync'].split())
                elif 'async' in command:
                    runInBackground(command['async'].split())
            except subprocess.CalledProcessError as error:
                if required:
                    logger.exception("Code deployment failed")
                    update_deployment_status(payload, "failure", "Deployment failed, see log for details",
                                             build_log_url)
                    return
            except Exception as fail:
                if required:
                    logger.exception("Code deployment failed")
                    update_deployment_status(payload, "failure",
                                             "Deployment failed with statuscode {}".format(fail.args[1]), build_log_url)
                    return
    update_deployment_status(payload, "success", "Deployment finished", build_log_url)
    logger.info("Deploy finished!")


def update_deployment_status(payload, state, description, log_url):
    headers = {"Accept": "application/vnd.github.ant-man-preview+json",
               "Authorization": "token " + CONFIG['github-token']}
    res = requests.post(payload["deployment"]["url"] + "/statuses",
                        json={"state": state,
                              "description": description,
                              "log_url": log_url},
                        headers=headers)
    logger.debug(res.text)


def runInBackground(exe):
    subprocess.Popen(exe)
    logger.info("Starting " + str(exe))


def runProcess(exe):
    logger.info("Running " + str(exe))
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        retcode = p.poll()  # returns None while subprocess is running
        line = p.stdout.readline()
        try:
            line = line.decode("utf-8")[::-1].replace('\n', '', 1)[::-1]
            if not line == "":
                logger.info(line)
        except:
            logger.info(line)
        if retcode is not None:
            logger.info("Returncode: {}".format(retcode))
            break
    if not retcode == 0:
        raise Exception(retcode)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
