import json
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, leave_room, join_room, send
import datetime
from sqlalchemy import or_,and_
s_date = datetime.datetime.now()


print("time is   --  ",s_date)
aa = [ ]
tie = ""
bb = []

sdate = str(s_date)

for x in sdate:
    
    aa.append(x)

gg = aa[0:16]

for i in gg:

    tie = tie + i




print(tie)

chat_app = Flask(__name__)
chat_app.secret_key = "abc8787"
chat_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
chat_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socket = SocketIO(chat_app)


db = SQLAlchemy(chat_app)


class users(db.Model):

    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    status = db.Column(db.String(100))

    def __ini__(self, username, email, password, status):
        self.username = username
        self.email = email
        self.password = password
        self.status = status


class chat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(300))
    to_id = db.Column(db.String(300))
    content = db.Column(db.String(300))
    room = db.Column(db.String(50))
    date = db.Column(db.String(300))
    count = db.Column(db.Integer)


    def __init__(self, from_id, to_id, content, room, date, count):
        self.from_id = from_id
        self.to_id = to_id
        self.content = content
        self.room = room
        self.date = date
        self.count = count


    def to_dict(self):
        data = {
            'id': self.id,
            'from_id': self.from_id,
            'to_id': self.to_id,
            'content': self.content,
            'room': self.room,
            'date': self.date,
            'count': self.count,
            'date': self.date
        }

        return data

online_user = set()

@chat_app.route('/')
def home():

    return render_template("home.html")


@chat_app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        u_name = users.query.filter_by(username=username).first()
        pass_word = users.query.filter_by(password=password).first()

        session['username'] = username

        u_name.status = "Online"
        db.session.commit()

        if u_name and pass_word:

            print(username, " - is authenticated!")

            return redirect(url_for('chat_list'))

        else:

            err = "please register first!!!"

            return render_template('login.html', err=err)

    elif "username" in session:

        print(session['username'], " - is authenticated!")

        return redirect(url_for('chat_list'))

    return render_template("login.html")


@chat_app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        re_password = request.form['re_password']
        email = request.form['email']
        session["username"] = username
        session['password'] = password
        session['email'] = email

        u_name = users.query.filter_by(username=username).first()

        if not u_name:

            if password == re_password:
                try:
                    usr = users(username=username,
                                password=password, email=email)

                    db.session.add(usr)
                    db.session.commit()

                    u_name = users.query.filter_by(username=username).first()

                    u_name.status = "Online"
                    db.session.commit()


                    return redirect(url_for('chat_list'))

                except:

                    print("auth registeration is failed some query issue!")
                    error_msg = "password not matching please re_enter!!!"

                    return render_template("register.html")

            else:
                error_msg = "password not matching please re_enter!!!"

                return render_template('register.html', err=error_msg)
        else:

            error_msg = "This username already exist try another one!!!"

            return render_template('register.html', err=error_msg)

    return render_template('register.html')


@chat_app.route('/chat_list', methods=['POST', 'GET'])
def chat_list():

    if request.method == "POST" and request.form['logout'] == 'logout':

        u_id = users.query.filter_by(username=session['username']).first()

        u_id.status = tie
        db.session.commit()

        session.pop("username", None)

        return redirect(url_for('home'))

    u_name = session['username']
    print("user :", u_name)


    usr = users.query.all()
        

    return render_template('chat_list.html', name=u_name, users=usr)



@socket.on('message')
def message_sender(data):
    print(data['content'])
    print(data['to_id'])



    session['to_id'] = data['to_id']

    if data['to_id'] and data['content']:

        try:

            chat_room = chat(from_id=session['username'], to_id=data['to_id'], content=data['content'], room=session['username'], date=tie, count=1)
            db.session.add(chat_room)
            db.session.commit()


            print("test : ",data['to_id'], " test2: ", data['content'])

            send({'to_id': data['to_id'], 'content': data['content']}, room=data['to_id'])
            send({'to_id': data['to_id'], 'content': data['content']}, room=session['username'])

            print("sucesfully submited")

            socket.emit("counter_update", {"user": session['username'], "count": 1})


        except:

            print("some error at creating time!!!")

    print('message recevied :', data)


@socket.on('sender')
def handle_massage(data):

    u_name = session['username']
    to_name = data['to_usr']

    session['to_id'] = data['to_usr']

    print(u_name, to_name)

    join_room(data['to_usr'])   



    try:

        count_msg = chat.query.filter_by(from_id=data['to_usr'], to_id=session['username']).all()

        if count_msg:

            for x in count_msg:
                x.count = 0
                db.session.commit()

            print("updated!!!!")

    except:
        print('some wrong in unsttenetd msg!!!')



    try:
        sender_history = chat.query.filter(chat.from_id.in_([u_name,to_name]),chat.to_id.in_([u_name,to_name])).order_by(chat.date).all()
        print('its succesfully fetched')

    except:
        print("some error at fetching time!!!")


    if data:
        s_h_data = [i.to_dict() for i in sender_history]
        
        emit('message_history',{'msg_history': s_h_data, 'username': session['username']})


@socket.on('count_up')
def count_update():
    
    user = users.query.all()

    arr = []

    for x in user:

        data = chat.query.filter_by(from_id=x.username, to_id=session['username'], count=1).count()
        
        arr.append({"username": x.username,'count': data})

    print("counter  - ",arr)

    emit("count_update", arr)


@socket.on('call_status')
def login_status():

    usr = users.query.all()

    data = []
    data.clear()

    for i in usr:
        if i.username:
            data.append({"username": i.username, "status": i.status})

    emit("status", data, broadcast=True)





if __name__ == '__main__':

    with chat_app.app_context():
        db.create_all()
        socket.run(chat_app, debug=True)
