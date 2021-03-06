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
    def getAuthorName(self):
        if self.author:
            return self.author
        else:
            return self.user.nickname
    def getType(self):
        if self.type == TypeEnum.world:
            return "world"
        elif self.type == TypeEnum.languagepack:
            return "lpack"
        return str(self.type)
    def typeToSring(self):
        if self.type == "world":
            return "worldmap"
        if self.type == "languagepack":
            return "languagepack"


class AddonVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.id'))
    version = db.Column(db.String(10))
    changes = db.Column(db.Text())
    license = db.Column(db.String(60))
    author = db.Column(db.String(60))
    int_version = db.Column(db.Integer)
    files = db.relationship('AddonFiles', backref='addonvers',lazy='dynamic')

    def generateNFO(self):
        license = self.getLicense()
        author = self.getAuthor()
        #if not self.addon.automaticmode:
        #    return None
        nfo = """
        (supertux-addoninfo
          (id "%s")
          (version %d)
          (type "%s")
          (title "%s")
          (author "%s")
          (license "%s"))

        """%(self.addon.name,self.int_version,str(self.addon.type),self.addon.title,author,license)

        return nfo

    def getAuthor(self):
        author = ""
        if self.license != None:
            author = self.author
        else:
            author = self.addon.author
        if author == None:
            author = "Unknown"
        return author
    def getLicense(self):
        license = ""
        if self.license != None:
            license = self.license
        else:
            license = self.addon.license
        return license


class AddonFiles(db.Model):
    __tablename__ = "addon_files"
    id = db.Column(db.Integer, primary_key=True)
    addonvers_id =db.Column(db.Integer,db.ForeignKey('addon_version.id'))
    format = db.Column(db.String(20)) # File extension
    path = db.Column(db.String(40))

supported_versions = db.Table('supported_versions',
    db.Column('addon_version_id', db.Integer, db.ForeignKey('addon_version.id')),
    db.Column('super_tux_version_id', db.Integer, db.ForeignKey('super_tux_versions.id'))
)

class SuperTuxVersions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10))
    addons = db.relationship('AddonVersion', secondary=supported_versions,backref=db.backref('supported', lazy='dynamic'))



