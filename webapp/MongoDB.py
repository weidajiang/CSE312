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
        Profile = db.Profile
        self.Profile = Profile

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

    def addProfile(self, username, sex, year, address, bio):
        data = {"username": username,
                "sex": sex,
                "year": year,
                "address": address,
                "bio": bio}
        self.Profile.insert_one(data)

    def UpdateProfile(self, username, sex, birth, address, bio):
        new_value = {"$set": {"sex": sex, "year": birth, "address": address, "bio": bio}}
        target = {"username": username}
        self.Profile.update_one(target, new_value)

    def findProfile(self, username):
        result = self.Profile.find_one({"username": username})
        return result







