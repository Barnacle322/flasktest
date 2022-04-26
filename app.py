from doctest import debug_script
from pydoc import describe
import re
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, sessions, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)

app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    complete = db.Column(db.Boolean, default = False)
    editable =db.Column(db.Boolean, default = False)

    def __repr__(self):
        return '<Item %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120))

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)



db.create_all()

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = db.session.query(User).filter(User.id == session['user_id']).first()

# Laod the home page
@app.get("/")
def home():
    # items_list = db.session.query(Item).all()
    return redirect(url_for("login"))

@app.route('/registration')
def registration():
    return render_template('registration.html')

# Add an item to the list
@app.post("/add/<int:house_id>")
def add_item(house_id):
    if not g.user:
        return redirect(url_for('login'))

    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    new_item = Item(name=name, price=price, quantity=quantity)
    db.session.add(new_item)    
    db.session.commit()

    item = db.session.query(Item).filter(Item.name == name, Item.price == price, Item.quantity == quantity).first()
    new_table = Table(house_id = house_id, user_id=g.user.id, item_id=item.id)
    db.session.add(new_table)
    db.session.commit()
    return redirect("/tracker/" + str(house_id))

@app.route("/add_house", methods=['GET', 'POST'])
def add_house():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")

        house = House(user_id = g.user.id, name = name, description = description)
        db.session.add(house)
        db.session.commit()
        return redirect(url_for("profile"))
        
    return render_template('add_house.html')

@app.get("/delete_house/<int:house_id>")
def delete_house(house_id):
    house = db.session.query(House).filter(House.id == house_id).first()
    db.session.delete(house)
    db.session.commit()
    return redirect(url_for("profile"))

@app.get("/user_list")
def user_list():
    if not g.user:
        return redirect(url_for('login'))

    user_list = db.session.query(User).all()
    return render_template('userlist.html', user_list=user_list)

@app.get("/profile")
def profile():
    if not g.user:
        return redirect(url_for('login'))
    try:
        house_list = db.session.query(House).filter(House.user_id == g.user.id).all()
    except:
        house_list = []

    return render_template('profile.html', house_list = house_list)

# Add a new user
@app.post("/users")
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("profile"))

# Update the status of an item
@app.get("/update/<int:item_id>")
def update(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    item.complete = not item.complete
    db.session.commit()
    return redirect(url_for("tracker"))

# Delete an item
@app.get("/delete/<int:item_id>")
def delete(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    table = db.session.query(Table).filter(Table.item_id == item_id).first()
    db.session.delete(table)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("tracker"))


@app.get("/edit/<int:item_id>")
def initiate_edit(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    item.editable = True
    db.session.commit()
    return redirect(url_for("tracker"))


@app.post("/edit_name/<int:item_id>")
def edit_name(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    item.name = request.form.get("name")
    item.editable = False
    db.session.commit()
    return redirect(url_for("tracker"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = db.session.query(User).filter(User.username == username).first()
        except:
            user = None

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for("profile"))
        
        return redirect(url_for("login"))
    img = './static/elements/PERET-removebg-preview.png'

    return render_template("login.html", img=img)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/tracker/<int:house_id>')
def tracker(house_id):
    if not g.user:
        return redirect(url_for('login'))
    table_list = db.session.query(Table).filter(Table.user_id == g.user.id).filter(Table.house_id == house_id).all()
    # list = []

    # for table in table_list:
    #     list.append(db.session.query(Item).filter(Item.id == table.item_id).first())
    list = [db.session.query(Item).filter(Item.id == table.item_id).first() for table in table_list if table.item_id]

    return render_template('tracker.html', item_list = list, house_id = house_id)

if __name__ == "__main__":
    app.run(debug=True)