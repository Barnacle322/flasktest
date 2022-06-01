from app import db
from sqlalchemy.orm import relationship

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)

    author = relationship('Users', foreign_keys=[author_id])
    house = relationship('House', foreign_keys=[house_id])

    def __repr__(self):
        return '<Item (id:%r, name:%r)>' % (self.id, self.name)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self) -> str:
        return '<Users (id:%r, username:%r)>' % (self.id, self.username)


class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120))
    address = db.Column(db.String(120))

    users = relationship('Users', foreign_keys=[user_id])

    def __repr__(self):
        return '<House (id:%r, name:%r)>' % (self.id, self.name)


class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    status = db.Column(db.String(80), nullable=False, default='pending')

    house = relationship('House', foreign_keys=[house_id])
    sender = relationship('Users', foreign_keys=[sender_id])
    recipient = relationship('Users', foreign_keys=[recipient_id])

    def __repr__(self):
        return '<Invitations (id:%r, sender_id:%r, recipient_id:%r)>' % (self.id, self.sender_id, self.recipient_id)


class Takers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    users = relationship('Users', foreign_keys=[user_id])
    item = relationship('Item', foreign_keys=[item_id])

    def __repr__(self):
        return '<Takers (id:%r, user_id:%r)>' % (self.id, self.user_id)


db.create_all()