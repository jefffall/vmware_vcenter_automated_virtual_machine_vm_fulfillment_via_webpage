import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# https://vdc-download.vmware.com/vmwb-repository/dcr-public/1cd28284-3b72-4885-9e31-d1c6d9e26686/71ef7304-a6c9-43b3-a3cd-868b2c236c81/doc/operations/com/vmware/vcenter/vm.list-operation.html

sess = requests.post("https://vcenter.jeffreyfall.com/rest/com/vmware/cis/session", auth=('administrator@vsphere.local', '!VerySecure1'), verify=False)
session_id = sess.json()['value']

resp = requests.get("https://vcenter.jeffreyfall.com/rest/vcenter/vm", verify=False, headers={
    "vmware-api-session-id": session_id
})
print(u"resp.text = %s" % str(resp.text))