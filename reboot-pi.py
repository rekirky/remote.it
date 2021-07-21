# https://support.remote.it/hc/en-us/articles/360016428732-Retrieve-Rasperry-Pi-Device-Details
#!/usr/bin/env python
# reboot_pi.py

import os
import sys
import subprocess

#output to log
sys.stdout = open('/etc/pyscriptlog.txt', 'w')
print(sys.argv[1:])

#check connectd installer package
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

#necessary for utilities
clear = " "
finalize_job = "Job Complete"
task_id = sys.argv[1]
api = sys.argv[2]
task_notifier = check_connectd()
columns = ['a','b','c','d','e']

print(task_id)
#clear status columns
for column in columns:
    print(task_id)
    subprocess.Popen([task_notifier, column, task_id, api, clear]).wait()

#create python script that tells connectd job is done and sends message to user then deletes itself
with open(os.path.join("/etc", "boot.py"), "w+") as boot_python_script:
    boot_python_script.write("#!/usr/bin/env python\n")
    boot_python_script.write("import os\n")
    boot_python_script.write("import subprocess\n")
    boot_python_script.write('subprocess.Popen(["{}", "a", "{}", "{}", "Pi Rebooted!"]).wait()\n'.format(task_notifier, task_id, api))
    boot_python_script.write('subprocess.Popen(["{}", "1", "{}", "{}", "{}"]).wait()\n'.format(task_notifier, task_id, api, finalize_job))
    boot_python_script.write('os.remove(__file__)\n')

#write lines to rc.local which will run at startup 
with open("/etc/rc.local", "w+") as boot_shell_script:
    boot_shell_script.write('#!/bin/sh -e\n')
    boot_shell_script.write('sleep 60\n')
    boot_shell_script.write('sudo python /etc/boot.py &\n')
    boot_shell_script.write('exit 0')

#set permissions to boot.py
subprocess.Popen(["sudo", "chmod", "+x", "/etc/boot.py"]).wait()

#reboot device
subprocess.Popen([task_notifier, "a", task_id, api, "Rebooting Pi..."]).wait()
subprocess.Popen(["sudo", "reboot", "now"]).wait()