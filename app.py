from flask import Flask, render_template, request, redirect, session, url_for, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from model import *

import base64

app = Flask(__name__)

app.secret_key = 'somesecretkeythatonlyishouldknow'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@localhost:5432/projectdatabase"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://jwtdsuzp:VAcbiITCmSzw2VHFyZk4ejKFeZ7faoq3@tyke.db.elephantsql.com/jwtdsuzp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# This is ran before each request
# It's needed to make sure the user is logged in
@app.before_request
def before_request():
    # Clear the global user variable
    g.users = None

    # Check whether the user is logged in
    if 'user_id' in session:
        # If the user is logged in then assign the global user variable to the user object, that cooresponds to the user_id in the session
        g.users = db.session.query(Users).filter(Users.id == session['user_id']).first()

# The index page redirects to the login page
@app.get("/")
def home():
    return redirect(url_for("login"))

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = str(request.form.get("username")).lower()
        password = request.form.get("password")

        try:
            users = db.session.query(Users).filter(Users.username == username).first()
        except:
            users = None

        if users and users.password == password:
            session['user_id'] = users.id
            return redirect(url_for("profile"))

        return redirect(url_for("login"))

    return render_template("login.html")


# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Registration page
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the username and password from the form
        # Make the username lowercase to remove case sensitivity
        username = str(request.form.get("username")).lower()
        password = request.form.get("password")

        # Check whether the username is already in the database
        users = db.session.query(Users).filter(Users.username == username).first()
        if users:
            # If the user exists then redirect to the login page
            return redirect(url_for("login"))

        # If the user doesn't exist, create a new user
        new_user = Users(username=username, password=password)
        # Add the user to the database
        db.session.add(new_user)
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for("login"))
    # If the request method is GET then render the registration page
    return render_template('registration.html')

# Profile page
@app.get("/profile")
def profile():
    if not g.users:
        return redirect(url_for('login'))

    try:
        invitation_list = (
            db.session.query(Invitations)
            .filter(Invitations.recipient_id == g.users.id)
            .filter(Invitations.status == 'accepted')
            .all()
        )
        house_list = [db.session.query(House).filter(House.id == invitation.house_id).first() for invitation in
                      invitation_list if invitation.house_id != None]
    except:
        house_list = []

    balance = {}
    for house in house_list:
        balance[house] = 0

    takers = (
        db.session.query(Takers)
        .join(Item, Takers.item_id == Item.id)
        .filter((Takers.user_id == g.users.id) | (Item.author_id == g.users.id))
        .all()
    )
    
    for taker in takers:
        if taker.user_id == g.users.id:
            balance[taker.item.house] -= taker.item.price / taker.item.quantity
        if taker.item.author_id == g.users.id:
            balance[taker.item.house] += taker.item.price / taker.item.quantity


    try:
        users = db.session.query(Users).filter(Users.id == g.users.id).first()
        if users:
            data_url = 'data:image/png;base64,' + users.avatar.decode('ascii')
        else:
            data_url = None
    # image = Image.open(BytesIO(base64.b64decode(avatar)))
    except:
        data_url = None

    return render_template('profile.html', balance=balance, image=data_url)


# Add a new house
@app.route("/add_house", methods=['GET', 'POST'])
def add_house():
    # Check whether the user is logged in
    if not g.users:
        return redirect(url_for('login'))

    # Check if the request method is POST
    if request.method == 'POST':
        # Get the variables from the HTML form
        name = request.form.get("name")
        description = request.form.get("description")
        address = request.form.get("address")
        
        # Add the house to the database
        house = House(user_id=g.users.id, name=name, description=description, address=address)
        db.session.add(house)
        db.session.commit()
        # Add a dummy invitation to the database. where both sender and recipient id are user's
        # This is needed because the system relies on invitations
        invitation = Invitations(sender_id=g.users.id, recipient_id=g.users.id, house_id=house.id, status='accepted')
        db.session.add(invitation)
        db.session.commit()
        return redirect(url_for("profile"))

    return render_template('add_house.html')

# Edit a house
@app.route("/edit_house/<int:house_id>", methods=['GET', 'POST'])
def edit_house(house_id):
    if not g.users:
        return redirect(url_for('login'))
    # Get the house from the database
    house = db.session.query(House).filter(House.id == house_id).first()
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the variables from the HTML form
        house.name = request.form.get("name")
        house.description = request.form.get("description")
        house.address = request.form.get("address")
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for("profile"))
    
    return render_template('edit_house.html', house_id=house_id, house=house)


# Delete an existing house
@app.get("/delete_house/<int:house_id>")
def delete_house(house_id):
    db.session.query(Invitations).filter(Invitations.house_id == house_id).delete()
    db.session.commit()

    takers = (
        db.session.query(Takers)
        .join(Item, Takers.item_id == Item.id)
        .filter(Item.house_id == house_id).all()
    )
    
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


# Notifications page
@app.get("/notifications")
def notifications():
    if not g.users:
        return redirect(url_for('login'))

    # Get the user_house_map table for the logged users to get all u status invites.
    invitation_list = (
        db.session.query(Invitations)
            .join(Users, Invitations.sender_id == Users.id)
            .join(House, Invitations.house_id == House.id)
            .filter(Invitations.recipient_id == g.users.id)
            .filter(Invitations.status == 'pending').all(
        )
    # Swap the sender id with the senders username.

    house_list = [db.session.query(House).filter(House.id == invitation.house_id).first() for invitation in
                  invitation_list if invitation.house_id != None]

    return render_template('notifications.html', house_list=house_list, invitation_list=invitation_list)


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
    if not g.users:
        return redirect(url_for('login'))

    if request.method == 'POST':
        avatar = request.files['file']
        # avatar = request.form.get("avatar")
        image_string = base64.b64encode(avatar.read())

        users = db.session.query(Users).filter(Users.id == g.users.id).first()
        users.avatar = image_string
        db.session.commit()
        return redirect(url_for("profile"))

    return render_template('add_avatar.html')

@app.get('/tracker/<int:house_id>')
def tracker(house_id):
    if not g.users:
        return redirect(url_for('login'))

    house = (
        db.session.query(Invitations)
        .filter(Invitations.recipient_id == g.users.id)
        .filter(Invitations.house_id == house_id)
        .filter(Invitations.status == 'accepted')
        .first()
    )
    
    if house == None:
        return redirect(url_for('profile'))

    item_list = db.session.query(Item).filter(Item.house_id == house_id).all()

    takers = db.session.query(Takers).join(Item, Takers.item_id == Item.id).filter(Item.house_id == house_id).all()

    participants = (
        db.session.query(Invitations)
        .join(Users, Invitations.recipient_id == Users.id)
        .filter(Invitations.house_id == house_id)
        .filter(Invitations.status == 'accepted')
        .all()
    )

    debtors = {}

    for participant in participants:
        debtors[participant.recipient] = 0

    for taker in takers:
        if taker.users in debtors:
            debtors[taker.users] -= taker.item.price / taker.item.quantity
            debtors[taker.item.author] += taker.item.price / taker.item.quantity
        else:
            debtors[taker.users] = -taker.item.price / taker.item.quantity

    debtors = {k: v for k, v in sorted(debtors.items(), key=lambda item: item[1], reverse=True)}
    for item in item_list:
        item_takers = [taker for taker in takers if taker.item_id == item.id]
        item.quantity = item.quantity - len(item_takers)

    try:
        users = db.session.query(Users).filter(Users.id == g.users.id).first()
        data_url = 'data:image/png;base64,' + users.avatar.decode('ascii')
    # image = Image.open(BytesIO(base64.b64decode(avatar)))
    except:
        data_url = None

    house = db.session.query(House).filter(House.id == house_id).first()

    return render_template('tracker.html', item_list=item_list, house=house, debtors=debtors, image=data_url)


@app.get("/user_list/<int:house_id>")
def user_list(house_id):
    # Check if the user is logged in
    if not g.users:
        # If the user is not logged in then redirect to the login page
        return redirect(url_for('login'))

    # Get all of the invitations with a specific house_id
    invitation_list = db.session.query(Invitations).filter(Invitations.house_id == house_id).all()

    # Create a list of all the users that are invited to the house
    invitation_list_ids = [invitation.recipient_id for invitation in invitation_list]

    # Get all of the pending invitations with a specific house_id
    invitation_list_pending = (
        db.session.query(Invitations)
        .filter(Invitations.house_id == house_id)
        .filter(Invitations.status == 'pending')
        .all()
    )
    
    # Create a list of all the users that a have a pending invitation to the house
    invitation_list_ids_pending = [invitation.recipient_id for invitation in invitation_list_pending]

    # Check whether there are any invitations to a specific house
    if invitation_list_ids:
        # If there are then get all of the users that are not invited to the house
        user_list = (
            db.session.query(Users)
            .filter(and_(Users.id != g.users.id, Users.id.not_in(invitation_list_ids)))
            .all()
        )
    else:
        # Otherwise get all of the users that are not the user that is logged in
        user_list = db.session.query(Users).filter(Users.id != g.users.id).all()

    # If there are some pending invitations
    if invitation_list_ids_pending:
        # Get all of the users who have a pending invitation
        user_list_pending = (
            db.session.query(Users)
            .filter(and_(Users.id != g.users.id, Users.id.in_(invitation_list_ids_pending)))
            .all()
        )
    else:
        # Otherwise send an empty list
        user_list_pending = []
    return render_template('userlist.html', user_list=user_list, user_list_pending=user_list_pending, house_id=house_id)


# A function that creates a record in the Invitations table
@app.post('/invite_user/<int:house_id>/<int:user_id>')
def invite_user(house_id, user_id):
    # Check if the user is logged in
    if not g.users:
        # If the user is not logged in then redirect to the login page
        return redirect(url_for('login'))
    # Create a new invitation
    invitation = Invitations(sender_id=g.users.id, recipient_id=user_id, house_id=house_id, status='pending')
    # Add the invitation to the database
    db.session.add(invitation)
    # Commit the changes to the database
    db.session.commit()
    # Redirect the user to the home page
    return redirect("/tracker/" + str(house_id))


# Add an item to the list
@app.route("/add_item/<int:house_id>", methods=['GET', 'POST'])
def add_item(house_id):
    # Check whether the user is logged in
    if not g.users:
        return redirect(url_for('login'))

    # Check if the request method is POST
    if request.method == 'POST':
        # Get the variables from the HTML form
        name = request.form.get("name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        # The id of the owner is the user id of the logged in user
        user_id = g.users.id

        # Create a new item
        new_item = Item(name=name, price=price, quantity=quantity, author_id=user_id, house_id=house_id)
        # Add the item to the database
        db.session.add(new_item)
        # Commit the changes to the database
        db.session.commit()
        # Redirect the user to the home page
        return redirect("/tracker/" + str(house_id))
    # If the request method is GET then render the add item page
    return render_template('add_item.html', house_id=house_id)


# Edit an item
@app.route("/edit_item/<int:house_id>/<int:item_id>", methods=['GET', 'POST'])
def edit_item(house_id, item_id):
    # Check whether the user is logged in
    if not g.users:
        return redirect(url_for('login'))

    # Get the item from the database
    item = db.session.query(Item).filter(Item.id == item_id).first()
    # Get the takers from the database
    takers = db.session.query(Takers).filter(Takers.item_id == item_id).all()
    # Change the quantity of an item according to the number of takers
    item_quantity = int(item.quantity) - len(takers)
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the variables from the HTML form
        item.name = request.form.get("name")
        item.price = request.form.get("price")

        # If the quantity is different from the initial quantity or the current quantity, then delete the takers of the items
        if int(request.form.get("quantity")) != item_quantity or int(request.form.get("quantity")) != item.quantity:
            db.session.query(Takers).filter(Takers.item_id == item_id).delete()

        # Get the quantity from the HTML form
        item.quantity = request.form.get("quantity")
        # Commit the changes to the database
        db.session.commit()
        return redirect("/tracker/" + str(house_id))
    # If the request method is GET then render the edit item page
    return render_template('edit_item.html', item=item, item_quantity=item_quantity, house_id=house_id)


# Delete an item
@app.get("/delete_item/<int:house_id>/<int:item_id>")
def delete_item(house_id, item_id):
    # Check whether the user is logged in
    if not g.users:
        return redirect(url_for('login'))
    # Delete all of the takers from the database
    db.session.query(Takers).filter(Takers.item_id == item_id).delete()
    # Get the item from the database
    item = db.session.query(Item).filter(Item.id == item_id).first()
    # Delete the item from the database. The item is deleted 
    db.session.delete(item)
    # Commit the changes to the database
    db.session.commit()
    return redirect("/tracker/" + str(house_id))


@app.get("/take_one/<int:house_id>/<int:item_id>")
def take_one(house_id, item_id):
    # Check whether the user is logged in
    if not g.users:
        return redirect(url_for('login'))

    # Get the item from the database
    item = db.session.query(Item).filter(Item.id == item_id).first()
    # Get the takers from the database
    takers = db.session.query(Takers).filter(Takers.item_id == item_id).all()

    # Check whether the quantity of the item is greater than 0
    if (item.quantity - len(takers)) == 0:
        # If the quantity is 0 then do nothing
        return redirect("/tracker/" + str(house_id))
    # If the quantity is greater than 0 then create a new taker
    new_taker = Takers(item_id=item_id, user_id=g.users.id)
    # Add the taker to the database
    db.session.add(new_taker)
    # Commit the changes to the database
    db.session.commit()

    return redirect("/tracker/" + str(house_id))


@app.get("/debts/<int:house_id>")
def debts(house_id):
    if not g.users:
        return redirect(url_for('login'))

    takers = (
        db.session.query(Takers)
        .join(Item, Takers.item_id == Item.id)
        .join(Users, Takers.user_id == Users.id)
        .filter(Item.house_id == house_id)
        .all()
    )
    
    participants = (
        db.session.query(Invitations)
        .join(Users, Invitations.sender_id == Users.id)
        .join(House, Invitations.house_id == House.id)
        .filter(House.id == house_id)
        .filter(Invitations.status == "accepted")
        .all()
    )

    debtors = {}
    debts = {}
    for owner in participants:
        for borrower in participants:
            if owner.recipient_id != borrower.recipient_id:
                if owner.recipient_id == g.users.id:
                    debtors[borrower.recipient] = sum([taker.item.price / taker.item.quantity for taker in takers if taker.user_id == borrower.recipient_id and taker.item.author_id == g.users.id])
                if borrower.recipient_id == g.users.id:
                    debts[owner.recipient] = sum([taker.item.price / taker.item.quantity for taker in takers if taker.user_id == borrower.recipient_id and taker.item.author_id == owner.recipient_id])

    return render_template('debts.html', debtors=debtors, debts=debts, house_id=house_id)

if __name__ == "__main__":
    app.run(debug=True)