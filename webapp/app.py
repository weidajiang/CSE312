import bcrypt
import os
import MongoDB
import hashlib
import random
import json
from flask_sock import Sock
from werkzeug.routing import BaseConverter
from flask import render_template, request, Flask, redirect


#让route可以以正则表达式的形式2
# IDK
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
sock = Sock(app)
app.url_map.converters['regex'] = RegexConverter
clients = {}


# #设置网页图标
# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
#
#
# #设置css
# @app.route('/style.css')
# def css_file():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'style.css')
@app.route('/register', methods=["POST"])
def register():
    salt = bcrypt.gensalt()
    app.secret_key = salt  # 设置随机生成salt
    db = MongoDB.mongoDB()
    username = request.form.get("NewUsername")  # 获取注册表单里的username
    password = request.form.get("NewPassword")  # 获取注册表单里的password
    hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()  # 哈希加盐
    db.addInfo(username, hashed_password, salt)  # 存入数据库
    db.addProfile(username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "bird.gif")
    response = redirect("http://127.0.0.1:5000/")  # 放回路径
    return response

#头像的更新
@app.route('/image-upload', methods=["POST"])
def upload():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")  # 拿到cookie
    username = db.findUsernameByCookie(cookie)['username']  # 通过cookie拿到username
    info = db.findInfo(username)
    salt = info["salt"]
    #拿到slat 作为文件名字 加上原文件后缀
    filename = request.files['filename']
    file = filename.read()
    if len(file) == 0:
        response = redirect(f"http://127.0.0.1:5000/profile/{username}")
        return response
    else:
        type_temp = filename.filename.split(".")[-1]# 拿到文件后缀
        salt = salt.decode().replace(".", "").replace("/","")
        #存入分配的文件中
        name = salt+'.'+type_temp
        f = open("static/user_photo/" + name, 'wb')
        f.write(file)
        f.close()

        db.Update_photo(username, name)

        response = redirect(f"http://127.0.0.1:5000/profile/{username}")
        return response

@app.route('/', methods=["GET", "POST"])
def login():
    salt = bcrypt.gensalt()
    app.secret_key = salt  # 设置随机生成salt
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('signin.html')
    if request.form.keys().__contains__("NewUsername"):
        username = request.form.get("NewUsername")  #获取注册表单里的username
        password = request.form.get("NewPassword")  #获取注册表单里的password
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()  #哈希加盐
        db.addInfo(username, hashed_password, salt)  #存入数据库
        db.addProfile(username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "bird.gif")
        return render_template("signin.html", successfully="Your account has been created successfully!")

    else:
        '''这里要判断用户名,hash值, salt是否存于database'''
        AuthenticationToken = generate_token()
        username = request.form.get("username")  # 获取登录表单里的username
        password = request.form.get("password")  # 获取登录表单里的password
        user_info = db.findInfo(username)        # 数据库查找username信息
        #如果找不到username直接放回
        if user_info is None:
            return render_template("signin.html", failed="wrong password or username")
        salt, stored_password = user_info["salt"], user_info["password"]  #存于数据的秘密和盐
        hashed_password = hashlib.sha224(password.encode() + salt).hexdigest()
        if hashed_password == stored_password:   #判断密码是否配对
            db.add_AuthenticationToken(username, AuthenticationToken)   #将cookie数据
            response = redirect("http://127.0.0.1:5000/chat")   #放回路径
            response.set_cookie("userToken", AuthenticationToken, max_age=3600)   #设置cookie
            return response
        else:
            return render_template("signin.html", failed="wrong password or username")


# 访问用户profile
@app.route('/profile', methods=["GET", "POST"])
def profile():
    db = MongoDB.mongoDB()
    if request.method == 'GET':
        return render_template('Profile.html')
    cookie = request.cookies.get("userToken")
    username = db.findUsernameByCookie(cookie)['username']
    print("update")
    # 拿到当前用户profile在进行redirect
    #email, sex, dob, address, bio, status, avatar
    db.UpdateProfile(username, request.form.get("email"), request.form.get("sex"), request.form.get("dob"), request.form.get("address"), request.form.get("bio"),request.form.get("status"))
    response = redirect(f"http://127.0.0.1:5000/profile/{username}")
    return response


#登入成功页面
@app.route('/user', methods=["GET", "POST"])
def userPage():
    if request.method == 'GET':
        return render_template("UserPage.html")
    print(1)


#访问meHotel
@app.route('/kiwi')
def kiwi():
    with open("static/kiwi-removebg-preview.png", "rb") as f:
        file = f.read()
    return file


#通过正则表达式来判断路径是否为 /profile/(username) 格式
@app.route('/profile/<regex("[a-z0-9]*"):username>', methods=["GET","POST"])
def profilePage(username):
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")   #拿到cookie
    print(cookie)
    stored_username = db.findUsernameByCookie(cookie)['username']  #通过cookie拿到username
    db = MongoDB.mongoDB()
    # 拿到当前username的profile
    info = db.findProfile(username)
    print(info)
    # 如果是本人提供修改profile选项
    # email, sex, dob, address, bio, status, avatar

    if username == stored_username:
        print(f"{info['avatar']}")
        return render_template("Profile.html",username=f"{username}", email=f"{info['email']}", sex=f"{info['sex']}",
                                dob =f"{info['dob']}", address=f"{info['address']}", bio=f"{info['bio']}",
                                status =f" {info['status']}", avatar=f"{info['avatar']}")
    # 不是本人只能游览
    else:
        return render_template("Profile.html", username=f"{username}", email=f"{info['email']}", sex=f"{info['sex']}",
                                dob =f"{info['dob']}", address=f"{info['address']}", bio=f"{info['bio']}",
                                status =f" {info['status']}", avatar=f"{info['avatar']}", hidden="visibility: hidden")

# 聊天室页面
@app.route('/chat')
def chat():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")   #拿到cookie
    username = db.findUsernameByCookie(cookie)['username']  #通过cookie拿到username
    clients[username] = ""
    # 显示当前聊天室里的人  这里有一个bug
    render_text = []
    render_text2 = []

    for c in clients:
        if c not in render_text:
            render_text.append(c)
            render_text2.append((c, db.findProfile(c)['bio']))
    return render_template("mainPage.html", username=username, onlines=render_text, users=render_text, onlines2=render_text2)



@app.route("/allevents")
def allEvent():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")  #从header拿到cookie
    username = db.findUsernameByCookie(cookie)['username']  #通过cookie拿到username
    render_text2 = []
    for c in clients:
        if c not in render_text2:
            render_text2.append((c, db.findProfile(c)['bio']))
    return render_template("ALLEvents.html", username=username, onlines2=render_text2)

@app.route("/allusers")
def allUser():
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")  #从header拿到cookie
    username = db.findUsernameByCookie(cookie)['username']  #通过cookie拿到username
    render_text = []
    for c in clients:
        if c not in render_text:
            render_text.append(c)
    return render_template("ALLusers.html", username=username, onlines=render_text, users=render_text)


@app.route("/about")
def AboutUs():
    return render_template("AboutUs.html")


@app.route("/signup")
def SignUp():
    return render_template("signup.html")



#暂时模拟websocket, 响应牵手, socketio用不明白只能用这个来代替了(我是傻逼)
@sock.route('/websocket')
def websocket(socket):
    db = MongoDB.mongoDB()
    cookie = request.cookies.get("userToken")  #从header拿到cookie
    username = db.findUsernameByCookie(cookie)['username']  #通过cookie拿到username
    clients[db.findUsernameByCookie(cookie)['username']] = socket  #吧socket加入到字典去
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
        # 判断是否为Emoji类型

        else:
            print(data)
            if data['Emoji'] == '0':
                data['comment'] = data['comment'].replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
                data['username'] = data['username'].replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
            # 公屏聊天
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
            # 私聊
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
def logOut():
    response = redirect("http://127.0.0.1:5000/")  # 放回路径
    response.set_cookie("userToken", "InvalidCookie", max_age=3600)
    return response

if __name__ == '__main__':
    app.run()