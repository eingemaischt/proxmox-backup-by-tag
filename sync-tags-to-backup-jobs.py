from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()


proxmox = ProxmoxAPI(
    os.getenv('PXMX_HOST'), 
    port=os.getenv('PXMX_PORT'), 
    user=os.getenv('PXMX_USER'), 
    token_name=os.getenv('PXMX_TOKEN_NAME'), 
    token_value=os.getenv('PXMX_TOKEN_VALUE'), 
    verify_ssl=True
)

# enter tag names and corresponding backup job-ids here: 
#TODO: Make them configurable in an .env


pairs = [
    ('daily', 'backup-3b78cbf7-1234'),
    ('weekly', 'backup-cb98d2cc-5678'),
]


# first build one list per job with the vmids to fill in

jobstofill = {}

for (name, job) in pairs:
    jobstofill[job] = []


vms = proxmox.cluster.resources.get(type='vm')

for vm in vms:
    if 'tags' in vm:
        for (name, job) in pairs:
            if name in vm['tags']:
                jobstofill[job].append(str(vm['vmid']))
    
        #proxmox.nodes(item['node']).qemu(item['vmid']).config.put(tags=newtag)

backups = proxmox.cluster.backup.get()

for backupjob in backups:
    if backupjob['id'] in jobstofill:
        listvmids = backupjob['vmid'].split(',')
        
        for vmid in jobstofill[backupjob['id']]:
            if vmid not in listvmids:
                listvmids.append(vmid)
        for vmid in listvmids:
            if vmid not in jobstofill[backupjob['id']]:
                listvmids.remove(vmid)
        proxmox.cluster.backup(backupjob['id']).put(vmid=','.join(listvmids))
