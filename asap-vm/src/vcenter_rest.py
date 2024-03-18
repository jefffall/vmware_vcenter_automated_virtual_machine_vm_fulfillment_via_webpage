import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client
session = requests.session()

# Disable cert verification for demo purpose. 
# This is not recommended in a production environment.
session.verify = False

# Disable the secure connection warning for demo purpose.
# This is not recommended in a production environment.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to a vCenter Server using username and password
vsphere_client = create_vsphere_client(server='169.44.153.126', username='administrator@vsphere.asap', password='!VerySecure1', session=session)

# List all VMs inside the vCenter Server
#print(vsphere_client.vcenter.VM.list())
mylist = vsphere_client.vcenter.VM.list()
for line in mylist:
    #print (line)
    print (line.vm, line.name, line.power_state, line.cpu_count, line.memory_size_mib)