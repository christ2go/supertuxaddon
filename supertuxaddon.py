from flask import Flask, render_template, flash, redirect, request, url_for, session,g,jsonify
from werkzeug import secure_filename
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask.ext.github import GitHub
from flask.ext.bower import Bower
from slugify import slugify
from functools import wraps
from flask_bootstrap import WebCDN
import os
from pprint import pprint
from models import db
import shutil
import zipfile
import requests, io
import sexpr
import git
import glob

def zipdir(path, zipf,prefix=""):
    # Iterate all the directories and files
    for root, dirs, files in os.walk(path):
        # Create a prefix variable with the folder structure inside the path folder.
        # So if a file is at the path directory will be at the root directory of the zip file
        # so the prefix will be empty. If the file belongs to a containing folder of path folder
        # then the prefix will be that folder.
        if root.replace(path,'') == '' and not prefix:
                prefix = ''

        else:
                # Keep the folder structure after the path folder, append a '/' at the end
                # and remome the first character, if it is a '/' in order to have a path like
                # folder1/folder2/file.txt
                prefix = root.replace(path, '') + '/'
                if (prefix[0] == '/'):
                        prefix = prefix[1:]
        for filename in files:
                actual_file_path = root + '/' + filename
                zipped_file_path = prefix + filename
                zipf.write( actual_file_path, zipped_file_path)

def create_app():
  app = Flask(__name__)
  app.config.from_object('config')
  Bootstrap(app)
  Bower(app)
  app.extensions['bootstrap']['cdns']['jquery'] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/")
  db.init_app(app)

  return app
app = create_app()
github = GitHub(app)
with app.app_context():
    g.user = None
@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin",False):
            flash("You have to login!",category="danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_user():
    if session.get("loggedin",False):
        user = User.query.filter_by(id=session["user_id"]).first()
        g.user = user
    else:
        flash("Hi")
        user = None  # Make it better, use an anonymous User instead



@app.route('/')
def index():
    return render_template("index.html")
"""
Function used for logging in with github
"""
@app.route('/loginwithgh')

def login_gh():
    return github.authorize(scope="user,repo")


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)
    ouser = User(oauth_token)

    g.user = ouser
    udict = github.get("user")
    user = User.query.filter_by(nickname=udict["login"]).first()
    if user is None:
        user = ouser
        user.nickname = udict["login"]
        db.session.add(user)

    user.github_access_token = oauth_token
    db.session.commit()
    session['user_id'] = user.id
    session['loggedin'] = True
    flash("Login successfull!",category="success")
    flash(str(session))
    # Add login in session variable


    return redirect(next_url)

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token
@app.route("/logout")
def logout():
    flash("Logged out.",category="success")
    session["loggedin"] = False
    session['user_id'] = None
    return redirect(url_for('index'))

@app.route("/addons/add",methods=["GET","POST"])
@login_required
def add_addon():
    if request.method == "POST":
        flash("Creating account!")
        title = request.form["addon-name"]
        name = slugify(request.form["addon-name"])
        descr = request.form["description"]
        managed = request.form.get("managed-mode")
        type = request.form.get("type")
        if type == "world":
            type = 'world'
        if type == "lpack":
            type = 'languagepack'

        # Check if slug really doesn't exist
        if len(Addon.query.filter_by(name=name).all()):
            flash("The name is not available!",category="danger")
            return render_template("addon/add.html")
        addon = Addon()
        addon.user = (g.user)
        if managed == "on":
            addon.name = name
            addon.automaticmode = True
            addon.description = descr
            addon.type = type
            addon.license = request.form.get("addon-license")
            addon.title = title
        else:
            # Create the add on
            addon.name = name
            addon.automaticmode = False
            addon.description = descr
            addon.type = type
            addon.title = title
        db.session.add(addon)
        db.session.commit()
        return redirect("user/"+g.user.nickname)
    else:
        return render_template("addon/add.html")

@app.route("/user/:username")
def userpage(username):
    return username
"""
    AJAX HELPER FUNCTIONS

"""

# Check if a slug (project name) is still available

@app.route('/_isavailable')
def isavailable():
    rv = False
    #if Addon.query
    return jsonify({"rv":rv})

@app.route("/user/<username>")
def user(username):
    # Check if user exists available
    user = User.query.filter_by(nickname=username).first()
    if user == None:
        flash("That user doesn't exist.")
        redirect(url_for("index"))
    test = ""
    tstr = ""

    return render_template("user/user.html", addons=user.addons.all(),username = username)

    return test

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ["7z","zip"]


@app.route("/user/<username>/addversion",methods=["GET","POST"])
@login_required
def add_version(username):
    if request.method == "POST":
        pprint(request.form)
        if not username == g.user.nickname:
            flash("You're not allowed to publish under this user's id.")
            redirect(url_for("index"))
        # Search for the addon
        addon = Addon.query.filter_by(name=request.form["addon-name"]).first()
        if addon == None:
            return jsonify({"err":"Addon not found!"})
        # Addon exists, check if Version exists
        if db.session.query(AddonVersion,Addon).filter(Addon.user == g.user).filter(AddonVersion.version == request.form["versionnumb"]).first() != None:
            return jsonify({"err": "Version exists!"})
        pprint(request.form)
        # Upload from the datasource into directory tmp/:username/
        if request.form["sourcetype"] == "http":
            if 'addonfile' not in request.files:
                return jsonify({"err": "No file given!"})
            # Check if a file was submitted (not empty)

            if request.files["addonfile"] == "":
                return jsonify({"err": "No file selected!"})
            # Check if extension is either 7z or zip
            file = request.files["addonfile"]
            if not (file and allowed_file(file.filename)):
                return jsonify({"err": "Incorrect file selected!"})
            filename = secure_filename(file.filename)
            dirname = os.path.join(app.config['UPLOAD_FOLDER'],addon.name+request.form["versionnumb"])
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
            os.mkdir(dirname)
            #dirname = os.path.join(dirname, addon.name + request.form["versionnumb"])
            #os.mkdir(dirname)
            filename = os.path.join(dirname, filename)

            file.save(filename)
            os.chdir(dirname)
            # Unzip (or un7zip) the file
            with zipfile.ZipFile(filename, 'r') as myzip:
                for file in myzip.namelist():
                    dir = file.split("/")[0]
                    myzip.extract(file,path=dirname)
            # rename folder
            print(dir)
            os.rename(dir,addon.name+request.form["versionnumb"])
            filename = os.path.join(dirname,addon.name+request.form["versionnumb"])
            #return jsonify({"err":fname.filename})
        elif request.form["sourcetype"] == "githubupl":
            print("Uploading from github")
            repo = request.form["reposelect"]
            #  #
            repoapi = github.get("repos/%s/%s"%(g.user.nickname,repo))
            pprint(repoapi)
            dirname = os.path.join(app.config['UPLOAD_FOLDER'], addon.name + request.form["versionnumb"])
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
            os.mkdir(dirname)
            dirname = os.path.join(dirname, addon.name + request.form["versionnumb"])
            os.mkdir(dirname)
            repo = git.Repo.init(dirname)
            origin = repo.create_remote('origin', repoapi["git_url"])
            origin.fetch()
            origin.pull(origin.refs[0].remote_head)
            filename = dirname
            # Uploaded from github
        elif request.form["sourcetype"] == "superdata":
            # Download from repo
            addonssrc = github.get("repos/SuperTux/addons-src/contents/")
            # Create directory, download zip , then only unpack appropriate folder
            dirname = os.path.join(app.config['UPLOAD_FOLDER'], addon.name + request.form["versionnumb"])
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
            os.mkdir(dirname)
            zip_file_url = "https://github.com/SuperTux/addons-src/archive/master.zip"

            with open(dirname+'/addons.zip', 'wb') as handle:
                response = requests.get(zip_file_url)

                if not response.ok:
                    return jsonify({"err":"Unable to fetch supertux/addons-src. Please upload manually (e.g. via ftp)"})
                # Something went wrong

                for block in response.iter_content(1024):
                    handle.write(block)
            with zipfile.ZipFile(dirname+'/addons.zip',"r") as z:
                for item in z.namelist():
                    if item.startswith("addons-src-master/"+request.form["import-folder"]+"/"):
                        print("Found file")
                        z.extract(item,path=dirname)
                        if item == "addons-src-master/"+request.form["import-folder"]+"/":
                            filename = os.path.join(dirname,item)
            os.remove(dirname+"/addons.zip")
            print(filename)
            os.rename(filename, os.path.join(dirname,addon.name + request.form["versionnumb"]))
            filename = os.path.join(dirname, addon.name + request.form["versionnumb"])

        else:
            return jsonify({"err": "Source unknown!"})
        version = AddonVersion()
        version.addon = addon
        olddir  = os.getcwd()
        q = AddonVersion.query.filter_by(addon=addon).order_by(AddonVersion.int_version.desc())
        if q.first().int_version == None:
            version.int_version = 1
        else:
            version.int_version = q.first().int_version + 1
        #### File is now uploaded #### => if managed mode it's nearly done, else check for md5 hash, version number
        if addon.automaticmode:
            os.chdir(filename)
            version.version = request.form["versionnumb"]
            version.author = addon.author
            version.license = addon.license
            # create .nfo file
            f = open(os.path.join(filename,"addon.nfo"),"w")
            f.write(version.generateNFO())
            f.close()
            print(version.generateNFO())
        else:
            # Check for NFO File in directory
            os.chdir(filename)
            if len(glob.glob("*.nfo")) == 0:
                return jsonify({"err":"No .nfo file was found!"})
            if len(glob.glob("*.nfo")) > 1:
                return jsonify({"err": "Too many .nfo files were found!"})
            nfofile = glob.glob("*.nfo")[0]
            print(nfofile)
            f = open(nfofile,"r")
            fcon = ("".join(f.readlines()))
            # Use grumbel's sexpr to parse the file
            try:
                x = sexpr.parse(fcon)
            except Exception:
                return jsonify({"err":"The nfo file seems to be poorly formatted. (Please recheck)"})
            for elem in x:
                if elem[0] == "version":
                    version.version = elem[1]
                if elem[0] == "license":
                    version.license = elem[1]
                if elem[0] == "author":
                    version.author = elem[1]

        # Internal version number was set
        print(version.int_version)
        # Finally zip and 7z the addon
        # Return to "main" directory
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        print(filename)
        zipf = zipfile.ZipFile('addons/%s_%s.zip'%(addon.name,version.int_version), 'w', zipfile.ZIP_DEFLATED)
        zipdir(filename+"/..", zipf)
        zipf.close()
        # Add file
        f = AddonFiles()
        f.addonvers = version
        f.format = "zip"
        f.path = zipf.filename

        db.session.add(version)
        db.session.add(f)

        # Add supported Versions

        db.session.commit()

        return "ok"
    # Check if user exists available
    user = User.query.filter_by(nickname=username).first()
    if user == None or user != g.user:
        flash("That user doesn't exist, or you don't have permission.")
        redirect(url_for("index"))
    # Get github data
    repos = []
    reposraw = github.get("user/repos")
    print(reposraw)
    for repo in reposraw:
        repos.append(repo["name"])

    addonssrc = github.get("repos/SuperTux/addons-src/contents/")
    print(addonssrc)
    dirs = []
    for f in addonssrc:
        if f["type"] == "dir":
            dirs.append(f["name"])
    print(dirs)
    versions = []
    for version in SuperTuxVersions.query.all():
        versions.append(version.version)
    addons =user.addons.all()
    return render_template("addon/update.html", **locals())



if __name__ == '__main__':
    app.run(debug=True,port=8080)




