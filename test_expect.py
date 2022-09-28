import traceback
from pexpect import pexpect.spawn


try:
    
    child = pexpect.spawn('ssh ghostsrv@gclelm75')
    a = child.expect(['password:', 'The authenticity of host'], timeout=300, async=True)
    if a == 0:
       child.sendline('ghostsrv')
       print('this ip has exists in know_host files!')
    if a == 1:
       print('this ip will be added to know_host files!')
       child.sendline('yes')
       child.expect('password:')
       child.sendline('ghostsrv')
       # send test
       child.sendline("df -h")
       child.interact()
except pexpect.EOF:
     traceback.print_exc()