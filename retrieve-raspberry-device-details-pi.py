#https://support.remote.it/hc/en-us/articles/360016428732-Retrieve-Rasperry-Pi-Device-Details
#!/usr/bin/env python
# get_pi_status.py
# remote.it sample script
# retrieves information about the Raspberry Pi device and displays info in status columns A through E

import os
import sys
import subprocess
import platform
from datetime import datetime, timedelta

#print output to log
sys.stdout = open('pyscriptlog.txt', 'w')
print(sys.argv[1:])

#check connectd package
def check_connectd():
    if(os.path.isfile("/usr/bin/connectd_task_notify") and os.path.isfile("/usr/bin/task_notify.sh")):
        print("target device running both connectd and weavedconnectd")
        return("/usr/bin/connectd_task_notify")

    elif (os.path.isfile("/usr/bin/connectd_task_notify")):
        print("target device running connectd")
        return("/usr/bin/connectd_task_notify")

    elif(os.path.isfile("/usr/bin/task_notify.sh")):
        print("target device running weavedconnectd")
        return("/usr/bin/task_notify.sh")

    else:
        print("target device has neither...how is that possible?")
        exit()

#retrieve and convert uptime to days/hours/minutes
def get_uptime():
    with open('/proc/uptime', 'r') as raw_uptime:
        parsed_uptime = raw_uptime.readline().split()

    total_seconds = float(parsed_uptime[0])
    delta = timedelta(seconds=total_seconds)
    days = delta.days
    rem_seconds = delta.seconds
    dte = datetime(2018, 1, 1, 0, 0) + timedelta(seconds=rem_seconds)
    return '{} days, {}'.format(days, dte.strftime('%H hours, %M minutes'))

#retrieve list of connectd services running on the device and count how many there are
def count_services():
    global count
    count = 0

    ps = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE)
    output = ps.communicate()[0]

    for line in output.split('\n'):
        if ".sh" in check_connectd(): 
            count += line.count('weaved/services')
        else:
            count += line.count('connectd/services')
    
    return(str(count))

#retrieve free memory in kB
def get_free_mem():
    with open('/proc/meminfo','r') as raw_meminfo:
        mem_info = raw_meminfo.readlines()
        
    return mem_info[1]

#retrieve connectd package version
def get_oem_ver():
    if ".sh" in check_connectd():
        with open('/usr/bin/weavedlibrary', 'r') as contents:
            for line in contents:
                if "LIBVERSION=" in line:
                    return("weavedconnectd" + line)
    else:
        with open('/usr/bin/connectd_library', 'r') as contents:
            for line in contents:
                if "LIBVERSION=" in line:
                    return("connectd" + line)

#necessary for utilities
finalize_job = "Job Complete"
clear = " "
task_id = sys.argv[1]
api = sys.argv[2]
task_notifier = check_connectd()
columns = ['a','b','c','d','e']

#information we are retrieving
os_type = "OS: " + platform.uname()[0] + platform.uname()[2]
oem_ver = get_oem_ver()
uptime = "Uptime: " + get_uptime()
num_services ="Services: " + count_services()
free_memory = get_free_mem()
info_list = [os_type, oem_ver, uptime, num_services, free_memory]

#clear status columns
for column in columns:
    subprocess.Popen([task_notifier, column, task_id, api, clear]).wait()

#populate status columns
for item in zip(columns, info_list):
    subprocess.Popen([task_notifier, item[0], task_id, api, item[1]]).wait()

#tell connectd job is done
subprocess.Popen([task_notifier, "1", task_id, api, finalize_job]).wait()
