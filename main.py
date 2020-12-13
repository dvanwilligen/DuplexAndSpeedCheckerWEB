from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = { 'main' : 'sqlite:///hosts.db', 'auth' : 'sqlite:///auth.db' }

db = SQLAlchemy(app)




class HostDB(db.Model):
    __bind_key__ = 'main'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(200), nullable=False)
    devicetype = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, nullable=False)

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
        #return '<id %r>,<nickname %r >, <devicetype %r>, <username %r>, <password %r>, <secret %r>' % ( self.id, self.nickname, self.devicetype, self.username, self.password, self.secret)
        return '%r,%r,%r,%r,%r' % ( self.id, self.nickname, self.username, self.password, self.secret)
        #return '<Nickname %r' % self.id

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

        print(host_to_add)
        print(devicetype_to_add)
        print(port_to_add)

        db_push_host = (HostDB(hostname=host_to_add, devicetype=devicetype_to_add, port=port_to_add))
        print(db_push_host)
        try:
            db.session.add(db_push_host)
            db.session.commit()
            return redirect('/hosts/')
        except Exception as e:
            return str(e)

    else:
        hosts = HostDB.query.order_by(HostDB.id).all()
        return render_template('hosts.html', hosts=hosts)


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
