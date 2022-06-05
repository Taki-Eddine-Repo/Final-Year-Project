from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import random
import string
"""
Here's What To Do:

1- Write the database structure DRAW it if necessary
2- Create classes models.
3- Run the models to create the tables
4- Write the login logic for the administrator
5- Write the login logic for the receiver
6- Write the administrator page's frontend
7- Write the receuver page's frontened
8- Write the database queries

"""


app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onlineShop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
app.config['UPLOAD_FOLDER'] = "./static/assets/images/uploads"
database = SQLAlchemy(app)


def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_admin(id):
    results = Admin.query.get(id)
    if results is not None:
        return True
    else:
        return False
# Database Schema


class Users(database.Model):
    UID = database.Column(database.Integer, primary_key=True)
    firstname = database.Column(database.String(400), nullable=False)
    lastname = database.Column(database.String(400), nullable=False)
    email = database.Column(database.String(400), nullable=False)
    username = database.Column(database.String(300), nullable=False)
    password = database.Column(database.String(500), nullable=False)
    date_created = database.Column(database.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Users %r>' % self.UID


class Admin(database.Model):
    UID = database.Column(database.Integer, database.ForeignKey(
        "users.UID"), primary_key=True, autoincrement=False)
    conversionRate = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return '<Admin %r>' % self.UID


class Receveur(database.Model):
    UID = database.Column(database.Integer, database.ForeignKey(
        "users.UID"), primary_key=True, autoincrement=False)
    points = database.Column(database.Integer, nullable=False)
    sales = database.Column(database.Integer, nullable=False)
    active = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return '<Receveur %r>' % self.UID


class Proimgs(database.Model):
    IMGID = database.Column(
        database.Integer, primary_key=True)
    PROID = database.Column(
        database.Integer, database.ForeignKey("proimgs.PROID"))
    img = database.Column(database.String(600), nullable=False)

    def __repr__(self):
        return '<Proimgs %r>' % self.PROID


class Products(database.Model):
    PROID = database.Column(
        database.Integer, primary_key=True)
    CATID = database.Column(
        database.Integer, database.ForeignKey("categories.CATID"))
    name = database.Column(database.String(600), nullable=False)
    description = database.Column(database.String(600), nullable=False)
    price = database.Column(database.Integer, nullable=False)
    shippingFee = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return '<Products %r>' % self.PROID


class Categories(database.Model):
    CATID = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(600), nullable=False)
    description = database.Column(database.String(600), nullable=False)

    def __repr__(self):
        return '<Categories %r>' % self.CATID


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products')
def products():
    products = Products.query.all()
    data = []
    for product in products:
        imgs = Proimgs.query.filter(Proimgs.PROID == product.PROID).all()
        data.append([{"product": product, "img": imgs}])
        print(data, '\n')
    return render_template('products.html', data=data)


@app.route('/products/<int:ID>')
def product(ID):
    product = Products.query.get(ID)
    if product is not None:
        category = Categories.query.get(product.CATID)
        imgs = Proimgs.query.filter(Proimgs.PROID == product.PROID).all()
        data = {
            "category": category,
            "product": product,
            "img": imgs
        }
        #data= jsonify(data)
        return render_template('product.html', data=data)
    else:
        return redirect('/404')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/dashboard')
def admin():
    if (session.get("id") is None):
        return redirect('/login')
    if (not check_admin(session.get("id"))):
        return render_template("WRONGPAGEYO.html")
    products = Products.query.all()
    if products is not None:
        data = []
        for product in products:
            imgs = Proimgs.query.filter(
                Proimgs.PROID == product.PROID).all()
            data.append([{"product": product, "img": imgs}])
        rec = Receveur.query.all()
        categories = Categories.query.all()
        categories = Categories.query.all()
        return render_template('dashboard.html', data=data, rec=rec, categories=categories)
    else:
        categories = Categories.query.all()
        rec = Receveur.query.all()
        return render_template('dashboard.html', data=None, rec=rec, categories=categories)


@app.route('/add', methods=['POST', 'GET'])
def addproduct():
    if (session.get("id") is None):
        return redirect('/login')
    if (not check_admin(session.get("id"))):
        return render_template("WRONGPAGEYO.html")
    if request.method == "POST":
        name = request.form["productName"]
        description = request.form["productDesc"]
        price = request.form["price"]
        fee = request.form["fee"]
        select = request.form["category"]
        if request.files is None:
            return redirect(request.url)
        uploaded_files = request.files.getlist("imgs[]")
        # if user does not select file, browser also
        # submit a empty part without filename
        new_product = Products(
            name=name,
            CATID=select,
            description=description,
            price=price,
            shippingFee=fee
        )
        database.session.add(new_product)
        database.session.commit()
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = ran_gen(7) + '-' + str(new_product.PROID) + \
                    '-' + secure_filename(file.filename)
                file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename))
                new_img = Proimgs(
                    PROID=new_product.PROID,
                    img=filename)
                database.session.add(new_img)
                database.session.commit()
        return redirect('/dashboard')
    else:
        categories = Categories.query.all()
        return render_template('addProduct.html', categories=categories)


@app.route('/add/category', methods=['POST', 'GET'])
def addCat():
    if session.get("id"):
        results = Admin.query.get(session.get("id"))
        if results is not None:
            if request.method == "POST":
                name = request.form["name"]
                descr = request.form["desc"]
                new_category = Categories(name=name, description=descr)
                database.session.add(new_category)
                database.session.commit()
                return redirect('/dashboard')
            else:
                return render_template('addCat.html')
        else:
            return redirect('/logitn')


@app.route('/delete/<int:id>')
def delete(id):
    product = Products.query.get_or_404(id)
    Proimgs.query.filter(Proimgs.PROID == product.PROID).delete()
    try:
        database.session.delete(product)
        database.session.commit()
        return redirect('/dashboard')
    except:
        return 'There was a problem deleting.'


@app.route('/delete/category/<int:id>', methods=['POST', 'GET'])
def deleteCat(id):
    category = Categories.query.get_or_404(id)
    try:
        database.session.delete(category)
        database.session.commit()
        return redirect('/dashboard')
    except:
        return 'There was a problem deleting.'


@app.route('/logout')
def logout():
    if session.get("id"):
        session.pop("id", None)
    return redirect('/')


@app.route('/404')
def notFound():
    return "NOT FOUND"


@app.route('/login', methods=["POST", "GET"])
def login():
    if session.get("id"):
        if (check_admin(session.get('id'))):
            return redirect('/dashboard')
        return redirect('/')
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Users.query.filter(Users.username == username).first()
        if user:
            if password == user.password:
                session["id"] = user.UID
                is_admin = check_admin(user.UID)
                if is_admin:
                    return redirect('dashboard')
                else:
                    return redirect('/receiver')
            else:
                return render_template('login.html', message="Wrong password!")
        else:
            return render_template('login.html', message="Uesrname doesn't exist")
    return render_template('login.html')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if session.get("id"):
        if check_admin(session.get("id")):
            return redirect('/dashboard')
        else:
            return redirect('/')
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        if (Users.query.filter(Users.username == username).first()):
            return render_template('signup.html', message="Username Already Taken")
        new_user = Users(firstname=firstname, lastname=lastname,
                         email=email, username=username, password=password)
        database.session.add(new_user)
        database.session.commit()
        new_rec = Receveur(UID=new_user.UID, points=0, sales=0, active=0)
        database.session.add(new_rec)
        database.session.commit()
    return render_template('signup.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/INIT')
def AddAdmin():
    if (Admin.query.get(1) and Users.query.filter(Users.username == "admin").first()):
        return "ALREADY INITIATED"
    else:
        admin = Admin(UID=1, conversionRate=1)
        user = Users(firstname="Hadil", lastname="Abir",
                     email="someone@someone.com", username="admin", password="admin")
        database.session.add(user)
        database.session.add(admin)
        database.session.commit()
        return "THERE WAS AN ERROR IN THE PREVIOUS INITIALIZATION OR THIS IS THE FIRST TIME INITIALIZING."


if __name__ == "__main__":
    app.run(debug=True)
