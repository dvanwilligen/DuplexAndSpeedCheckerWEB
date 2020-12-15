from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from speedandduplex_cisco import speedandduplex_cisco

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = { 'main' : 'sqlite:///hosts.db', 'auth' : 'sqlite:///auth.db' }

db = SQLAlchemy(app)




class HostDB(db.Model):
    __bind_key__ = 'main'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(200), nullable=False)
    devicetype = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    authpair = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '%r,%r,%r,%r' % (self.id, self.hostname, self.devicetype, self.port)

class AuthDB(db.Model):
    __bind_key__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    secret = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '%r,%r,%r,%r,%r' % ( self.id, self.nickname, self.username, self.password, self.secret)

class ResultsDB(db.Model):
    __bind_key__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    resulttime = db.Column(db.String(200))
    hostname = db.Column(db.String(200))
    port = db.Column(db.String(200))
    name = db.Column(db.String(200))
    status = db.Column(db.String(200))
    vlan = db.Column(db.String(20))
    speed = db.Column(db.String(200))
    duplex = db.Column(db.String(200))
    type = db.Column(db.String(200))

    def __repr__(self):
        return '%r,%r,%r,%r,%r' % ( self.id, self.nickname, self.username, self.password, self.secret)





@app.route('/', methods=['POST', 'GET'])
def index_main():
    return render_template('index.html')

@app.route('/authentication/', methods=['POST', 'GET'])
def index_authentication():
    if request.method == 'POST':
        nick_to_add = request.form['nickname']
        username_to_add = request.form['username']
        password_to_add = request.form['password']
        secret_to_add = request.form['secret']

        db_push = (AuthDB(nickname=nick_to_add, username=username_to_add, password=password_to_add, secret=secret_to_add))

        try:
            db.session.add(db_push)
            db.session.commit()

            return redirect('/authentication/')
        except Exception as e:
            return str(e)
    else:
        #AuthDetails = AuthDB.query.order_by(AuthDB.id).all()
        AuthDetails = AuthDB.query.order_by(AuthDB.id).all()
    return render_template('authentication.html', authdetails=AuthDetails)



@app.route('/hosts/', methods=['POST', 'GET'])
def index_hosts():
    if request.method == 'POST':
        host_to_add = request.form['newhost']
        devicetype_to_add = request.form['devicetype']
        port_to_add = int(request.form['port'])

        db_push_host = (HostDB(hostname=host_to_add, devicetype=devicetype_to_add, port=port_to_add))
        try:
            db.session.add(db_push_host)
            db.session.commit()
            return redirect('/hosts/')
        except Exception as e:
            return str(e)

    else:
        hosts = HostDB.query.order_by(HostDB.id).all()
        return render_template('hosts.html', hosts=hosts)

@app.route('/setup/', methods=['POST', 'GET'])
def setup():
    if request.method == 'POST':
        setuparray = []
        setupcount = 1
        for each in HostDB.query.all():
            setuparray.append(str(request.form[str(setupcount)]))
            setupcount += 1
        try:
            for x in range((len(setuparray))):
                auth_to_add = HostDB.query.filter_by(id=x+1).first()
                auth_to_add.authpair = setuparray[x]
            db.session.commit()
            return redirect('/setup')
        except Exception as e:
            return str(e)

        return redirect('/setup/')
    else:
        hosts = HostDB.query.order_by(HostDB.id).all()
        AuthDetails = AuthDB.query.order_by(AuthDB.id).all()
        return render_template('setup.html', authdetails=AuthDetails, hosts=hosts)


@app.route('/launch/', methods= ['POST', 'GET'])
def launch():
    if request.method == 'POST':
        Devices_to_check = HostDB.query.order_by(HostDB.id).all()
        for iteration, each in enumerate(Devices_to_check):
            CurrentDevice = HostDB.query.filter_by(id=iteration).first
            hostname = CurrentDevice.hostname
            devicetype = CurrentDevice.devicetype
            port = CurrentDevice.port
            authpair = CurrentDevice.authpair

            if devicetype == 'cisco_ios':
                credStage = AuthDB.query.filter_by(nickname=authpair).first()
                username = credStage.username
                password = credStage.password
                secret = credStage.secret
                output1 = speedandduplex_cisco(hostname, username, password, secret, port)
                now = datetime.now()
                output1 = output1.splitlines()
                FinalOutput = []
                for line in output1:
                    line = line.split()
                    FinalOutput.append(line)
                for each in FinalOutput:
                    if each[0] == 'Port':
                        pass
                    else:
                        db_push = (ResultsDB(resulttime=now, hostname=hostname, port=each[0], name=each[1],status=each[2], vlan=each[3], duplex=each[4], speed=each[5], type=each[6])
                        db.session.add(db_push)
                        db.session.commit
            else:
                print("device type not supported yet")

    else:
        pass
    return render_template('/')



@app.route('/auth_delete/<int:id>')
def delete_auth(id):
    auth_to_delete = AuthDB.query.get_or_404(id)

    try:
        db.session.delete(auth_to_delete)
        db.session.commit()
        return redirect('/authentication/')
    except Exception as e:
        return str(e)

@app.route('/host_delete/<int:id>')
def delete_host(id):
    host_to_delete = HostDB.query.get_or_404(id)

    try:
        db.session.delete(host_to_delete)
        db.session.commit()
        return redirect('/hosts/')
    except Exception as e:
        return str(e)








if __name__ == "__main__":
    app.run(debug=True)
