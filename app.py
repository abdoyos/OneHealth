from flask import Flask, render_template,redirect, flash, url_for, request,session, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from transfer import Connection
from flask_sqlalchemy  import SQLAlchemy
import mysql.connector
import paramiko
import datetime
import json
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql+pymysql://root@localhost:3306/schedule_doc'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

conn = mysql.connector.connect(user='root',  host='localhost', database='schedule_doc',pool_name='batman',
    pool_size = 3)
cur = conn.cursor()

hostname = "tmwtlx91"
username = "ghostsrv"
password = "ghostsrv"




@login_manager.user_loader
def load_user(user_id):
    return accounts.query.get(int(user_id))

######################################

class accounts(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(50))
    user_name = db.Column(db.String(100), unique=True)
    passwd = db.Column(db.String(100))
    name = db.Column(db.String(100))
    Speciality = db.Column(db.String(100))
    clinic_id = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    Is_active = db.Column(db.Integer)

    def is_active(self):
       """True, as all users are active."""
       return True

    def is_authenticated(self):
       """Return True if the user is authenticated."""
       return self.authenticated

    def is_anonymous(self):
       """False, as anonymous users aren't supported."""
       return False

######################################


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5000)
    session.modified = True
    user = current_user

######################################
@app.route('/', methods=['GET','POST'])
def index():
     return  redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == "POST":
        passwords = request.form.get('Pass')
        email = request.form.get('email')
        user = accounts.query.filter_by(user_name=email).first()
        next_page = request.args.get("next")

        if user:
           if user.passwd != passwords:
              flash('Wrong Password, Please verify!','error')
              return  redirect(url_for('login'))
            
           else:
               login_user(user,remember=False)
               next_page = request.args.get("next")  
               if next_page:
                    return redirect(next_page)
               else:
                    return redirect(url_for('O1'))
        else:
           flash('Invalid username or password','error')
           return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/Forgetpass', methods=['GET','POST'])
def Fogetpass():
      
   if request.method == "POST":
       flash('An email will be sent to you','success')
       return redirect(url_for('login'))

   return render_template('forgot-password.html')

@app.route('/LabSupport/Monitoring/Timisoara', methods=['GET','POST'])
@login_required
def Timis():


     cur.execute("select host,comment, case when access = 1 then 'RSH' else 'SSH' end as access,type,case when just_ping =1 then 'Yes' else 'No' end as jus_ping,case when timisoara.ignore =1 then 'Yes' else 'No' end as jus_pingf, case when aut_fail =1 then 'Yes' else 'No' end as aut_fail, shutdown from timisoara;")
     data = cur.fetchall()
     if request.method == "POST":

         cur.execute("select host from timisoara;")
         hosts = cur.fetchall()
         myssh = Connection(host=hostname, username=username,  password=password)
         with open("ping_results.txt", "a") as myfile:
              for x in hosts:
                z = myssh.execute(command='ping -c 1 %s' %(x))             
                if "unknown" in z[0]:
                    myfile.write("%s: the host unknown \n" %(x))
                    myfile.write("\n")
                elif "Unreachable" in z[1]:
                    myfile.write("%s: Unreachable ping is KO & is down!" %(x))
                    myfile.write("\n")
                elif "100%" in z[3]:
                    myfile.write("%s: ping is KO & is down!" %(x))
                    myfile.write("\n")
                else:
                    myfile.write("%s: ping is OK & is up!" %(x) )
                    myfile.write("\n")
              
              flash('Sucess Ping all Machine','success')
              return redirect(url_for('Timis'))

         #flash('Sucess Ping all Machine','success')
         #return redirect(url_for('Timis'))
                   
            #return redirect(url_for('Timis'))
         #if stderr:
          #   flash(stderr.readlines(),'error')
           #  return redirect(url_for('Timis'))
         #else:
          #  flash(stdout.readlines()[0],'success')
           # return redirect(url_for('Timis'))

     return render_template('Timisoara.html', data=data)

@app.route('/LabSupport/Monitoring/SHALL', methods=['GET','POST'])
@login_required
def SHALL():

     if request.method == "POST":

         cur.execute("select host from timisoara;")
         x = "accsol106"
         host="accsol106"
         myssh = Connection(host=hostname, username=username, password=password)
         with open("SSH.txt", "a") as myfile:
                Type = myssh.execute(command= " ssh {} -l ghostsrv uname".format(host))
                z = myssh.execute(command='ping -c 1 %s' %(x))             
                print(str(z))
                
    
     return redirect(url_for('Timis'))
              


@app.route('/LabSupport/Monitoring/Timisoara/Threshold', methods=['GET','POST'])
@login_required
def Timis_Threshold():
     cur.execute("select  *  from timisoara_threshold;")
     data = cur.fetchall()
     return render_template('Timisoara_Threshold.html', data=data)

@app.route('/LabSupport/Monitoring/Timisoara/shutdownWS', methods=['GET','POST'])
@login_required
def SHWS():


     if request.method == "POST":
         passwd = request.form.get('pass')
         host = request.form.get('shs')
         rcode = request.form.get('rcode')
         if passwd == "1":
               Type = os.system("ssh {} -l ghostsrv uname".format(host))
               try:
                  child = pexpect.popen_spawn.PopenSpawn("ssh {} -l ghostsrv uname".format(host))
                  a = child.expect(['password:', 'The authenticity of host'], timeout=300, async=True)
                  if a == 0:
                     child.sendline('123456789')
                     print('this ip has exists in know_host files!')
                  if a == 1:
                     print('this ip will be added to know_host files!')
                     child.sendline('yes')
                     child.expect('password:')
                     child.sendline('123456789')
                     # send test
                     child.sendline("df -h")
                     child.interact()
               except pexpect.EOF:
                    traceback.print_exc()
               if "key" in Type[0]:
                  child = popen_spawn.PopenSpawn(Type) #'ssh {} -l ghostsrv uname'.format(host))
                  child.wait()
                  #child.expect('password:')
                  #child.sendline(password)
                  #child.expect(pexpect.EOF)
                  flash(child.before,'success')
                  return redirect(url_for('Timis'))
               else:    
                 version = myssh.execute(command= "ssh {} -l ghostsrv uname -v".format(host))
                 release = myssh.execute(command= "ssh {} -l ghostsrv uname -r".format(host))
               #if Type[0] == "AIX":
               #    myssh.execute(command= " ssh {} -l ghostsrv /usr/sbin/shutdown -F -h now 2>&1".format(host))
               #elif Type[0] == "HP-UX":
               #    myssh.execute(command= " ssh {} -l ghostsrv /usr/sbin/shutdown -y -h now 2>&1".format(host))
               #elif Type[0] == "SunOS":
               #    myssh.execute(command= " ssh {} -l ghostsrv /usr/sbin/shutdown -y -i5 -g0 2>&1".format(host))
               #elif Type[0] == "Linux":
               #    myssh.execute(command= " ssh {} -l ghostsrv /usr/sbin/shutdown -h now 2>&1".format(host))
               #else:
               #    flash('Ignoring: OS unknown for $machine!! ','error')
               flash('Host:'+ host +' '+'machine:'+ Type[0] +' '+ 'Version:' + version[0] +' '+ 'Release:' + release[0],'success')
               return redirect(url_for('Timis'))
            
     
          #except:
           #   flash('Connection failed to Host: %s, please try again' %host,'error')
            #  return redirect(url_for('Timis'))
         else:
             flash('Wrong password, please try again %s' %host,'error')
             return redirect(url_for('Timis'))

@app.route('/LabSupport/Monitoring/Lannion/Threshold', methods=['GET','POST'])
@login_required
def Lan_Threshold():
     cur.execute("select  *  from timisoara_threshold;")
     data = cur.fetchall()
     return render_template('Lan_Threshold.html', data=[])

@app.route('/LabSupport/Monitoring/Stuttgart/Threshold', methods=['GET','POST'])
@login_required
def Stutt_Threshold():
     cur.execute("select  *  from timisoara_threshold;")
     data = cur.fetchall()
     return render_template('Stutt_Threshold.html', data=[])

@app.route('/LabSupport/Monitoring/Lannion')
@login_required
def Lan():
    return render_template('Lannion.html')

@app.route('/LabSupport/Monitoring/Stuttgart')
@login_required
def Stutt():
    return render_template('Stuttgart.html')

@app.route('/LabSupport/Monitoring/Daily')
@login_required
def daily():
    return render_template('index.html')

@app.route('/LabSupport/knowledgebase/Doc')
@login_required
def Knowledgebase():
    return render_template('Knowledgebase.html')



@app.route('/LabSupport/Monitoring/Opale/tickets')
@login_required
def OPALE_ticket_how():
    return render_template('opale_tickets.html')

@app.route('/LabSupport/Monitoring/HCL/Tickets', methods=['GET','POST'])
@login_required
def OPALE():
    
    cur.execute("select  *  from OPALE;")
    data = cur.fetchall()
    Title="HCL Tickets"
    if request.method == "POST":
       HCL = request.form.get('HCL')
       Cdate = request.form.get('Cdate')
       Status = request.form.get('Status')
       Escalated = request.form.get('Escalated')
       #Rdate = request.form.get('Rdate')
       update = "Insert into OPALE(Ticket_ID,creation_date,Status,Escelated) values(%s, %s, %s, %s)"
       parameters= (HCL,Cdate,Status,Escalated)
       cur.execute(update,parameters)
       conn.commit()
       flash('The Ticket have been added successfully','success')
       return redirect(url_for('OPALE'))

    return render_template('OPALE.html', data=data, Title=Title)



@app.route('/LabSupport/Monitoring/Backup/Details', methods=['GET','POST'])
@login_required
def Backup_d():
    
    #cur.execute("select  *  from backups_details;")
    #data = cur.fetchall()
    Title="Backup Details"
    if request.method == "POST":
       docid = request.form.get('Docname')
       From = request.form.get('From')
       To = request.form.get('To')
       Room = request.form.get('Room')
       #Rdate = request.form.get('Rdate')
       #update = "Insert into backups_details(hostname,IP,Description,OS,Virtualize,VM_Hosts,Backup_Hosts,Backup_Location_1,Backup_location_2) values(%s, %s, %s, %s,%s, %s, %s, %s,%s)"
       #parameters= (hostname,ipad,desc,OS,virt,vmhost,bkphost,bkploc1,bkploc2)
       #cur.execute(update,parameters)
       #conn.commit()
       flash('New  record have been added successfully','success')
       return redirect(url_for('Backup_d'))

    return render_template('backups_details.html', Title=Title)#, data=data, Title=Title)



@app.route('/onheleath/Pediatrics/schedule/creationO1', methods=['GET','POST'])
@login_required
def schedule_create_o1():
    
    if request.method == "POST":
    
       docid = request.form.get('Docname')
       From = request.form.get('From')
       To = request.form.get('To')
       Room = request.form.get('room')
       comm = request.form.get('comm')
       s_from = datetime.datetime.strptime(From, '%Y-%m-%dT%H:%M')
       s_from_day = s_from.strftime("%A")
       s_to = datetime.datetime.strptime(To, '%Y-%m-%dT%H:%M')
       s_to_time = s_to.time()
       s_from_time = s_from.time()
       s_from_date = s_from.date()
       clinic_id = 1
       update = "Insert into schedule(clinic_id,doc_id,Date,Day,start_time,end_time,room,comments) values(%s, %s, %s, %s,%s, %s, %s, %s)"
       parameters= (clinic_id,int(docid),s_from_date,s_from_day,s_from_time,s_to_time,Room,comm)
       cur.execute(update,parameters)
       conn.commit()
       flash('New  record have been added successfully','success')
       return redirect(url_for('O1'))

   
@app.route('/onheleath/Pediatrics/schedule/O1_Center', methods=['GET','POST'])
@login_required
def O1():

      cur.execute("SELECT id,name FROM accounts where clinic_id=1 ;")
      data1 = cur.fetchall()
      cur.execute("SELECT user_code FROM accounts where clinic_id=1 ;")
      data2= cur.fetchall()
      cur.execute("SELECT b.name, b.user_code, b.Speciality, a.Date, a.Day, a.start_time, a.end_time, a.room from schedule a inner join accounts b on a.doc_id = b.id where b.clinic_id=1")
      schedule = cur.fetchall()
      Title="Schedule"
      if request.method == "POST":
            import socket
         #try:
            vmhost = request.form.get('vmhost')
            bkphost = request.form.get('bkphost')
            holo = request.form.get('holo')
            bkptype = request.form.get('bkptype')
            loc1 = request.form.get('loc1')
            loc2 = request.form.get('loc2')
            bkpserver = "tmdepot"
            #ip_address = socket.gethostbyname(vmhost)
            myssh = Connection(host=hostname, username=username, password=password)
            if bkptype=="Proxmox":
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
   
            elif bkptype=="ESXi":
                version = myssh.execute(command= 'ssh {0} -l ghostsrv  /bin/sh -c "cd /home/ghostsrv; ./esxidump.bash {1} {2} {3}" >> ESXI_backup_log.log'.format(bkpserver,vmhost,loc1,loc2))
                
            else:
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
         
            
            flash('Host:'+ str(vmhost)+' '+ 'Version:' + str(version[0]).split("'")[1].replace('"',''),'success')
            #flash('IP address is'+' '+ ip_address +'','success')
            return redirect(url_for('create_backup'))
         #except:
          #    flash('The Host'+': '+ vmhost +' '+'is not available','error')
           #   return redirect(url_for('create_backup'))

      return render_template('O1.html',data1=data1,data2=data2,schedule=schedule,Title=Title)

@app.route('/onheleath/Pediatrics/schedule/Korba_Center', methods=['GET','POST'])
@login_required
def Korba():

      #cur.execute("SELECT host FROM timisoara ;")
      #data1 = cur.fetchall()
      Title="Schedule"
      if request.method == "POST":
            import socket
         #try:
            vmhost = request.form.get('vmhost')
            bkphost = request.form.get('bkphost')
            holo = request.form.get('holo')
            bkptype = request.form.get('bkptype')
            loc1 = request.form.get('loc1')
            loc2 = request.form.get('loc2')
            bkpserver = "tmdepot"
            #ip_address = socket.gethostbyname(vmhost)
            myssh = Connection(host=hostname, username=username, password=password)
            if bkptype=="Proxmox":
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
   
            elif bkptype=="ESXi":
                version = myssh.execute(command= 'ssh {0} -l ghostsrv  /bin/sh -c "cd /home/ghostsrv; ./esxidump.bash {1} {2} {3}" >> ESXI_backup_log.log'.format(bkpserver,vmhost,loc1,loc2))
                
            else:
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
         
            
            flash('Host:'+ str(vmhost)+' '+ 'Version:' + str(version[0]).split("'")[1].replace('"',''),'success')
            #flash('IP address is'+' '+ ip_address +'','success')
            return redirect(url_for('create_backup'))
         #except:
          #    flash('The Host'+': '+ vmhost +' '+'is not available','error')
           #   return redirect(url_for('create_backup'))

      return render_template('Korba.html', Title=Title)

@app.route('/onheleath/Pediatrics/schedule/Park_clinic', methods=['GET','POST'])
@login_required
def Park():

      #cur.execute("SELECT host FROM timisoara ;")
      #data1 = cur.fetchall()
      Title="Schedule"
      if request.method == "POST":
            import socket
         #try:
            vmhost = request.form.get('vmhost')
            bkphost = request.form.get('bkphost')
            holo = request.form.get('holo')
            bkptype = request.form.get('bkptype')
            loc1 = request.form.get('loc1')
            loc2 = request.form.get('loc2')
            bkpserver = "tmdepot"
            #ip_address = socket.gethostbyname(vmhost)
            myssh = Connection(host=hostname, username=username, password=password)
            if bkptype=="Proxmox":
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
   
            elif bkptype=="ESXi":
                version = myssh.execute(command= 'ssh {0} -l ghostsrv  /bin/sh -c "cd /home/ghostsrv; ./esxidump.bash {1} {2} {3}" >> ESXI_backup_log.log'.format(bkpserver,vmhost,loc1,loc2))
                
            else:
                version = myssh.execute(command= "ssh {0} -l ghostsrv cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(bkpserver,vmhost,loc1,loc2))
         
            
            flash('Host:'+ str(vmhost)+' '+ 'Version:' + str(version[0]).split("'")[1].replace('"',''),'success')
            #flash('IP address is'+' '+ ip_address +'','success')
            return redirect(url_for('create_backup'))
         #except:
          #    flash('The Host'+': '+ vmhost +' '+'is not available','error')
           #   return redirect(url_for('create_backup'))

      return render_template('Park.html', Title=Title)


@app.route('/LabSupport/create_backup/<host>/', methods=['GET','POST'])
@login_required
def get_OS(host):

     myssh = Connection(host=hostname, username=username, password=password)
     version = myssh.execute(command= "ssh {} -l ghostsrv  cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2".format(host))          
     if len(version) > 2 :
       data = str(str(version).split('"')[1])
     else:
          data = "The VM is not available"

     response = make_response(json.dumps(data))
     response.content_type = 'application/json'
     return response

@app.route('/LabSupport/Monitoring/UPDATE/Tickets', methods=['GET','POST'])
@login_required
def OPALE_UPDATE():
    
    cur.execute("select  *  from OPALE;")
    data = cur.fetchall()
    if request.method == "POST":
       delo = request.form.get('upd')
       person = request.form.get('person')
       Status = request.form.get('Status1')
       Escalated = request.form.get('Escalated1')
       Rdate = request.form.get('Rdate')
       update = "update OPALE set Status=%s, Escelated=%s, Contact_person=%s, resolution_date=%s where id =%s" 
       parameters= (Status,Escalated,person,Rdate,delo)
       cur.execute(update,parameters)
       conn.commit()
       flash('The Ticket have been Updated successfully','success')
       return redirect(url_for('OPALE'))


@app.route('/LabSupport/Monitoring/Update', methods=['GET','POST'])
@login_required
def Updates():

    if request.method == "POST":
       host = request.form.get('upd')
       com = request.form.get('com')
       AC = request.form.get('AC')
       WS = request.form.get('WS')
       JP = request.form.get('JP')
       IG = request.form.get('IG')
       FL = request.form.get('FL')
       SH = request.form.get('SH')
       update = "update timisoara set comment=%s, access=%s, type=%s, just_ping=%s, timisoara.ignore=%s, aut_fail=%s, del='N', shutdown=%s  where host= %s"
       parameters= (com,AC,WS,JP,IG,FL,SH,host)
       cur.execute(update,parameters)
       conn.commit()
       flash('The host have been Updated successfully','success')
       return redirect(url_for('Timis'))

@app.route('/LabSupport/Monitoring/Insert', methods=['GET','POST'])
@login_required
def add():

    if request.method == "POST":
       host = request.form.get('upd')
       com = request.form.get('com')
       AC = request.form.get('AC')
       WS = request.form.get('WS')
       JP = request.form.get('JP')
       IG = request.form.get('IG')
       FL = request.form.get('FL')
       SH = request.form.get('SH')
       update = "Insert into timisoara(host,comment,access,type,just_ping,timisoara.ignore,aut_fail,del,shutdown) values(%s, %s, %s, %s, %s, %s, %s,'N', %s)"
       parameters= (host,com,AC,WS,JP,IG,FL,SH)
       cur.execute(update,parameters)
       conn.commit()
       flash('The host have been Added successfully','success')
       return redirect(url_for('Timis'))

@app.route('/LabSupport/Monitoring/delete', methods=['GET','POST'])
@login_required
def delete():
     
    if request.method == "POST":
       hostname = request.form.get('del')
       cur.execute("update timisoara set del='Y' where host= %s ",(hostname,))
       flash('The host have been deleted successfully','success')
       return redirect(url_for('Timis'))

@app.route('/LabSupport/Monitoring/daily/Monitoring', methods=['GET','POST'])
@login_required
def DailyAudit():
     
     hostname = "tmwtlx91-temp"
     username = "ghostsrv"
     password = "ghostsrv" 
     if request.method == "POST":
        myssh = Connection(host=hostname, username="root", private_key = 'C:/users/ababdell/desktop/test_transfer/id_rsa') #password=password)
        if myssh:
            #myssh.put("audit")
            #myssh.execute(command="chmod 777 audit ")
            #myssh.execute(command="sed -i -e 's/\r$//' audit ")
            myssh.execute(command="./audit") 
            myssh.execute(command="screen -d") 
            #Command = myssh.execute(command="screen -S Audit ./home/ghostsrv/monitoring/audit_machines timisoara > /home/ghostsrv/monitoring/timisoara.log")
            #flash(Command2,'success')
            flash('The script executed successfully, An email will be sent shortly','success')
            return redirect(url_for('Timis'))
        else:
            flash('The Script executed successfully, email will be sent','success')
            return redirect(url_for('Timis'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/logoutinactive')
@login_required
def logoutinactive():
    logout_user()
    flash('You have logged out due to Inactivity', 'error')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port="5000")
 