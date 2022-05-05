import bcrypt
import os
import MongoDB
import hashlib
import random
import json
from flask_sock import Sock
from werkzeug.routing import BaseConverter
from flask import render_template, request, send_from_directory, Flask, redirect


#让route可以以正则表达式的形式
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
sock = Sock(app)
app.url_map.converters['regex'] = RegexConverter
clients = {}


#设置网页图标


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


#设置css
@app.route('/style.css')
def css_file():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'style.css')


@app.route('/', methods=["GET", "POST"])
def login():
    salt = bcrypt.gensalt()
    app.secret_key = salt  # 设置随机生成salt
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('index.html')

    if request.form.keys().__contains__("NewUsername"):
        username = request.form.get("NewUsername")  #获取注册表单里的username
        password = request.form.get("NewPassword")  #获取注册表单里的password
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()  #哈希加盐
        db.addInfo(username, hashed_password, salt)  #存入数据库
        db.addProfile(username, "N/A", "N/A", "N/A", "N/A", "N/A")
        return render_template("index.html", successfully="Your account has been created successfully!")

    else:
        '''这里要判断用户名,hash值, salt是否存于database'''
        AuthenticationToken = generate_token()
        username = request.form.get("username")  # 获取登录表单里的username
        password = request.form.get("password")  # 获取登录表单里的password
        user_info = db.findInfo(username)        # 数据库查找username信息
        salt, stored_password = user_info["salt"], user_info["password"]  #存于数据的秘密和盐
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()
        if hashed_password == stored_password:   #判断密码是否配对
            db.add_AuthenticationToken(username, AuthenticationToken)   #将cookie数据
            response = redirect("http://127.0.0.1:5000/chat")   #放回路径
            response.set_cookie("userToken", AuthenticationToken, max_age=3600)   #设置cookie
            return response
        else:
            return render_template("index.html", failed="wrong password or username")


@app.route('/profile', methods=["GET", "POST"])
def profile():
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('Profile.html')
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    db.UpdateProfile(username, request.form.get("sex"), f"{request.form.get('month')}, {request.form.get('year')}", request.form.get("address"), request.form.get("bio"))
    response = redirect(f"http://127.0.0.1:5000/profile/{username}")
    return response



#登入成功页面
@app.route('/user')
def userPage():

    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    return render_template("UserPage.html", username=username)


#访问meHotel
@app.route('/kiwi')
def kiwi():
    with open("static/kiwi-removebg-preview.png", "rb") as f:
        file = f.read()
    return file


@app.route('/profile/<regex("[a-z]*"):username>')
def profilePage(username):
    db = MongoDB.mongoDB()
    info = db.findProfile(username)
    return render_template("userProfile.html", username=f"Username:   {username}", sex=f"Sex:   {info['sex']}",
                           birth=f"Birthday:   {info['year']}", address=f"Address:   {info['address']}", bio=f"Bio:   {info['bio']}")


#聊天室页面
@app.route('/chat')
def chat():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    clients[username] = ""
    render_text = []
    for c in clients:
        if c not in render_text:
            render_text.append(c)
    return render_template("chat.html", username=username, onlines=render_text, profileLink=f'http://127.0.0.1:5000/profile/{username}')


@app.route("/function.js")
def static_dir(path):
    return send_from_directory("static", path)


#暂时模拟websocket, 响应牵手, socketio用不明白只能用这个来代替了
@sock.route('/websocket')
def websocket(socket):
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    clients[db.findUsernameByCookie(cookie)['username']] = socket
    while True:
        data = socket.receive()
        data = data.replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
        data = json.loads(data)
        data['username'] = username
        target_user = data['target']
        if data.__contains__("webRTC"):
            for c in clients:
                if clients[c] != socket:
                    clients[c].send(data)
        else:
            if target_user == 'All users':
                data = json.dumps(data)
                try:
                    for c in clients:
                        clients[c].send(data)
                except Exception as e:
                    continue
            else:
                data['comment'] = data['comment'] + '(private)'
                data = json.dumps(data)
                if clients[target_user] != socket:
                    clients[target_user].send(data)
                    socket.send(data)
                else:
                    socket.send(data)


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


if __name__ == '__main__':
    app.run()
