import pymongo

class mongoDB:

    def __init__(self):
        # mongodb://localhost:27017/
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.Users
        InfoProject = db.InfoProject
        self.InfoProject = InfoProject
        Cookies = db.Cookies
        self.Cookies = Cookies

    def addInfo(self, username, password, salt):

        data = {"username": username,
                "password": password,
                "salt": salt}
        self.InfoProject.insert_one(data)

    def findInfo(self, username):
        result = self.InfoProject.find_one({"username": username})
        return result

    def add_AuthenticationToken(self, username, token):
        data = {"username": username,
                "token": token}
        self.Cookies.insert_one(data)


    def findUsernameByCookie(self, cookie):
        result = self.Cookies.find_one({"token": cookie})
        return result






