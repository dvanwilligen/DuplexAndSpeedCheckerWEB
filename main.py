from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = { 'main' : 'sqlite:///hosts.db', 'auth' : 'sqlite:///auth.db', 'setup' : 'sqlite:///setup.db' }

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

class SetupDB(db.Model):
    __bind_key__ = 'setup'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '%r,%r,%r' % ( self.id, self.hostname, self.nickname)

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
        Setup = SetupDB.query.order_by(SetupDB.id).all()
        return render_template('setup.html', authdetails=AuthDetails, hosts=hosts, setup=Setup)


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
