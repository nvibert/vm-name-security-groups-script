#!/usr/bin/env python3
# The shebang above is to tell the shell which interpreter to use. This make the file executable without "python3" in front of it (otherwise I had to use python3 pyvmc.py)
# I also had to change the permissions of the file to make it run. "chmod +x pyVMC.py" did the trick.
# I also added "export PATH="MY/PYVMC/DIRECTORY":$PATH" (otherwise I had to use ./pyvmc.y)
# For git BASH on Windows, you can use something like this #!/C/Users/usr1/AppData/Local/Programs/Python/Python38/python.exe

################################################################################
### Copyright (C) 2019-2020 VMware, Inc.  All rights reserved.
### SPDX-License-Identifier: BSD-2-Clause
################################################################################


"""

VMware Cloud on AWS API Documentation is available at: https://code.vmware.com/apis/920/vmware-cloud-on-aws
CSP API documentation is available at https://console.cloud.vmware.com/csp/gateway/api-docs
vCenter API documentation is available at https://code.vmware.com/apis/366/vsphere-automation

You can install python 3.8 from https://www.python.org/downloads/windows/ (Windows) or https://www.python.org/downloads/mac-osx/ (MacOs).

You can install the dependent python packages locally (handy for Lambda) with:
pip3 install requests or pip3 install requests -t . --upgrade
pip3 install configparser or pip3 install configparser -t . --upgrade
pip3 install PTable or pip3 install PTable -t . --upgrade

With git BASH on Windows, you might need to use 'python -m pip install' instead of pip3 install

"""

import requests                         # need this for Get/Post/Delete
import configparser                     # parsing config file
import time
import sys
from prettytable import PrettyTable

config = configparser.ConfigParser()
config.read("./config.ini")
strProdURL      = config.get("vmcConfig", "strProdURL")
strCSPProdURL   = config.get("vmcConfig", "strCSPProdURL")
Refresh_Token   = config.get("vmcConfig", "refresh_Token")
ORG_ID          = config.get("vmcConfig", "org_id")
SDDC_ID         = config.get("vmcConfig", "sddc_id")




class data():
    sddc_name       = ""
    sddc_status     = ""
    sddc_region     = ""
    sddc_cluster    = ""
    sddc_hosts      = 0
    sddc_type       = ""

def getAccessToken(myKey):
    """ Gets the Access Token using the Refresh Token """
    params = {'refresh_token': myKey}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    jsonResponse = response.json()
    access_token = jsonResponse['access_token']
    return access_token

def getNSXTproxy(org_id, sddc_id, sessiontoken):
    """ Gets the Reverse Proxy URL """
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = "{}/vmc/api/orgs/{}/sddcs/{}".format(strProdURL, org_id, sddc_id)
    response = requests.get(myURL, headers=myHeader)
    json_response = response.json()
    proxy_url = json_response['resource_config']['nsx_api_public_endpoint_url']
    return proxy_url

def getSDDCVMNameBasedGroup(proxy_url,sessiontoken):
    """ Gets the SDDC Groups that are VM-based """
    myHeader = {'csp-auth-token': sessiontoken}
    proxy_url_short = proxy_url.rstrip("sks-nsxt-manager")
    myURL = proxy_url_short + "policy/api/v1/infra/domains/cgw/groups"
    response = requests.get(myURL, headers=myHeader)
    json_response = response.json()
    sddc_group = json_response['results']
    for i in sddc_group:
        group_id = i["id"]
        myURL = proxy_url_short + "policy/api/v1/infra/domains/cgw/groups/" + group_id
        response = requests.get(myURL, headers=myHeader)
        json_response = response.json()
        if not json_response['expression']:
            continue
        else:
            group_criteria = json_response['expression'][0]
            group_name = json_response['display_name']
            if group_criteria["resource_type"] == "Condition" and "member_type" in group_criteria.keys():
                if group_criteria["member_type"] == "VirtualMachine" and group_criteria["key"] == "Name":
                    print("The group " + group_name + " is using a VM Name based criteria, using the VM name " + group_criteria["value"])
                    f = open("List of all VM Name Based Groups.txt", "a")
                    f.write("\nThe group " + group_name + " is using a VM Name based criteria, using the VM name " + group_criteria["value"])
                    f.close()
                else:
                    print("The group " + group_name + " is not using a VM Name based criteria.")
                    continue
            else:
                print("The group " + group_name + " is not using a VM Name based criteria.")
                continue

# --------------------------------------------
# ---------------- Main ----------------------
# --------------------------------------------

session_token = getAccessToken(Refresh_Token)
proxy = getNSXTproxy(ORG_ID, SDDC_ID, session_token)
getSDDCVMNameBasedGroup(proxy, session_token)
