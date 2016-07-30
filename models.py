from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
"""
Supertux Version Model

"""
import enum
class TypeEnum(enum.Enum):
    world = "one"
    languagepack = "two"
    three = "three"


"""
User Model
Every User contains of a username,
"""
class User(db.Model):
    def __init__(self,github_access_token):
        self.github_access_token = github_access_token
    id = db.Column(db.Integer, primary_key=True,nullable=False, unique=True, autoincrement=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    github_access_token = db.Column(db.String(64), index=True, unique=True)
    addons = db.relationship('Addon', backref='user',
                             lazy='dynamic')
class Addon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    name = db.Column(db.String)
    automaticmode = db.Column(db.BOOLEAN)
    license = db.Column(db.String(60))
    author = db.Column(db.String(60))
    title = db.Column(db.String(60))
    versions = db.relationship('AddonVersion', backref='addon',
                               lazy='dynamic'
                               )
    type = db.Column(db.Enum('world', 'languagepack', name='addon_types'))
    description = db.Column(db.Text)

    def setUser(self,u):
        self.user_id = u.id

    def getType(self):
        if self.type == TypeEnum.world:
            return "world"
        elif self.type == TypeEnum.languagepack:
            return "lpack"
        return str(self.type)



class AddonVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.id'))
    version = db.Column(db.String(10))
    changes = db.Column(db.Text())
    source = db.Column(db.Text())

class SuperTuxVersions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10))




