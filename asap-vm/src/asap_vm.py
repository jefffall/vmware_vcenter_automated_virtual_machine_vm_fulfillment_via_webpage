#!/usr/bin/python3
from flask import Flask, request, jsonify, send_from_directory
import socket
import logging
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


app = Flask(__name__, static_url_path='')

api_url = 'https://vcenter.jeffreyfall.com/rest'
api_user = 'administrator@vsphere.local'
api_pass = '!Vmware!Vmware1'

def getDatastoreInformation(datastore):
    summary = datastore.summary
    capacity = summary.capacity
    freeSpace = summary.freeSpace
    uncommittedSpace = summary.uncommitted
    #freeSpacePercentage = (float(freeSpace) / capacity) * 100
    provisionedSpace = 0
    if uncommittedSpace is not None:
        provisionedSpace = (capacity - freeSpace) + uncommittedSpace
        provisionedSpace = provisionedSpace /1073741824.0
    return(round(capacity/1073741824.0,2), round(freeSpace/1073741824.0,2), round(provisionedSpace,2))

def get_datastore_stats():
    #si = SmartConnectNoSSL(host="vcenter.jeffreyfall.com", user="administrator@vsphere.local",
        #pwd="!Vmware!Vmware1", port=int(80))
    
    #session = requests.session()
    #session.verify = False # SSL cert verification
    #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disable a ssl cert error warning
    #client = create_vsphere_client(server=idcs[idc]['API'], username=os.environ['TF_VAR_vsphere_user'], password=os.environ['TF_VAR_vsphere_pass'], session=session)                          
    
    si = SmartConnect(host="vcenter.jeffreyfall.com", user="administrator@vsphere.local", pwd="!Vmware!Vmware1", port=int(443))
     
    content = si.RetrieveContent()
    print ("content = ")
    print (content.rootFolder.childEntity)
    
    for datacenter in content.rootFolder.childEntity:
        if hasattr(datacenter.vmFolder, 'childEntity'):
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
               
            datastores = datacenter.datastore
            largest_freespace = 0
            dc_capacity = 0
            dc_freespace = 0
            dc_provisioned = 0
            for ds in datastores:
                capacity, freespace, provisioned = getDatastoreInformation(ds)
                if freespace > largest_freespace:
                    largest_freespace = dc_freespace
                dc_capacity = dc_capacity + capacity
                dc_freespace = dc_freespace + freespace
                dc_provisioned = dc_provisioned + provisioned
                            
            #print("capacity: "+str(dc_capacity))
            #print("freespace: "+str(dc_freespace))
            #print("largest freespace: "+str(largest_freespace))
            #print("dc_provisioned: "+str(dc_provisioned))
            
            del si
            del content
            del vmFolder
            del vmList
            
            return (dc_capacity, dc_freespace, largest_freespace, dc_provisioned)
            #return (str(round(dc_capacity,2)), str(round(dc_freespace,2)), str(round(largest_freespace,2)), str(round(dc_provisioned,2)) )
            
def get_vm_info_rest(): 
    session = requests.session()

    # Disable cert verification for demo purpose. 
    # This is not recommended in a production environment.
    session.verify = False
    
    # Disable the secure connection warning for demo purpose.
    # This is not recommended in a production environment.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Connect to a vCenter Server using username and password
    vsphere_client = create_vsphere_client(server='169.44.153.126', username='administrator@vsphere.asap', password='!Vmware!Vmware1', session=session)
    
    # List all VMs inside the vCenter Server
    #print(vsphere_client.vcenter.VM.list())
    return (vsphere_client.vcenter.VM.list())
   
   
@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_img(path):
    return send_from_directory('assets/img', path)


@app.route('/get_datastore_metrics', methods=['POST'])
def get_datastore_numbers():
    if request.method == "POST":
        capacity, freespace, largest_freespace, dc_provisioned = get_datastore_stats()
        
        
        mylist = get_vm_info_rest()
        vminfo = ""
        for line in mylist:
            #print (line.vm, line.name, line.power_state, line.cpu_count, line.memory_size_mib) 
            vminfo = vminfo + line.vm +": "+ line.name +" "+  line.power_state +" "+  str(line.cpu_count) +" CPU "+  str(line.memory_size_mib) + " GiB MEM<br>"      
            print (vminfo)
            
        if capacity > 1000:
            capacity = str(round(capacity/1000.0, 2)) + " TB"
        else:
            capacity = str(round(capacity, 2)) + " GB"
                
        if freespace > 1000.0:
            freespace = str(round(freespace/1000.0,2)) + " TB"
        else:
            freespace = str(round(freespace, 2)) + " GB"
                
        if largest_freespace > 1000.0:
            largest_freespace = str(round(largest_freespace/1000.0, 2)) + " TB"
        else:
            largest_freespace = str(round(largest_freespace ,2)) + " GB"
        
        if dc_provisioned > 1000.0:
            dc_provisioned = str(round(dc_provisioned/1000.0, 2)) + " TB"
        else:
            dc_provisioned = str(round(dc_provisioned, 2)) + " GB"
                
                
    return jsonify({"capacity" : capacity, "freespace" : freespace,\
                    "largest_freespace" : largest_freespace,\
                    "dc_provisioned" : dc_provisioned,\
                    "vminfo" : vminfo\
                    })
'''
self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
'''

app.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
app.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#app.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
app.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
app.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
