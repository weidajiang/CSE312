import bcrypt
import os
import MongoDB
import hashlib
import random
import json
from flask_sock import Sock
from flask import make_response, render_template, request, send_from_directory, Flask, redirect, Response



app = Flask(__name__)
sock = Sock(app)
clients = {}


#设置网页图标
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


#设置css
@app.route('/style.css')
def css_file():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'stye.css')


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


#聊天室页面
@app.route('/chat')
def chat():
    render_text = []
    for c in clients:
        render_text.append(clients[c])
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    return render_template("chat.html", username=username, onlines=render_text)


@app.route("/function.js")
def static_dir(path):
    return send_from_directory("static", path)


#暂时模拟websocket, 响应牵手
@sock.route('/websocket')
def websocket(socket):
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    clients[socket] = db.findUsernameByCookie(cookie)['username']
    while True:
        data = socket.receive()
        data = data.replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
        data = json.loads(data)
        data['username'] = username
        data = json.dumps(data)
        if data.__contains__("webRTC"):
            for c in clients:
                if c != socket:
                    c.send(data)
        else:
            for c in clients:
                c.send(data)


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
