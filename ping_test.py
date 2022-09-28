import paramiko


hostname = "tmwtlx91"
username = "ghostsrv"
password = "ghostsrv"

client = paramiko.SSHClient()
# add to known hosts
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
 client.connect(hostname=hostname, username=username, password=password)
except:
   print("[!] Cannot connect to the SSH Server")
       
stdin, stdout, stderr = client.exec_command('ping -c 1 gclpcfs6')
if stderr:
  print(stderr)
 
else:
   print(stdout)
