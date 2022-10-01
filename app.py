from flask import Flask, render_template,redirect, flash, url_for, request,session, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from transfer import Connection
from flask_sqlalchemy  import SQLAlchemy
import mysql.connector
import paramiko
import datetime
import json
import os
import psycopg2

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
#app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql+pymysql://orqyNUUokU:zvFTE9hxaP@remotemysql.com:3306/orqyNUUokU'
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql+psycopg2://wkxgscyrnnjswy:a9d5fe2a0cd9712e62c3540648ee3ded183be1dab23f166484ce09b1aa015c34@ec2-52-211-37-76.eu-west-1.compute.amazonaws.com:5432/dca9mhfsklk6b2'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

conn = psycopg2.connect(user='wkxgscyrnnjswy', password='a9d5fe2a0cd9712e62c3540648ee3ded183be1dab23f166484ce09b1aa015c34', host='ec2-52-211-37-76.eu-west-1.compute.amazonaws.com', database='dca9mhfsklk6b2',port=5432,
    options="-c search_path=puplic,schedule")
cur = conn.cursor()

hostname = "tmwtlx91"
username = "ghostsrv"
password = "ghostsrv"




@login_manager.user_loader
def load_user(user_id):
    return accounts_new.query.get(int(user_id))

######################################

class accounts_new(UserMixin, db.Model):

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
        user = accounts_new.query.filter_by(user_name=email).first()
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
       update = 'Insert into public.schedule_new(clinic_id,doc_id,"Date","Day",start_time,end_time,room,comments) values(%s, %s, %s, %s,%s, %s, %s, %s)'
       parameters= (clinic_id,int(docid),s_from_date,s_from_day,s_from_time,s_to_time,Room,comm)
       cur.execute(update,parameters)
       conn.commit()
       flash('New  record have been added successfully','success')
       return redirect(url_for('O1'))

   
@app.route('/onheleath/Pediatrics/schedule/O1_Center', methods=['GET','POST'])
@login_required
def O1():

      cur.execute("SELECT id,name FROM public.accounts_new where clinic_id=1 ;")
      data1 = cur.fetchall()
      cur.execute("SELECT user_code FROM public.accounts_new where clinic_id=1 ;")
      data2= cur.fetchall()
      cur.execute('SELECT b.name, b.user_code, b."Speciality", a."Date", a."Day", a.start_time, a.end_time, a.room from public.schedule_new a inner join public.accounts_new b on a.doc_id = b.id where b.clinic_id=1')
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
    app.run(debug=True,port=5000)
 