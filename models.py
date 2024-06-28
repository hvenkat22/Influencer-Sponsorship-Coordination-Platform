from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'sponsor', 'influencer'
    phone_number = db.Column(db.Integer, nullable=False) #Phone number and email are for communication purposes
    email = db.Column(db.String(100), nullable=False)
    flagged = db.Column(db.String(3), nullable=False)
    flagged_messages = db.Column(db.String(200), nullable=True)

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=True)
    industry = db.Column(db.String(150), nullable=True)
    budget = db.Column(db.Float, nullable=True)

class Influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(150), nullable=True)
    niche = db.Column(db.String(150), nullable=True)
    reach = db.Column(db.Integer, nullable=True)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)  # 'public', 'private'
    goals = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.String(3), nullable=False)
    flagged_messages = db.Column(db.String(200), nullable=True)

class AdRequest(db.Model):
    __tablename__ = 'adrequest'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False, unique=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False, unique=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False, unique=False)
    messages = db.Column(db.Text, nullable=True, unique=False)
    requirements = db.Column(db.Text, nullable=True, unique=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'Pending', 'Accepted', 'Rejected'
    temp = db.Column(db.Float, nullable=False)
    payment_received_date = db.Column(db.Date, nullable=True) #Recording date when adrequest is 'paid' for Influencer Stats
