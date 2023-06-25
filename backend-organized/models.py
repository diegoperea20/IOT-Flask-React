from app import db, ma


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user= db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, email, user, password):
        self.email = email
        self.user = user
        self.password = password
        
#Allnodes
class Allnode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user= db.Column(db.String(200))
    code = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(200))

    def __init__(self, user, code, name):
        self.user = user
        self.code = code
        self.name = name

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'user', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Allnode
class AllnodeSchema(ma.Schema):
    class Meta:
        fields = ('id','user', 'code', 'name')


allnode_schema = AllnodeSchema()
allnodes_schema = AllnodeSchema(many=True)