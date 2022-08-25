import requests
import json
import boto3
from pycognito.aws_srp import AWSSRP
from pprint import pprint
import time

api_key="hnuu9jbbJr7MssFDWm5nU2Z7nG5Q5rxsaqWsE7e9" # maybe hardcoded into app?

username=""
password=""
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

AccessToken=gettoken()
deviceid=getdevice(AccessToken)
lockstate=getlockstate(AccessToken)
print(f"Current lockstate: {lockstate}")
lockstate=togglelock(AccessToken,deviceid,1)
print(f"New lockstate: {lockstate}")
print("Sleeping to emulate app behavior...")
time.sleep(10)
lockstate=getlockstate(AccessToken)
print(f"Recheck lockstate... Is now {lockstate} which probably is still the old state for some reason...")