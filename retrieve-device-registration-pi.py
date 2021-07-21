# https://support.remote.it/hc/en-us/articles/360016428732-Retrieve-Rasperry-Pi-Device-Details
#!/usr/bin/env python
# get_device_info.py
# retrieves hwid,regkey,and bulk id code of device and sends to status columns.
# only works with connectd since weavedconnectd doesn't support bulk reg

import os
import sys
import subprocess

#print output to log
sys.stdout = open('pyscriptlog.txt', 'w')
print(sys.argv[1:])

#necessary for utilities
finalize_job = "Job Complete"
clear = " "
task_id = sys.argv[1]
api = sys.argv[2]
task_notifier = "/usr/bin/connectd_task_notify"
columns = ['a','b','c','d','e']

#clear status columns
for column in columns:
    subprocess.Popen([task_notifier, column, task_id, api, clear]).wait()

#read file containing information we want
ps = subprocess.Popen(["connectd_control", "show"], stdout=subprocess.PIPE)
output = ps.communicate()[0]

#send info status columns
for line in output.split('\n'):
    if "Hardware ID" in line:
        hardware_id = line
        print("found hardware id:")
        print(hardware_id)
        subprocess.Popen([task_notifier, "a", task_id, api, hardware_id]).wait()

    elif "Registration key" in line:
        reg_key = line
        print("found reg key:")
        print(reg_key)
        subprocess.Popen([task_notifier, "b", task_id, api, reg_key]).wait()

    elif "Bulk ID Code" in line :
        bulk_id = line
        print("found bulk:")
        print(bulk_id)
        subprocess.Popen([task_notifier, "c", task_id, api, bulk_id]).wait()     

#tell connectd job is done
subprocess.Popen([task_notifier, "1", task_id, api, finalize_job]).wait()
