from flask import Flask, render_template, request, redirect, session, url_for, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.orm import relationship

import base64

app = Flask(__name__)

app.secret_key = 'somesecretkeythatonlyishouldknow'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@localhost:5432/projectdatabase"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://jwtdsuzp:VAcbiITCmSzw2VHFyZk4ejKFeZ7faoq3@tyke.db.elephantsql.com/jwtdsuzp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)

    author = relationship('User', foreign_keys=[author_id])
    house = relationship('House', foreign_keys=[house_id])

    def __repr__(self):
        return '<Item (id:%r, name:%r)>' % (self.id, self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self) -> str:
        return '<User (id:%r, username:%r)>' % (self.id, self.username)


class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120))
    address = db.Column(db.String(120))

    user = relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return '<House (id:%r, name:%r)>' % (self.id, self.name)


class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    status = db.Column(db.String(80), nullable=False, default = 'pending')

    house = relationship('House', foreign_keys=[house_id])
    sender = relationship('User', foreign_keys=[sender_id])
    recipient = relationship('User', foreign_keys=[recipient_id])

    def __repr__(self):
        return '<Invitations (id:%r, sender_id:%r, recipient_id:%r)>' % (self.id, self.sender_id, self.recipient_id)

class Takers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    user = relationship('User', foreign_keys=[user_id])
    item = relationship('Item', foreign_keys=[item_id])

    def __repr__(self):
        return '<Takers (id:%r, user_id:%r)>' % (self.id, self.user_id)

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

    invitation = Invitations(sender_id = g.user.id, recipient_id = user_id, house_id = house_id, status = 'pending')
    db.session.add(invitation)
    db.session.commit()
    return redirect("/tracker/" + str(house_id))


@app.get("/user_list/<int:house_id>")
def user_list(house_id):
    if not g.user:
        return redirect(url_for('login'))
    

    invitation_list = db.session.query(Invitations).filter(Invitations.house_id == house_id).filter((Invitations.status == 'rejected') | (Invitations.status == 'accepted')| (Invitations.status == 'pending')).all()
    invitation_list_ids = [invitation.recipient_id for invitation in invitation_list]

    invitation_list_pending = db.session.query(Invitations).filter(Invitations.house_id == house_id).filter(Invitations.status == 'pending').all()
    invitation_list_ids_pending = [invitation.recipient_id for invitation in invitation_list_pending]

    if invitation_list_ids != []:
        user_list = db.session.query(User).filter(and_(User.id != g.user.id, User.id.not_in(invitation_list_ids))).all()
    else:
        user_list = db.session.query(User).filter(User.id != g.user.id).all()

    if invitation_list_ids_pending != []:
        user_list_pending = db.session.query(User).filter(and_(User.id != g.user.id, User.id.in_(invitation_list_ids_pending))).all()
    else:
        user_list_pending = []
    return render_template('userlist.html', user_list = user_list, user_list_pending = user_list_pending, house_id = house_id)

@app.get("/")
def home():
    return redirect(url_for("login"))

# Registration page
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = str(request.form.get("username")).lower()
        password = request.form.get("password")

        user = db.session.query(User).filter(User.username == username).first()
        if user:
            return redirect(url_for("profile"))

        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template('registration.html')


# Add an item to the list
@app.route("/add_item/<int:house_id>", methods=['GET', 'POST'])
def add_item(house_id):
    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get("name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        user_id = g.user.id
        new_item = Item(name=name, price=price, quantity=quantity, author_id=user_id, house_id = house_id)
        db.session.add(new_item)    
        db.session.commit()

        return redirect("/tracker/" + str(house_id))
    
    return render_template('add_item.html', house_id = house_id)


@app.route("/edit_item/<int:house_id>/<int:item_id>", methods=['GET', 'POST'])
def edit_item(house_id, item_id):
    if not g.user:
        return redirect(url_for('login'))

    item = db.session.query(Item).filter(Item.id == item_id).first()
    takers = db.session.query(Takers).filter(Takers.item_id == item_id).all()
    item_quantity = item.quantity - len(takers)

    if request.method == 'POST':
        item.name = request.form.get("name")
        item.price = request.form.get("price")

        if int(request.form.get("quantity")) != item.quantity:
            db.session.query(Takers).filter(Takers.item_id == item_id).delete()

        item.quantity = request.form.get("quantity")
        db.session.commit()
        return redirect("/tracker/" + str(house_id))
    
    
    return render_template('edit_item.html', item = item, item_quantity = item_quantity, house_id = house_id)

# Delete an item
@app.get("/delete_item/<int:house_id>/<int:item_id>")
def delete_item(house_id, item_id):
    if not g.user:
        return redirect(url_for('login'))

    house_id = house_id
    item = db.session.query(Item).filter(Item.id == item_id).first()
    db.session.query(Takers).filter(Takers.item_id == item_id).delete()

    db.session.delete(item)
    db.session.commit()
    return redirect("/tracker/" + str(house_id))

@app.get("/take_one/<int:house_id>/<int:item_id>")
def take_one(house_id, item_id):
    if not g.user:
        return redirect(url_for('login'))
    
    item = db.session.query(Item).filter(Item.id == item_id).first()
    takers = db.session.query(Takers).filter(Takers.item_id == item_id).all()

    if (item.quantity - len(takers)) == 0:
        return redirect("/tracker/" + str(house_id))
    new_taker = Takers(item_id=item_id, user_id=g.user.id)
    db.session.add(new_taker)
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
        invitation = Invitations(sender_id = g.user.id, recipient_id = g.user.id, house_id = house.id, status = 'accepted')
        db.session.add(invitation) 
        db.session.commit()
        return redirect(url_for("profile"))
        
    return render_template('add_house2.html')


# Edit a house
@app.route("/edit_house/<int:house_id>", methods=['GET', 'POST'])
def edit_house(house_id):
    if not g.user:
        return redirect(url_for('login'))

    house = db.session.query(House).filter(House.id == house_id).first()
    if request.method == 'POST':
        house = db.session.query(House).filter(House.id == house_id).first()
        house.name = request.form.get("name")
        house.description = request.form.get("description")
        house.address = request.form.get("address")
        db.session.commit()
        return redirect(url_for("profile"))

    return render_template('edit_house.html', house_id = house_id, house = house)

# Delete an existing house
@app.get("/delete_house/<int:house_id>")
def delete_house(house_id):
    db.session.query(Invitations).filter(Invitations.house_id == house_id).delete()
    db.session.commit()

    takers = db.session.query(Takers).join(Item, Takers.item_id == Item.id).filter(Item.house_id == house_id).all()

    for taker in takers:
        db.session.delete(taker)
    db.session.commit()

    items = db.session.query(Item).filter(Item.house_id == house_id).all()


    for item in items:
        db.session.delete(item)
    db.session.commit()

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
        invitation_list = db.session.query(Invitations).filter(Invitations.recipient_id == g.user.id).filter(Invitations.status == 'accepted').all()
        house_list = [db.session.query(House).filter(House.id == invitation.house_id).first() for invitation in invitation_list if invitation.house_id != None]
    except:
        house_list = []

    try:
        user = db.session.query(User).filter(User.id == g.user.id).first()
        if user:
            data_url = 'data:image/png;base64,' + user.avatar.decode('ascii')
        else: 
            data_url = None
    # image = Image.open(BytesIO(base64.b64decode(avatar)))
    except:
        data_url = None

    return render_template('profile.html', house_list = house_list, image = data_url)

# Notifications page
@app.get("/notifications")
def notifications():
    if not g.user:
        return redirect(url_for('login'))

    # try:
    # Get the user_house_map table for the logged user to get all u status invites.
    invitation_list = db.session.query(Invitations).join(User, Invitations.sender_id == User.id).join(House, Invitations.house_id == House.id).filter(Invitations.recipient_id == g.user.id).filter(Invitations.status == 'pending').all()
    # Swap the sender id with the senders username.

    house_list = [db.session.query(House).filter(House.id == invitation.house_id).first() for invitation in invitation_list if invitation.house_id != None]

    return render_template('notifications.html', house_list = house_list, invitation_list = invitation_list)

# Accept an invitation from the notifications page
@app.get("/accept_invitation/<int:invitation_id>")
def accept_invitation(invitation_id):
    invitation = db.session.query(Invitations).filter(Invitations.id == invitation_id).first()
    invitation.status = 'accepted'
    db.session.commit()
    return redirect(url_for("notifications"))

# Decline an invitation from the notifications page
@app.get("/decline_invitation/<int:invitation_id>")
def decline_invitation(invitation_id):
    invitation = db.session.query(Invitations).filter(Invitations.id == invitation_id).first()
    invitation.status = 'rejected'
    db.session.commit()
    return redirect(url_for("notifications"))

# Add avatar page 
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

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = str(request.form.get("username")).lower()
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

@app.get('/tracker/<int:house_id>')
def tracker(house_id):
    if not g.user:
        return redirect(url_for('login'))

    house = db.session.query(Invitations).filter(Invitations.recipient_id == g.user.id).filter(Invitations.house_id == house_id).filter(Invitations.status == 'accepted').first()
    if house == None:
        return redirect(url_for('profile'))


    item_list = db.session.query(Item).filter(Item.house_id == house_id).all()

    takers = db.session.query(Takers).join(Item, Takers.item_id == Item.id).filter(Item.house_id == house_id).all()

    participants = db.session.query(Invitations).join(User, Invitations.recipient_id == User.id).filter(Invitations.house_id == house_id).filter(Invitations.status == 'accepted').all()
    
    debtors = {}

    for participant in participants:
        debtors[participant.recipient_id] = 0

    for taker in takers:
        if taker.user_id in debtors:
            debtors[taker.user_id] -= taker.item.price / taker.item.quantity
            debtors[taker.item.author.id] += taker.item.price / taker.item.quantity
        else:
            debtors[taker.user_id] = -taker.item.price / taker.item.quantity
    
    debtors = {k: v for k, v in sorted(debtors.items(), key=lambda item: item[1])}
    print(debtors)

    for item in item_list:
        item_takers = [taker for taker in takers if taker.item_id == item.id]
        item.quantity = item.quantity - len(item_takers)
        
    try:
        user = db.session.query(User).filter(User.id == g.user.id).first()
        data_url = 'data:image/png;base64,' + user.avatar.decode('ascii')
    # image = Image.open(BytesIO(base64.b64decode(avatar)))
    except:
        data_url = None

    participants = db.session.query(Invitations).join(User, Invitations.recipient_id == User.id).filter(Invitations.house_id == house_id).filter(Invitations.status == 'accepted').all()

    house = db.session.query(House).filter(House.id == house_id).first()

    return render_template('tracker2.html', item_list = item_list, house = house, participants = participants, debtors = debtors, image = data_url)

if __name__ == "__main__":
    app.run(debug=True)