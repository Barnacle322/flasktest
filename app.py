from xml.dom.expatbuilder import Rejecter
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, sessions, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

app.secret_key = 'somesecretkeythatonlyishouldknow'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@localhost:5432/projectdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    complete = db.Column(db.Boolean, default = False)
    editable = db.Column(db.Boolean, default = False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Item %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120))
    address = db.Column(db.String(120))

    def __repr__(self):
        return '<House %r>' % self.name

class Item_House_Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    def __repr__(self):
        return '<Item_House_Map %r>' % self.id

class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    status = db.Column(db.String(80), nullable=False, default = 'pending')

    def __repr__(self):
        return '<Invitations %r>' % self.id

db.create_all()

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = db.session.query(User).filter(User.id == session['user_id']).first()

@app.post('/invite_user/<int:house_id>/<int:user_id>')
def invite_user(house_id, user_id):
    house_id = house_id
    user_id = user_id

    invitation = Invitations(sender = g.user.id, recipient = user_id, house_id = house_id, status = 'pending')
    db.session.add(invitation)
    db.session.commit()
    return redirect("/tracker/" + str(house_id))


@app.get("/user_list/<int:house_id>")
def user_list(house_id):
    if not g.user:
        return redirect(url_for('login'))
    

    invitation_list = db.session.query(Invitations).filter(Invitations.house_id == house_id).filter((Invitations.status == 'rejected') | (Invitations.status == 'accepted')| (Invitations.status == 'pending')).all()
    invitation_list_ids = [invitation.recipient for invitation in invitation_list]

    invitation_list_pending = db.session.query(Invitations).filter(Invitations.house_id == house_id).filter(Invitations.status == 'pending').all()
    invitation_list_ids_pending = [invitation.recipient for invitation in invitation_list_pending]

    if invitation_list_ids != []:
        user_list = db.session.query(User).filter(and_(User.id != g.user.id, User.id.not_in(invitation_list_ids))).all()
    else:
        user_list = db.session.query(User).filter(User.id != g.user.id).all()

    if invitation_list_ids_pending != []:
        user_list_pending = db.session.query(User).filter(and_(User.id != g.user.id, User.id.in_(invitation_list_ids_pending))).all()
    else:
        user_list_pending = []
    return render_template('userlist.html', user_list = user_list, user_list_pending = user_list_pending, house_id = house_id)

# Redirect to login page if user is not logged in
@app.get("/")
def home():
    return redirect(url_for("login"))

# Registration page
@app.route('/registration')
def registration():
    return render_template('registration.html')

# Register a user
@app.post("/users")
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("profile"))
# Add an item to the list
@app.post("/add/<int:house_id>")
def add_item(house_id):
    if not g.user:
        return redirect(url_for('login'))

    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")   
    user_id = g.user.id
    new_item = Item(name=name, price=price, quantity=quantity, author=user_id)
    db.session.add(new_item)    
    db.session.commit()

    new_table = Item_House_Map(house_id=house_id, item_id=new_item.id)
    db.session.add(new_table)
    db.session.commit()
    return redirect("/tracker/" + str(house_id))

# Add a new house
@app.route("/add_house", methods=['GET', 'POST'])
def add_house():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        address = request.form.get("address")

        house = House(user_id = g.user.id, name = name, description = description, address = address)
        db.session.add(house)
        db.session.commit()
        invitation = Invitations(sender = g.user.id, recipient = g.user.id, house_id = house.id, status = 'accepted')
        db.session.add(invitation) 
        db.session.commit()
        return redirect(url_for("profile"))
        
    return render_template('add_house2.html')

# Delete an existing house
@app.get("/delete_house/<int:house_id>")
def delete_house(house_id):
    house = db.session.query(House).filter(House.id == house_id).first()
    db.session.delete(house)
    db.session.commit()
    return redirect(url_for("profile"))

# Profile page
@app.get("/profile")
def profile():
    if not g.user:
        return redirect(url_for('login'))

    try:
        invitation_list = db.session.query(Invitations).filter(Invitations.recipient == g.user.id).filter(Invitations.status == 'accepted').all()
        house_list = [db.session.query(House).filter(House.id == invitation.house_id).first() for invitation in invitation_list if invitation.house_id != None]
    except:
        house_list = []

    try:
        user = db.session.query(User).filter(User.id == g.user.id).first()
        data_url = 'data:image/png;base64,' + user.avatar.decode('ascii')
    # image = Image.open(BytesIO(base64.b64decode(avatar)))
    except:
        data_url = None

    return render_template('profile.html', house_list = house_list, image = data_url)

# Notifications page
@app.get("/notifications")
def notifications():
    if not g.user:
        return redirect(url_for('login'))

    try:
        # Get the user_house_map table for the logged user to get all u status invites.
        table_list = db.session.query(Invitations).filter(Invitations.recipient == g.user.id).filter(Invitations.status == 'pending').all()
        # Swap the sender id with the senders username.

        for element in table_list:
            user = db.session.query(User).filter(User.id == element.sender).first()
            house = db.session.query(House).filter(House.id == element.house_id).first()
            element.sender = user.username
            element.house_name = house.name

        house_list = [db.session.query(House).filter(House.id == table.house_id).first() for table in table_list if table.house_id != None]
    except:
        house_list = []
        table_list = []
    return render_template('notifications.html', house_list = house_list, table_list = table_list)

# Accept an invitation from the notifications page
@app.get("/accept_invitation/<int:table_id>")
def accept_invitation(table_id):
    invitation = db.session.query(Invitations).filter(Invitations.id == table_id).first()
    invitation.status = 'accepted'
    db.session.commit()
    return redirect(url_for("notifications"))

# Decline an invitation from the notifications page
@app.get("/decline_invitation/<int:table_id>")
def decline_invitation(table_id):
    table = db.session.query(Invitations).filter(Invitations.id == table_id).first()
    table.status = 'rejected'
    db.session.commit()
    return redirect(url_for("notifications"))

@app.route("/add_avatar", methods=['GET', 'POST'])
def add_avatar():
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':

        avatar = request.files['file']
        # avatar = request.form.get("avatar")
        image_string = base64.b64encode(avatar.read())

        user = db.session.query(User).filter(User.id == g.user.id).first()
        user.avatar = image_string
        db.session.commit()
        return redirect(url_for("profile"))

    return render_template('add_avatar.html')

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
    table = db.session.query(Item_House_Map).filter(Item_House_Map.item_id == item_id).first()
    db.session.delete(table)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("tracker"))


# TODO:redo this
@app.get("/edit/<int:item_id>")
def initiate_edit(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    item.editable = True
    db.session.commit()
    return redirect(url_for("tracker"))

# TODO:redo this
@app.post("/edit_name/<int:item_id>")
def edit_name(item_id):
    item = db.session.query(Item).filter(Item.id == item_id).first()
    item.name = request.form.get("name")
    item.editable = False
    db.session.commit()
    return redirect(url_for("tracker"))

# Login page
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

    return render_template("login.html")

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Tracker page
@app.route('/tracker/<int:house_id>')
def tracker(house_id):
    if not g.user:
        return redirect(url_for('login'))
    house = db.session.query(Invitations).filter(Invitations.recipient == g.user.id).filter(Invitations.house_id == house_id).filter(Invitations.status == 'accepted').first()
    if house == None:
        return redirect(url_for('profile'))

    # Queries the "Table" to get to get all the item ids that are compliant with user_id and house_id
    table_list = db.session.query(Item_House_Map).filter(Item_House_Map.house_id == house_id).all()
    # list = []

    # for table in table_list:
    #     list.append(db.session.query(Item).filter(Item.id == table.item_id).first())

    # Get all the items from the table Item that are compliant with the coresponding item id in the table id, query for which was preceding.
    list = [db.session.query(Item).filter(Item.id == table.item_id).first() for table in table_list if table.item_id]

    for element in list:
        username = db.session.query(User.username).filter(User.id == element.author).first()
        try:
            element.author = username[0]
        except:
            element.author = username
    
    return render_template('tracker.html', item_list = list, house_id = house_id)

if __name__ == "__main__":
    app.run(debug=True)