import pymongo


class mongoDB:
    def __init__(self):
        # mongodb://mongo:27017/
        client = pymongo.MongoClient("mongodb://mongo:27017/")
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

    # 用户名，邮箱，性别，生日，地址，个签，状态，头像
    def addProfile(self, username, email, sex, dob, address, bio, status, avatar):
        data = {"username": username,
                "email": email,
                "sex": sex,
                "dob": dob,
                "address": address,
                "bio": bio,
                "status": status,
                "avatar": avatar
                }
        self.Profile.insert_one(data)

    def UpdateProfile(self, username, email, sex, dob, address, bio, status):
        new_value = {"$set": {"email": email, "sex": sex, "dob": dob, "address": address, "bio": bio, "status": status}}
        target = {"username": username}
        self.Profile.update_one(target, new_value)

    def Update_photo(self, username, avatar):
        new_value = {"$set": {"avatar": avatar}}
        target = {"username": username}
        self.Profile.update_one(target, new_value)

    def findProfile(self, username):
        result = self.Profile.find_one({"username": username})
        return result

    def addChat(self, sendFrom, sendTo, comment):

        data = {"from": sendFrom,
                "to": sendTo,
                "comment": comment}
        self.InfoProject.insert_one(data)