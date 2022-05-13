import bcrypt
import os
import MongoDB
import hashlib
import random
import json
from flask_sock import Sock
from werkzeug.routing import BaseConverter
from flask import render_template, request, Flask, redirect,url_for


#
# class RegexConverter(BaseConverter):
#     def __init__(self, url_map, *items):
#         super(RegexConverter, self).__init__(url_map)
#         self.regex = items[0]


app = Flask(__name__)
sock = Sock(app)
# app.url_map.converters['regex'] = RegexConverter
clients = {}

@app.route('/register', methods=["POST"])
def register():
    salt = bcrypt.gensalt()
    app.secret_key = salt
    db = MongoDB.mongoDB()
    username = request.form.get("NewUsername")
    password = request.form.get("NewPassword")
    user_info = db.findInfo(username)
    if user_info is not None:
        return render_template("signup.html", failed=1)
    hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()
    db.addInfo(username, hashed_password, salt)
    db.addProfile(username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "bird.gif")
    response = redirect("/")
    return response


@app.route('/image-upload', methods=["POST"])
def upload():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    info = db.findInfo(username)
    salt = info["salt"]
    filename = request.files['filename']
    file = filename.read()
    if len(file) == 0:
        response = redirect(f"profilePage?username={username}")
        return response
    else:
        type_temp = filename.filename.split(".")[-1]
        salt = salt.decode().replace(".", "").replace("/","")
        name = salt+'.'+type_temp
        f = open("static/user_photo/" + name, 'wb')
        f.write(file)
        f.close()
        db.Update_photo(username, name)
        response = redirect(f"profilePage?username={username}")
        return response

@app.route('/', methods=["GET", "POST"])
def login():
    salt = bcrypt.gensalt()
    app.secret_key = salt
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('signin.html')
    if request.form.keys().__contains__("NewUsername"):
        username = request.form.get("NewUsername")
        password = request.form.get("NewPassword")
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()
        db.addInfo(username, hashed_password, salt)
        db.addProfile(username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "bird.gif")
        return render_template("signin.html", successfully="Your account has been created successfully!")

    else:
        AuthenticationToken = generate_token()
        username = request.form.get("username")
        password = request.form.get("password")
        user_info = db.findInfo(username)

        if user_info is None:
            return render_template("signin.html", failed=1)
        salt, stored_password = user_info["salt"], user_info["password"]
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()
        if hashed_password == stored_password:
            db.add_AuthenticationToken(username, AuthenticationToken)
            response = redirect('chat')
            response.set_cookie("userToken", AuthenticationToken, max_age=3600)
            return response
        else:
            return render_template("signin.html", failed=2)



@app.route('/profile', methods=["GET", "POST"])
def profile():
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('Profile.html')
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    print("update")
    db.UpdateProfile(username, request.form.get("email"), request.form.get("sex"), request.form.get("dob"), request.form.get("address"), request.form.get("bio"),request.form.get("status"))
    response = redirect(f"profilePage?username={username}")
    return response


@app.route('/user', methods=["GET", "POST"])
def userPage():
    if request.method == 'GET':
        return render_template("UserPage.html")
    print(1)


# @app.route('/profile/<regex("[a-z0-9]*"):username>', methods=["GET","POST"])
@app.route('/profilePage', methods=["GET","POST"])
def profilePage():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    print(cookie)
    stored_username = db.findUsernameByCookie(cookie)['username']
    db = MongoDB.mongoDB()
    username = request.args.get('username')
    print(username)
    info = db.findProfile(username)
    print(info)

    #update mode
    if username == stored_username:
        print(f"{info['avatar']}")
        return render_template("Profile.html",username=f"{username}", email=f"{info['email']}", sex=f"{info['sex']}",
                                dob =f"{info['dob']}", address=f"{info['address']}", bio=f"{info['bio']}",
                                status =f" {info['status']}", avatar=f"{info['avatar']}")
    # view mode
    else:
        return render_template("Profile.html", username=f"{username}", email=f"{info['email']}", sex=f"{info['sex']}",
                                dob =f"{info['dob']}", address=f"{info['address']}", bio=f"{info['bio']}",
                                status =f" {info['status']}", avatar=f"{info['avatar']}", hidden="visibility: hidden")


@app.route('/chat')
def chat():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    clients[username] = ""
    render_text = []
    render_text2 = []

    for c in clients:
        if c not in render_text:
            render_text.append(c)
            render_text2.append((c, db.findProfile(c)['bio']))
    return render_template("mainPage.html", username=username, onlines=render_text, users=render_text, onlines2=render_text2)



@app.route("/allevents")
def allevents():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    render_text2 = []
    for c in clients:
        if c not in render_text2:
            render_text2.append((c, db.findProfile(c)['bio']))
    return render_template("ALLEvents.html", username=username, onlines2=render_text2)

@app.route("/allusers")
def allusers():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    render_text = []
    for c in clients:
        if c not in render_text:
            render_text.append(c)
    return render_template("ALLusers.html", username=username, onlines=render_text, users=render_text)


@app.route("/about")
def about():
    return render_template("AboutUs.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")



@sock.route('/websocket')
def websocket(socket):
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    clients[db.findUsernameByCookie(cookie)['username']] = socket
    while True:
        data = socket.receive()
        # html character escape
        data = json.loads(data)
        data['username'] = username
        if data['messageType'].__contains__("webRTC"):
            data = json.dumps(data)
            for c in clients:
                if clients[c] != socket:
                    clients[c].send(data)

        else:
            print(data)
            if data['Emoji'] == '0':
                data['comment'] = data['comment'].replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
                data['username'] = data['username'].replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")

            target_user = data['target']
            db.addChat(username, target_user, data["comment"])
            if target_user == 'All users':
                data = json.dumps(data)
                try:
                    for c in clients:
                        try:
                            clients[c].send(data)
                        except Exception as e:
                            continue
                except Exception as e:
                    continue
            else:
                data['comment'] = data['comment'] + '(private)'
                data = json.dumps(data)
                try:
                    if clients[target_user] != socket:
                        clients[target_user].send(data)
                        socket.send(data)
                    else:
                        socket.send(data)
                except Exception as e:
                    continue


def generate_token():
    token = ""
    for i in range(20):
        x = random.randint(0, 100)
        if x % 3 == 0:
            token += chr(random.randint(48, 57))
        elif x % 2 == 0:
            token += chr(random.randint(65, 90))
        else:
            token += chr(random.randint(97, 122))
    return token

@app.route('/logout', methods=["GET", "POST"])
def logout():
    response = redirect("/")
    response.set_cookie("userToken", "InvalidCookie", max_age=3600)
    return response

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port = "8000")
    app.run()