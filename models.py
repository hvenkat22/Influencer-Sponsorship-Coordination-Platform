#Created by: Hari Venkataraman (hvenkat22)
#Influencer Sponsorship Coordination Platform using Flask-sqlalchemy, Jinja2, HTML, JS, and Bootstrap CSS

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

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False, unique=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False, unique=False)
    adrequest_id = db.Column(db.Integer, db.ForeignKey('adrequest.id'), nullable=False, unique=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    feedback_date = db.Column(db.Date, nullable=False)

class Message(db.Model):
    __tablename__ ='message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_text = db.Column(db.Text, nullable=False)
    notification_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('payment.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False, unique=False)
    adrequest_id = db.Column(db.Integer, db.ForeignKey('adrequest.id'), nullable=False, unique=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False, unique=False)
    invoice_date = db.Column(db.Date, nullable=False)
    invoice_amount = db.Column(db.Float, nullable=False)

class Dispute(db.Model):
    __tablename__ = 'dispute'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(UUID(as_uuid=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    dispute_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(255))

class FAQ(db.Model):
    __tablename__ = 'faq'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=True)
