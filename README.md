# vm-name-security-groups-script
A script I did for a customer to identify which VMC NSX Security Groups are using criteria based on the name of the VM.

The script will go through all Compute Groups and work out whether they are using criteria based on the name of VM or not. 
It will print on the terminal the groups that are using VM Name criteria and also write to a file (called "List of all VM Name Based Groups.txt").

A sample file is added to this repo. If you want to change the name, go to line 94 and replace the name accordingly.

The script only makes GET requests (apart from the POST to get an temporary token) so it shouldn't cause any disruption. 
But still, use the script at your own risk.


## What are the pre-requisites for this script ?
- Python3 installed on your machine
- a VMware Cloud on AWS account

## How do I use this script ?
- Clone repo.
- Install dependencies.
```
$ pip install -r requirements.txt
```
- Edit the config.ini with your own SDDC ID,  Organization (Org) ID and your access token.

## Usage and example:

```
$ python3 show-vm-name-based-groups.py
The group AVI Controller is using a VM Name based criteria, using the VM name AVI controller
The group AVi-HZ-private is not using a VM Name based criteria.
```
