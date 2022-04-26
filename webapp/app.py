import flask
import bcrypt
import os
from flask_sock import Sock
app = flask.Flask(__name__)
sock = Sock(app)
clients = []


#设置网页图标
@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


#设置css
@app.route('/style.css')
def css_file():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                          'stye.css')


@app.route('/', methods=["GET", "POST"])
def login():
    app.secret_key = bcrypt.gensalt()  # 设置随机生成salt
    if flask.request.method == 'GET':
        return flask.render_template('index.html')
    username = flask.request.form.get("username")  #获取表单里的username
    password = flask.request.form.get("password")  #获取表单里的password
    print(username)
    print(password)
    '''这里要判断用户名,hash值, salt是否存于database'''
    if username == 'buxiangchizhaji' and password == "zhebeizi":
        flask.session['user_info'] = username  #使用username加salt生成cookie
        return flask.redirect("/user")

    if True:
        return flask.render_template("index.html", failed="wrong password or username")


#登入成功页面
@app.route('/user')
def userPage():
    username = flask.session["user_info"]
    return flask.render_template("UserPage.html", username=username)


#访问meHotel
@app.route('/kiwi')
def kiwi():
    with open("static/kiwi-removebg-preview.png", "rb") as f:
        file = f.read()
    return file


#聊天室页面
@app.route('/chat')
def chat():
    return flask.render_template('chat.html')


@app.route("/function.js")
def static_dir(path):
    return flask.send_from_directory("static", path)


#暂时模拟websocket, 响应牵手
@sock.route('/websocket')
def websocket(socket):
    clients.append(socket)
    while True:
        data = socket.receive()
        data = data.replace("\r\n", "").replace("&", "&amp").replace(">", "&gt").replace("<", "&lt")
        if data.__contains__("webRTC"):
            for c in clients:
                if c != socket:
                    c.send(data)
        else:
            for c in clients:
                c.send(data)



if __name__ == '__main__':
    app.run()
