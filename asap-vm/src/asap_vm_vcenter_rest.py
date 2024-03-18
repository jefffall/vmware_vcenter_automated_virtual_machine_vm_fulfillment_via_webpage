#!/usr/bin/python3
import datetime
from flask import Flask, request, jsonify, send_from_directory
import socket
import logging
import requests
import urllib3
import uncurl
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from vmware.vapi.vsphere.client import create_vsphere_client

import os
import sys
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor



def run_ansible_playbook():
    variable_manager = VariableManager()
    loader = DataLoader()
    
    InventoryManager(loader=loader)
    inventory = InventoryManager(loader=loader,  sources="localhost")
    playbook_path = 'templatevm.yaml'
    
    #if not os.path.exists(playbook_path):
        ##sys.exit()
    
    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user='slotlocker', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method=None, become_user='root', verbosity=None, check=False)
    
    #variable_manager.extra_vars = {'hosts': 'mywebserver'} 
    passwords = {}
    
    #pbex = PlaybookExecutor(playbooks=['/Users/jfall/templatevm.yaml'], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords=passwords)
    pbex = PlaybookExecutor(playbooks=['/Users/jfall/templatevm.yaml'],inventory=inventory, variable_manager=variable_manager, loader=loader,passwords=passwords)
    variable_manager.safe_basedir = "/Users/jfall"
    results = pbex.run()
    return(results)
    

def build_ansible_template(memory, cpucores, storage, ostoinstall):
    
    memory = memory.replace(" GB", "")
    if memory == "2":
        memory = "2048"
    elif memory == "4":
        memory = "4096"
    elif memory == "8":
        memory = "8192"
    elif memory == "16":
        memory = "16384"
    
    create_date = str(datetime.datetime.now()).split(".")[0]
    
    filename_date = str(datetime.datetime.now()).split(".")[0].replace(" ","").replace(":","")
    
    name = ""
    cpucores = cpucores.replace(" cpu cores","")
    storage = storage.replace(" GB","")
    
    template = ""
    if ostoinstall == "Windows 2019":
        template = "Win2019-Template-Base"
        name = "WinSvr2019 "+create_date
    elif ostoinstall == "Centos 7":
        template = "CentOS7-Template"
        name = "Centos7 "+create_date
    elif ostoinstall == "Ubuntu 18.04":
        template = "Ubuntu-18-template"
        name = "Ubuntu18 "
        


    myyaml = \
'---\n\
- name: Create a VM from a template\n\
  hosts: localhost\n\
  connection: local\n\
  gather_facts: no\n\
  tasks:\n\
  - name: Clone the template\n\
    vmware_guest:\n\
      hostname: vcenter.jeffreyfall.com\n\
      username: administrator@vsphere.local\n\
      password: "!VerySecure1"\n\
      validate_certs: False\n\
      name: '+name+'\n\
      template: '+template+'\n\
      datacenter: Datacenter\n\
      folder: /Datacenter/vm\n\
      state: poweredon\n\
      wait_for_ip_address: yes\n\
      disk:\n\
      - size_gb: '+storage+'\n\
        type: thin\n\
        datastore: datastore3\n\
\n\
      hardware:\n\
        memory_mb: '+memory+'\n\
        num_cpus: '+cpucores+'\n\
        scsi: paravirtual\n\
        memory_reservation_lock: False\n\
        mem_limit: '+memory+'\n\
        mem_reservation: 1024\n\
        cpu_limit: 8096\n\
        cpu_reservation: 4096\n\
        max_connections: 5\n\
        hotadd_cpu: True\n\
        hotremove_cpu: True\n\
        hotadd_memory: True\n\
        version: 12 # Hardware version of virtual machine\n\
        boot_firmware: "efi"'
    print (myyaml)
    myfd = open("vcenter_create_vm.yaml"+filename_date, "w")
    myfd.write(myyaml)
    myfd.close()
    return "vcenter_create_vm.yaml"+filename_date


cache = {}
try:
    cache['session_id'] = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!Vmware!Vmware1'), verify=False).json()['value']
except:
    print ("Issue with getting session ID...")

print(cache['session_id'])



app = Flask(__name__, static_url_path='')


def getDatastoreInformation(datastore):
    capacity = datastore['capacity']
    freeSpace = datastore['free_space']
    provisionedSpace = (capacity - freeSpace)
    provisionedSpace = provisionedSpace /1073741824.0
    return(round(capacity/1073741824.0,2), round(freeSpace/1073741824.0,2), round(provisionedSpace,2))

def get_datastore_stats(session_id):
                         
    result = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/datastore",
    headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
        
    datastores_json = result.json()
    datastores = datastores_json['value']
    
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
            
           
    return (dc_capacity, dc_freespace, largest_freespace, dc_provisioned)
    #return (str(round(dc_capacity,2)), str(round(dc_freespace,2)), str(round(largest_freespace,2)), str(round(dc_provisioned,2)) )
   
@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_img(path):
    return send_from_directory('assets/img', path)


@app.route('/get_datastore_metrics', methods=['POST'])
def get_datastore_numbers():
    if request.method == "POST":
        #sess = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!VerySecure1'), verify=False)
        #session_id = sess.json()['value']
        
        session_id = cache['session_id']

        result = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/vm",
        headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
        
        vm_json = result.json()
        vminfo = ""
        memory_alloc = 0
        vm_count = 0
        vms = vm_json['value']
        for vm in vms:
            vm_count = vm_count + 1
            try:
                if vm['power_state'] == "POWERED_ON":
                    power_state = "Power ON"
                else:
                    power_state = "Power OFF"
            except:
                #session id timed out
                try:
                    cache['session_id'] = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!VerySecure1'), verify=False).json()['value']
                except:
                    print ("Issue with getting session ID...")
            try:         
                mymem =  round(vm['memory_size_MiB']/1000,1)
                memory_alloc = memory_alloc + int(mymem)
            except:
                mymem = " BUILDING"
                vm['cpu_count'] = "0"
            #vminfo = vminfo + vm['vm'] +": "+ vm['name'] +", "+ power_state +", "+  str(vm['cpu_count']) +" CPU, "+  str(mymem) + " GB memory<br>"   
            if "VMware vCenter7 Server" in vm['name'] or "vCLS" in vm['name']:
                pass
                #vminfo = vminfo + vm['name'] +", "+ power_state +", "+  str(vm['cpu_count']) +" CPU, "+  str(mymem) + " GB memory<br>" 
            else:
                myvm = vm['vm']
                myip = get_vm_ip(session_id, myvm)
                vminfo = vminfo + vm['name'].strip() +", "+ power_state +", "+  str(vm['cpu_count']) +" CPU, "+  str(mymem) + " GB mem" +myip+"<br>"    
            
        capacity, freespace, largest_freespace, dc_provisioned = get_datastore_stats(session_id)
        
        if int(capacity) > 1000:
            capacity = str(round(float(capacity/1000),1)) + " TB"
        else:
            capacity = str(round(capacity,1)) + " GB"
            
        if int(freespace) > 1000:
            freespace = str(round(float(freespace/1000),1)) + " TB"
        else:
            freespace = str(round(freespace,1)) + " GB"
    
        #return jsonify({"vminfo" : vminfo})

        return jsonify({"capacity" : capacity,\
                    "freespace" : freespace,\
                    "largest_freespace" : str(round(largest_freespace,2))+" GB",\
                    "dc_provisioned" : str(round(dc_provisioned,2))+" GB",\
                    "memory_alloc" : str(round(memory_alloc,2))+" GB",\
                    "vminfo" : vminfo,\
                    "vm_count" : str(vm_count - 4)
                    })


@app.route('/vcenter_create_vm', methods=['POST'])
def vcenter_create_vm():
    if request.method == "POST":
        if request.is_json == True:
            print ("Processing create vm")
            create_vm = request.get_json()
            memory = create_vm['memory']
            cpucores = create_vm['cpucores']  
            storage = create_vm['storage']
            ostoinstall = create_vm['ostoinstall']
            
            ansible_yaml = build_ansible_template(memory, cpucores, storage, ostoinstall)
            os.system("/Library/Frameworks/Python.framework/Versions/3.8/bin/ansible-playbook /Users/jfall/eclipse-workspace/asap-vm/src/"+ansible_yaml)
            return "creating VM with "+memory+" "+cpucores+" "+ storage+" "+ ostoinstall, 200
            
        




#u = uncurl.parse("curl -X  GET 'https://vcenter.jeffreyfall.com/rest/vcenter/vm/%7Bvm%7D' -H 'vmware-api-session-id: 69672a97c145a2aa79a46b9ab753710d'")
#print (u)

def metrics():
    sess = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!VerySecure1'), verify=False)
    session_id = sess.json()['value']

    result = requests.get("https://vcenter.jeffreyfall.com/api/stats/counters",
    headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
    
    
    counters = result.json()
    for line in counters:
        cid = line['cid']
        myresult = requests.get("https://vcenter.jeffreyfall.com/api/stats/counters/"+cid+"/metadata",
        headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
        metadata = myresult.json()
        metadict = metadata.pop(0)
        
        mid = metadict['mid']
        mycid = metadict['cid']
        #print (mid, mycid)
        
        metrics = requests.get("https://vcenter.jeffreyfall.com/api/stats/counters/"+cid+"/metadata/"+mid,
        headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
        
        metric = metrics.json()
        
        print (metric)
        
def get_vm_ip(session_id, vm):  
    result = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/vm/"+vm+"/guest/identity",
    headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
    ident_json = result.json()
    identity = ident_json['value']
    try:
        return (" IP="+str(identity['ip_address']))
    except:
        return ("")
        
        
        
        
def data():
    sess = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!VerySecure1'), verify=False)
    session_id = sess.json()['value']

    result = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/vm",
    #result = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/vm/vm-5023/guest/identity",
    headers={"vmware-api-session-id": session_id }, cookies={}, verify=False )
    
    results = result.json()
    print (results)


app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
