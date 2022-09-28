#from transfer import Connection
#import pexpect 
#
#
#
#
#def main():
#    """Little test when called ."""
#    # Set these to your own details.
#    #myssh = Connection(host='accsol101.zeu.alcatel-lucent.com',username='ababdell', password='Nokia@675' )#private_key = 'C:/users/ababdell/desktop/test_transfer/id_rsa')
#    #myssh = Connection(host='135.117.130.8',username='serw3ou', private_key = 'C:/users/ababdell/desktop/test_transfer/id_rsa') # password='ghostsrv') #
#    myssh = Connection(host='139.54.203.65',username='FNuser', password='FNlabuser2022?' )
#    #myssh.put('mypass')
#    #myssh.put('transfer.py')
#    #myssh.put('test.py')
#     
#    x = myssh.execute(command= "ifconfig") 
#    #x = myssh.execute(command= "rsync -pavz  /home/serw3ou/sendpass ababdell@accsol101.zeu.alcatel-lucent.com:/home/ababdell  ") 
#    #child = pexpect.spawn(mycommand)
#    #child.expect('password:')
#    #child.sendline(PASS)
#    #child.expect(pexpect.EOF)
#    print (x)
#       
#
#    myssh.close()
#
## start the ball rolling.
#if __name__ == "__main__":
#    main()
    
#with open('C:/Users/ababdell/Downloads/QueryResult.xls',"r") as LO :
# k = LO.read.decode('utf-8', 'ignore')
# print(k)

out= open('listout1','w')

with open('179.txt','r') as ne:
   for x in ne: 
    with open('178.txt','r') as crid:
     for line in crid:
       if x not in line:
        y = line
        print(line.strip())
        out.write(y)