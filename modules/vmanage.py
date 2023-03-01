import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from time import time


class vManage():


    def __init__(self,server,port,username,password):

        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.host = server + ':' + port
        self.cookie = self.get_auth_cookie()
        self.token = self.get_auth_token()
        self.devices = self.get_devices()
        self.policyID = self.get_active_policyID()
        self.policy = self.get_active_policy()


    def get_auth_cookie(self):

        url = f"https://{self.host}/j_security_check"

        payload = f'j_username={self.username}&j_password={self.password}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)

        cookie = response.cookies.get_dict()['JSESSIONID']

        return cookie


    def get_auth_token(self):

        url = f"https://{self.server}/dataservice/client/token"

        payload={}
        headers = {
        'Cookie': f'JSESSIONID={self.cookie}'
        }

        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        token = response.text

        return token


    def send_request(self,action,resource,body):

        url = f'https://{self.host}/dataservice{resource}'

        headers = {
        'X-XSRF-TOKEN': self.token,
        'Cookie': f'JSESSIONID={self.cookie}',
        'Content-Type': 'application/json',
        }

        response = requests.request(action, url, headers=headers, data=body, verify=False)

        return response
                

    def logout(self):

        url = f"https://{self.host}/logout?nocache={str(int(time()))}"

        payload={}

        headers = {
        'Cookie': f'JSESSIONID={self.cookie}',
        }

        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        message = 'vManage session closed!' if response.status_code == 200 else 'Problems closing session'
        print(message)

    
    def get_devices(self):

        response = self.send_request('GET','/device',body={})
        headers = ['host-name', 'system-ip', 'site-id', 'reachability', 'device-type', 'device-model']
        devices = []

        for device in response.json()["data"]:
            if 'vedge' in device["device-type"]:
                new_row = []
                for header in headers:
                    new_row.append(device[header])
                devices.append(new_row)

        return devices
    

    def get_active_policyID(self):
    
        response = self.send_request('GET','/template/policy/vsmart',body={})

        for policy in response.json()["data"]:
            if policy["isPolicyActivated"]:
                active_policy = policy
                break

        policyID = active_policy["policyId"]

        return policyID
    
    
    def get_active_policy(self):

        response = self.send_request('GET',f'/template/policy/vsmart/definition/{self.policyID}',body={})

        if isinstance(response.json()["policyDefinition"],dict):
            response = self.send_request('GET',f'/template/policy/assembly/vsmart/{self.policyID}',body={})
            policy = response.json()["preview"].splitlines()
        else:
            policy = response.json()["policyDefinition"].splitlines()

        return policy

    def collect_aar_stats(self,system_ips):

        
        headers = ["vdevice-host-name","local-color","remote-system-ip","remote-color","mean-loss","average-latency","mean-jitter"]
        data = [headers]
        
        for system_ip in system_ips:

            response = self.send_request('GET',f'/device/app-route/statistics?deviceId={system_ip}',body={})
            aar_stats = response.json()["data"]

            for line in aar_stats:

                new_row = []

                for item in headers:

                    new_row.append(line[item])

                data.append(new_row)

        return data
