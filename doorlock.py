import paho.mqtt.client
import requests
import json
import boto3
from pycognito.aws_srp import AWSSRP
from pprint import pprint
import time
import paho.mqtt.client as paho
import random
import datetime

api_key="hnuu9jbbJr7MssFDWm5nU2Z7nG5Q5rxsaqWsE7e9" # maybe hardcoded into app?
username=""
password=""

check_interval_seconds = 30
broker = '192.168.1.10'
port = 1883
topic = "schlage/lock"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


def gettoken():
    client = boto3.client('cognito-idp',region_name='us-west-2')
    aws = AWSSRP(username=username, password=password,
                 client_id='t5836cptp2s1il0u9lki03j5', pool_id="us-west-2_2zhrVs9d4", client=client, client_secret="1kfmt18bgaig51in4j4v1j3jbe7ioqtjhle5o6knqc5dat0tpuvo")
    tokens = aws.authenticate_user()
    #pprint(tokens)
    #pprint(tokens['AuthenticationResult']['AccessToken'])
    return tokens['AuthenticationResult']['AccessToken']


def getinfo(AccessToken):
    res=requests.get("https://api.allegion.yonomi.cloud/v1/devices?archetype=lock", headers={"Authorization":f"Bearer {AccessToken}","x-api-key": api_key, "content-type": "application/json", "accept-encoding": "gzip", "user-agent": "okhttp/4.2.2" })
    return res.json()

def getdevice(AccessToken):
    res=requests.get("https://api.allegion.yonomi.cloud/v1/devices?archetype=lock", headers={"Authorization":f"Bearer {AccessToken}","x-api-key": api_key, "content-type": "application/json", "accept-encoding": "gzip", "user-agent": "okhttp/4.2.2" })
    dict=json.loads(res.text)
    return dict[0]['deviceId']

def getlockstate(AccessToken):
    res=requests.get("https://api.allegion.yonomi.cloud/v1/devices?archetype=lock", headers={"Authorization":f"Bearer {AccessToken}","x-api-key": api_key, "content-type": "application/json", "accept-encoding": "gzip", "user-agent": "okhttp/4.2.2" })
    dict=json.loads(res.text)
    return dict[0]['attributes']['lockState']



def togglelock(token, deviceid,lockstate):
    data=f'''
{{
  "attributes": {{
    "lockState": {lockstate}
  }}
}}
    '''
    res = requests.put(f"https://api.allegion.yonomi.cloud/v1/devices/{deviceid}",
                       headers={"x-api-key": api_key, "Authorization": f"Bearer {token}",
                                "content-type": "application/json; charset=UTF-8", "Accept-Encoding": "gzip",
                                "user-agent": "okhttp/4.2.2"},
                       data=data
                       )
    return res.json()['attributes']['lockState']

def on_message(client, userdata, message):
    time.sleep(1)

    deviceid=getdevice(AccessToken)
    if str(message.payload.decode("utf-8")) == "LOCK":
        print("Received lock command")
        lockstate = togglelock(AccessToken, deviceid, 1)
        if lockstate==1:
            client.publish(topic + "/state", "LOCKED")
    if str(message.payload.decode("utf-8")) == "UNLOCK":
        print("Received unlock command")
        lockstate = togglelock(AccessToken, deviceid, 0)
        if lockstate==0:
            client.publish(topic + "/state", "UNLOCKED")

print("Connecting to Schlage instance...")
AccessToken=gettoken()
token_acquired=datetime.datetime.now()
client=paho.Client(client_id)
client.on_message=on_message
print("connecting to broker...",broker)
client.connect(broker)#connect
client.loop_start() #start loop to process received messages
print(f"subscribing to topic {topic}/command")
client.subscribe(topic+"/command")#subscribe
time.sleep(2)
while True:
    if datetime.datetime.now() - token_acquired > datetime.timedelta(minutes=58):
        print("Reconnecting to Schlage instance to renew token...")
        AccessToken = gettoken()
        token_acquired = datetime.datetime.now()
    lockstate=getlockstate(AccessToken)
    if lockstate==1:
        print("Publishing status: LOCKED")
        client.publish(topic+"/state","LOCKED")
    if lockstate==0:
        print("Publishing status: UNLOCKED")
        client.publish(topic+"/state","UNLOCKED")
    time.sleep(check_interval_seconds)

