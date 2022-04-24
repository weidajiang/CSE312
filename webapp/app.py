import flask
import bcrypt
import hashlib

app = flask.Flask(__name__)

@app.route('/', methods=["GET","POST"])
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


@app.route('/user')
def userPage():
    username = flask.session["user_info"]
    return flask.render_template("UserPage.html", username=username)






if __name__ == '__main__':
    app.run()
