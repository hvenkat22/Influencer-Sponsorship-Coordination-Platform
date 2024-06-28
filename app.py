import random
from sqlalchemy import func, desc
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import User, Sponsor, Influencer, Campaign, AdRequest, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///InfluencerHub.db'
app.config['SECRET_KEY'] = 'X348AGHR8IQ2'
admin_key = '5T2E3#R%$!'
flag=False
paid=False
db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash("Please enter both username and password.")
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user']=user.username
            session['id']=user.id
            session['role']=user.role
            session['email']=user.email
            session['phone_number']=user.phone_number
            session['flagged']=user.flagged
            session['flagged_messages']=user.flagged_messages
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')


        if not username or not password or not role:
            flash("Please fill out all required fields.")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role=role, phone_number=phone_number, email=email, first_name=first_name, last_name=last_name, flagged='No', flagged_messages=None)
        db.session.add(new_user)
        db.session.commit()

        if role == 'sponsor':
            new_sponsor = Sponsor(user_id=new_user.id)
            db.session.add(new_sponsor)
            db.session.commit()
        elif role == 'influencer':
            new_influencer = Influencer(user_id=new_user.id)
            db.session.add(new_influencer)
            db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin_validation', methods=['GET', 'POST'])
def admin_validation():
    if request.method == 'POST':
        response = request.form['admin_key']
        username = session.get('user')
        if response != admin_key:
            flash("Invalid admin key")
            return redirect(url_for('admin_validation'))
        flash('Correct admin key!')
        global flag
        flag=True
        return redirect(url_for('home'))
    return render_template('admin_validation.html')

@app.route('/')
def home():
    role = session.get('role', 'guest')
    username = session.get('user', 'Guest')
    flagged = session.get('flagged')
    flagged_messages = session.get('flagged_messages')
    user_id = session.get('id')
    email = session.get('email')
    phone_number = session.get('phone_number')
    first_name = db.session.query(User.first_name).filter_by(username=username).first()
    last_name = db.session.query(User.last_name).filter_by(username=username).first()
    

    influencers = db.session.query(User, Influencer).join(Influencer, Influencer.user_id == User.id).filter(User.role == 'influencer').all()
    influencer_data = []
    for user, influencer in influencers:
        influencer_info = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'niche': influencer.niche,
            'category': influencer.category,
            'reach': influencer.reach
        }
        influencer_data.append(influencer_info)


    if role == 'admin':
        if not flag:
            return render_template('admin_validation.html')

        sponsors = db.session.query(User, Sponsor).join(Sponsor, Sponsor.user_id == User.id).filter(User.role == 'sponsor').all()

        sponsor_data = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'company_name': sponsor.company_name,
                'industry': sponsor.industry,
                'budget': sponsor.budget,
                'flagged':user.flagged
            }
            for user, sponsor in sponsors
        ]
        influencers = db.session.query(User, Influencer).join(Influencer, Influencer.user_id == User.id).filter(User.role == 'influencer').all()

        influencer_data = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'niche': influencer.niche,
                'category': influencer.category,
                'reach': influencer.reach,
                'flagged':user.flagged
            }
            for user, influencer in influencers
        ]
        active_campaigns = Campaign.query.filter(Campaign.end_date >= datetime.today().date()).all()
        active_campaigns = [
            {
                'id': campaign.id,
                'name': campaign.name,
                'sponsor_first_name': db.session.query(User.first_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().first_name,
                'sponsor_last_name': db.session.query(User.last_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().last_name,
                'description': campaign.description,
                'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                'budget': campaign.budget,
                'visibility': campaign.visibility,
                'goals': campaign.goals,
                'flagged':campaign.flagged
            }
            for campaign in active_campaigns
        ]

        inactive_campaigns = Campaign.query.filter(Campaign.end_date < datetime.today().date()).all()
        inactive_campaigns = [
            {
                'id': campaign.id,
                'name': campaign.name,
                'sponsor_first_name': db.session.query(User.first_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().first_name,
                'sponsor_last_name': db.session.query(User.last_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().last_name,
                'description': campaign.description,
                'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                'budget': campaign.budget,
                'visibility': campaign.visibility,
                'goals': campaign.goals
            }
            for campaign in inactive_campaigns
        ]

        all_adrequests = AdRequest.query.all()
        all_adrequests = [
            {
                'id': adrequest.id,
                'influencer_first_name': db.session.query(User).join(Influencer, User.id == Influencer.user_id).join(AdRequest, Influencer.id == adrequest.influencer_id).first().first_name,
                'influencer_last_name': db.session.query(User).join(Influencer, User.id == Influencer.user_id).join(AdRequest, Influencer.id == adrequest.influencer_id).first().last_name,
                'sponsor_first_name': db.session.query(User).join(Sponsor, User.id == Sponsor.user_id).join(AdRequest, Sponsor.id == adrequest.sponsor_id).first().first_name,
                'sponsor_last_name': db.session.query(User).join(Sponsor, User.id == Sponsor.user_id).join(AdRequest, Sponsor.id == adrequest.sponsor_id).first().last_name,
                'campaign_name': Campaign.query.filter_by(id=adrequest.campaign_id).first().name,
                'messages': adrequest.messages,
                'requirements': adrequest.requirements,
                'payment_amount': adrequest.payment_amount,
                'status': adrequest.status,
            }
            for adrequest in all_adrequests
        ]

        return render_template('home.html', role=role, uname=username, sponsorlist=sponsor_data, influencerlist=influencer_data, email=email, phone_number=phone_number, active_campaigns=active_campaigns, inactive_campaigns = inactive_campaigns, fname=first_name[0], lname=last_name[0], adrequestlist = all_adrequests)
    
    elif role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=User.query.filter_by(username=username).first().id).first()
        company_name = sponsor.company_name
        industry = sponsor.industry
        budget = sponsor.budget
        if not sponsor.company_name or not sponsor.industry or not sponsor.budget:
            flash('Please complete your sponsor profile.')
            return redirect(url_for('sponsor_setup'))
        
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        campaign_list = [
            {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'start_date': campaign.start_date.date(),
                'end_date': campaign.end_date.date(),
                'budget': campaign.budget,
                'visibility': campaign.visibility,
                'goals': campaign.goals,
                'flagged':campaign.flagged
            }
            for campaign in campaigns
        ]
        
        adrequests = AdRequest.query.filter_by(sponsor_id=sponsor.id).all()
        adrequest_list = [
            {
                'id': adrequest.id,
                'influencer_first_name': db.session.query(User).join(Influencer, User.id == Influencer.user_id).join(AdRequest, Influencer.id == adrequest.influencer_id).first().first_name,
                'influencer_last_name': db.session.query(User).join(Influencer, User.id == Influencer.user_id).join(AdRequest, Influencer.id == adrequest.influencer_id).first().last_name,
                'campaign_name': Campaign.query.filter_by(id=adrequest.campaign_id).first().name,
                'messages': adrequest.messages,
                'requirements': adrequest.requirements,
                'payment_amount': adrequest.payment_amount,
                'status': adrequest.status,
                'new_payment_amount':adrequest.temp
            }
            for adrequest in adrequests
        ]
        
        return render_template('home.html', flagged_messages=flagged_messages, today_date = datetime.today().date(), role=role, uname=username, campaigns=campaign_list, adrequests=adrequest_list, c_name=company_name, email=email, phone_number=phone_number, industry=industry, budget=budget, fname=first_name[0], lname=last_name[0],flagged=flagged,id=user_id)
    
    elif role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=User.query.filter_by(username=username).first().id).first()
        if not influencer.category or not influencer.niche or not influencer.reach:
            flash('Please complete your Influencer profile.')
            return redirect(url_for('influencer_setup'))
        adreceives = AdRequest.query.filter_by(influencer_id=influencer.id).all()
        adreceives_list = [
            {
                'id': req.id,
                'sponsor_first_name': db.session.query(User).join(Sponsor, User.id == Sponsor.user_id).join(AdRequest, Sponsor.id == req.sponsor_id).first().first_name,
                'sponsor_last_name': db.session.query(User).join(Sponsor, User.id == Sponsor.user_id).join(AdRequest, Sponsor.id == req.sponsor_id).first().last_name,
                'campaign_name': Campaign.query.filter_by(id=req.campaign_id).first().name,
                'messages': req.messages,
                'requirements': req.requirements,
                'payment_amount': req.payment_amount,
                'status':req.status
            }
            for req in adreceives
        ]
        return render_template('home.html', flagged_messages=flagged_messages, role=role, uname=username, category=influencer.category, niche=influencer.niche,reach=influencer.reach, email=email, phone_number=phone_number, adreceives=adreceives_list, fname=first_name[0], lname=last_name[0], flagged=flagged, id=user_id)

    return render_template('home.html', role=role, uname=username)

@app.route('/logout')
def logout():
    session.clear()
    global flag
    flag=False
    return redirect(url_for('home'))

@app.route('/profile_edit', methods=['GET','POST'])
def profile_edit():
    if request.method == 'POST':
        username = session.get('user')
        role = session.get('role')
        if role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=User.query.filter_by(username=username).first().id).first()
            influencer.niche = request.form['niche']
            influencer.reach = request.form['reach']

            if int(influencer.reach) < 1000:
                influencer.category = 'nano_influencer'
            elif int(influencer.reach) >=1000 and int(influencer.reach) < 100000:
                influencer.category = 'micro_influencer'
            elif int(influencer.reach) >= 100000 and int(influencer.reach) < 500000:
                influencer.category = 'mid-tier_influencer'
            elif int(influencer.reach) >= 500000 and int(influencer.reach) < 1000000:
                influencer.category = 'macro_influencer'
            else:
                influencer.category = 'mega_influencer'
        
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('profile_edit.html')


@app.route('/sponsor_setup', methods=['GET', 'POST'])
def sponsor_setup():
    if request.method == 'POST':
        company_name = request.form['company_name']
        industry = request.form['industry']
        budget = request.form['budget']
        username = session.get('user')
        
        user = User.query.filter_by(username=username).first()
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        sponsor.company_name = company_name
        sponsor.industry = industry
        sponsor.budget = budget
        db.session.commit()

        flash("Sponsor profile setup complete!")
        return redirect(url_for('home'))
    return render_template('sponsor_setup.html')

@app.route('/influencer_setup', methods=['GET', 'POST'])
def influencer_setup():
    if request.method == 'POST':
        category = request.form['category']
        niche = request.form['niche']
        reach = request.form['reach']
        username = session.get('user')
        
        user = User.query.filter_by(username=username).first()
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        influencer.category = category
        influencer.niche = niche
        influencer.reach = reach
        db.session.commit()

        flash("Influencer profile setup complete!")
        return redirect(url_for('home'))
    return render_template('influencer_setup.html')

@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        username = session.get('user')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('create_campaign'))
        
        if username is None:
            flash('Username is missing. Please log in again.')
            return redirect(url_for('home'))
        
        user = User.query.filter_by(username=username).first()
        sponsor = Sponsor.query.filter_by(user_id = user.id).first()
        if sponsor is None or user.role!= 'sponsor':
            flash('Invalid user or user is not a sponsor.')
            return redirect(url_for('home'))

        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            sponsor_id=sponsor.id,
            flagged='No',
            flagged_messages=None
        )
        try:
            db.session.add(new_campaign)
            db.session.commit()
            flash('Campaign created successfully!')
            return redirect(url_for('home'))
        except Exception as e:
            print(f'Error creating campaign: {e}')
            return redirect(url_for('home'))

    return render_template('create_campaign.html')

@app.route('/search_campaigns', methods=['GET', 'POST'])
def search_campaigns():
    result = []
    searched = False
    today_date = datetime.today().date()
    user_id = User.query.filter_by(username=session.get('user')).first().id
    influencer = Influencer.query.filter_by(user_id=user_id).first()
    ad_requests_sent = AdRequest.query.filter_by(influencer_id=influencer.id).all()

    if request.method == 'POST':
        searched = True
        search_type = request.form.get('type')
        query = request.form.get('query')

        if search_type == 'by_name':
            campaigns = Campaign.query.filter(
                        Campaign.name.ilike(f'%{query}%'),
                        Campaign.end_date >= today_date,
                        Campaign.visibility == 'public').all()
            result = [
                {
                    'id': campaign.id,
                    'name': campaign.name,
                    'company_name': Sponsor.query.get(campaign.sponsor_id).company_name,
                    'budget': campaign.budget,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'niche/industry':Sponsor.query.get(campaign.sponsor_id).industry
                }
                for campaign in campaigns
            ]
        elif search_type == 'by_niche':
            campaigns = Campaign.query.join(Sponsor).filter(
                        Sponsor.industry.ilike(f'%{query}%'),
                        Campaign.end_date >= today_date,
                        Campaign.visibility == 'public').all()

            result = [
                {
                    'id': campaign.id,
                    'name': campaign.name,
                    'company_name': Sponsor.query.get(campaign.sponsor_id).company_name,
                    'budget': campaign.budget,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'niche/industry':Sponsor.query.get(campaign.sponsor_id).industry
                }
                for campaign in campaigns
            ]
    return render_template('search_campaigns.html', result=result, searched=searched, ad_requests_sent=ad_requests_sent)

@app.route('/edit_campaign/<int:id>', methods=['GET', 'POST'])
def edit_campaign(id):
    campaign = Campaign.query.filter(Campaign.id == id).first()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        campaign.name=name
        campaign.description=description
        campaign.start_date=start_date
        campaign.end_date=end_date
        campaign.budget=budget
        campaign.visibility=visibility
        campaign.goals=goals

        try:
            db.session.commit()
        except Exception as e:
            print(f'Error updating campaign: {e}')
            return redirect(url_for('home'))
        flash('Campaign updated successfully!')
        return redirect(url_for('home'))
    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = db.session.query(Campaign).filter_by(id=campaign_id).first()
    adrequests = db.session.query(AdRequest).filter_by(campaign_id=campaign_id).all()
    if campaign:
        for adrequest in adrequests:
            db.session.delete(adrequest)

        db.session.delete(campaign)
        db.session.commit()
        flash(f'Campaign "{campaign.name}" has been deleted.', 'success')
    else:
        flash('Campaign not found.', 'danger')
    
    return redirect(url_for('home'))

@app.route('/delete_adrequest/<int:adrequest_id>', methods=['POST'])
def delete_adrequest(adrequest_id):
    adrequest = db.session.query(AdRequest).filter_by(id=adrequest_id).first()
    if adrequest:
        db.session.delete(adrequest)
        db.session.commit()
    else:
        flash('AdRequest not found.', 'danger')
    
    return redirect(url_for('home'))

@app.route('/edit_adrequest/<int:id>', methods=['GET', 'POST'])
def edit_adrequest(id):
    adrequest = AdRequest.query.filter(AdRequest.id == id).first()
    if request.method == 'POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')

        adrequest.messages = messages
        adrequest.requirements = requirements
        adrequest.payment_amount = payment_amount

        try:
            db.session.commit()
        except Exception as e:
            print(f'Error updating adrequest: {e}')
            return redirect(url_for('home'))
        flash('AdRequest updated successfully!')
        return redirect(url_for('home'))
    return render_template('edit_adrequest.html', adrequest=adrequest)

@app.route('/search_influencers', methods=['GET', 'POST'])
def search_influencers():
    result = []
    today_date = datetime.today().date()
    searched = False
    campaigns = None

    if request.method == 'POST':
        searched = True
        user_id = User.query.filter_by(username=session.get('user')).first().id
        search_type = request.form.get('type')
        query = request.form.get('query')

        if search_type in ['by_user', 'by_niche', 'by_category']:
            influencers_query = db.session.query(User, Influencer)\
                .join(Influencer, User.id == Influencer.user_id)\
                .filter(User.role == 'influencer')

            if search_type == 'by_user':
                influencers_query = influencers_query.filter(User.username.ilike(f'{query}%'))
            elif search_type == 'by_niche':
                influencers_query = influencers_query.filter(Influencer.niche.ilike(f'%{query}%'))
            elif search_type == 'by_category':
                category = request.form.get('category')
                influencers_query = influencers_query.filter(Influencer.category.ilike(f'%{category}%'))

            influencers = influencers_query.all()

            for user, influencer in influencers:
                result.append([
                    influencer.id,
                    user.first_name,
                    user.last_name, 
                    user.username,
                    influencer.niche,
                    influencer.category,
                    influencer.reach,
                    user.phone_number,
                    user.email
                ])

        sponsor = Sponsor.query.filter_by(user_id=user_id).first()
        if sponsor:
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).filter(Campaign.end_date >= today_date).all()

    return render_template('search_influencers.html', result=result, searched=searched, campaigns=campaigns, today_date=today_date)


@app.route('/send_adrequest', methods=['GET', 'POST'])
def send_adrequest():
    if request.method == 'GET':
        influencer_id = request.args.get('influencer_id')
        campaign_id = request.args.get('campaign_id')

        influencer = User.query.filter_by(id=influencer_id).first()
        influencer_info = Influencer.query.filter_by(user_id=influencer_id).first()

        return render_template('send_adrequest.html', influencer=influencer, influencer_info=influencer_info, campaign_id=campaign_id)

    if request.method == 'POST':
        influencer_id = request.form['influencer_id']
        campaign_id = request.form['campaign_id']
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        username = session.get('user')
        user = User.query.filter_by(username=username).first()
        sponsor_id = Sponsor.query.filter_by(user_id=user.id).first().id

        ad_request = AdRequest(
            influencer_id=influencer_id,
            sponsor_id=sponsor_id, 
            campaign_id=campaign_id, 
            messages=messages, 
            requirements=requirements, 
            payment_amount=payment_amount,
            status='Pending',
            temp=0,
            payment_received_date=None
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad Request sent successfully!')
        return redirect(url_for('home'))

    return render_template('send_adrequest.html', influencer=influencer, influencer_info=influencer_info)

@app.route('/accept_adrequest', methods=['POST'])
def accept_adrequest():
    adrequest_id = request.form.get('adrequest_id')
    adrequest = AdRequest.query.get(adrequest_id)
    if adrequest:
        adrequest.status = 'accepted'
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/reject_adrequest', methods=['POST'])
def reject_adrequest():
    adrequest_id = request.form.get('adrequest_id')
    adrequest = AdRequest.query.get(adrequest_id)
    if adrequest:
        adrequest.status = 'rejected'
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/negotiate_adrequest', methods=['POST'])
def negotiate_adrequest():
    adrequest_id = request.form.get('adrequest_id')
    new_payment_amount = request.form.get('new_payment_amount')
    adrequest = AdRequest.query.filter_by(id=adrequest_id).first()
    if adrequest:
        adrequest.status = 'negotiating'
        adrequest.temp=new_payment_amount
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/payment_page/<int:adrequest_id>', methods=['GET', 'POST'])
def payment_page(adrequest_id):
    if request.method == 'POST':
        return redirect(url_for('payment_completion',adrequest_id=adrequest_id))
    return render_template('payment_page.html')

@app.route('/payment_completion/<int:adrequest_id>', methods=['GET', 'POST'])
def payment_completion(adrequest_id):
    idpay = random.randint(1, 10000000)
    update_ad_request_status(adrequest_id)
    return render_template('payment_completion.html', payment_id=idpay)

def update_ad_request_status(ad_request_id):
    ad_request = db.session.query(AdRequest).filter_by(id=ad_request_id).first()
    if ad_request and ad_request.status != 'paid':
        ad_request.status = 'paid'
        ad_request.payment_received_date = datetime.today().date()
        db.session.commit()

@app.route('/influencer_stats', methods=['GET','POST'])
def influencer_stats():
    username = session.get('user')
    user_id = db.session.query(User).filter_by(username=username).first().id
    influencer_id = db.session.query(Influencer).filter(Influencer.user_id == user_id).first().id
    accepted = AdRequest.query.filter(AdRequest.status == 'accepted').filter(AdRequest.influencer_id == influencer_id).count()
    rejected = AdRequest.query.filter(AdRequest.status == 'rejected').filter(AdRequest.influencer_id == influencer_id).count()
    paid = AdRequest.query.filter(AdRequest.status == 'paid').filter(AdRequest.influencer_id == influencer_id).count()
    negotiating = AdRequest.query.filter(AdRequest.status == 'negotiating').filter(AdRequest.influencer_id == influencer_id).count()
    pending = AdRequest.query.filter(AdRequest.status == 'Pending').filter(AdRequest.influencer_id == influencer_id).count()

    top_sponsors = db.session.query(
    User.first_name,
    User.last_name,
    func.count(AdRequest.id).label('paid_ad_requests')
    ).select_from(
    User
    ).join(
    Sponsor
    ).join(
    AdRequest
    ).filter(
    AdRequest.status == 'paid'
    ).group_by(
    User.first_name,
    User.last_name
    ).order_by(
    func.count(AdRequest.id).desc()
    ).limit(5).all()
    
    sponsor_names=[]
    ads_num=[]
    for element in top_sponsors:
        sponsor_names.append(str(element[0])+' '+str(element[1]))
        ads_num.append(int(element[2]))

    top_campaigns = db.session.query(
        Campaign.name,
        User.first_name,
        User.last_name,
        func.sum(AdRequest.payment_amount).label('total_spent')
    ).join(Sponsor, Sponsor.id == Campaign.sponsor_id)\
    .join(User, User.id == Sponsor.user_id)\
    .join(AdRequest, AdRequest.campaign_id == Campaign.id)\
    .group_by(Campaign.id, User.first_name, User.last_name)\
    .order_by(desc(func.sum(AdRequest.payment_amount))).limit(5).all()

    campaign_labels = []
    total_spent = []

    for campaign in top_campaigns:
        campaign_labels.append(f"{campaign.name} ({campaign.first_name} {campaign.last_name})")
        total_spent.append(campaign.total_spent)

    duration_data = db.session.query(
        Sponsor.company_name,
        User.first_name,
        User.last_name,
        func.avg(func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date)).label('average_duration')
    ).join(Campaign).group_by(Sponsor.company_name).join(User, User.id == Sponsor.user_id).all()

    company_names = []
    average_durations = []

    for data in duration_data:
        company_names.append(f"{data.company_name} ({data.first_name} {data.last_name})")
        average_durations.append(data.average_duration)

    revenue_data = db.session.query(
        func.strftime('%Y-%m-%d', AdRequest.payment_received_date).label('date'),
        func.sum(AdRequest.payment_amount).label('total_revenue')
    ).filter(
        AdRequest.influencer_id == influencer_id,
        AdRequest.status == 'paid'
    ).group_by(func.strftime('%Y-%m-%d', AdRequest.payment_received_date)).order_by(func.strftime('%Y-%m-%d', AdRequest.payment_received_date)).all()

    cumulative_revenues = []
    linechart_dates=[]
    linechart_revenues=[]
    cumulative_sum = 0
    for row in revenue_data:
        cumulative_sum += row.total_revenue
        cumulative_revenues.append((row.date, cumulative_sum))
    for row in cumulative_revenues:
        linechart_dates.append(row[0])
        linechart_revenues.append(row[1])


    
    return render_template('influencer_stats.html', accepted=accepted,rejected=rejected,paid=paid,negotiating=negotiating,pending=pending,
                            sponsor_names=sponsor_names, ads_num=ads_num,campaign_names=campaign_labels,total_spent=total_spent, company_names=company_names, 
                           average_durations=average_durations, linechart_dates=linechart_dates, linechart_revenues=linechart_revenues)

@app.route('/sponsor_stats', methods=['GET','POST'])
def sponsor_stats():
    username = session.get('user')
    user_id = db.session.query(User).filter_by(username=username).first().id
    sponsor_id = db.session.query(Sponsor).filter(Sponsor.user_id == user_id).first().id
    today_date = datetime.today().date()
    active_count = Campaign.query.filter(Campaign.end_date >= today_date).filter(Campaign.sponsor_id == sponsor_id).count()
    inactive_count =Campaign.query.filter(Campaign.end_date < today_date).filter(Campaign.sponsor_id == sponsor_id).count()

    accepted = AdRequest.query.filter(AdRequest.status == 'accepted').filter(AdRequest.sponsor_id == sponsor_id).count()
    rejected = AdRequest.query.filter(AdRequest.status == 'rejected').filter(AdRequest.sponsor_id == sponsor_id).count()
    paid = AdRequest.query.filter(AdRequest.status == 'paid').filter(AdRequest.sponsor_id == sponsor_id).count()
    negotiating = AdRequest.query.filter(AdRequest.status == 'negotiating').filter(AdRequest.sponsor_id == sponsor_id).count()
    pending = AdRequest.query.filter(AdRequest.status == 'Pending').filter(AdRequest.sponsor_id == sponsor_id).count()

    top_influencers = db.session.query(User.first_name, User.last_name)\
    .join(Influencer)\
    .order_by(desc(Influencer.reach))\
    .limit(5)\
    .all()

    reachs = db.session.query(Influencer.reach).order_by(desc(Influencer.reach)).limit(5).all()

    influencer_names=[]
    influencer_reachs=[]
    for f_name, l_name in top_influencers:
        influencer_names.append(str(f_name)+' '+str(l_name))

    for element in reachs:
        influencer_reachs.append(element.reach)


    budget_utilization = db.session.query(
        Campaign.name,
        Campaign.budget,
        func.sum(AdRequest.payment_amount).label('spent')
    ).join(AdRequest, AdRequest.campaign_id == Campaign.id, isouter=True).filter(
        Campaign.sponsor_id == sponsor_id
    ).group_by(Campaign.id).all()

    campaign_names = []
    allocated_budgets = []
    spent_budgets = []

    for campaign in budget_utilization:
        campaign_names.append(campaign.name)
        allocated_budgets.append(campaign.budget)
        spent_budgets.append(campaign.spent if campaign.spent else 0)


    return render_template('sponsor_stats.html', active=active_count, inactive=inactive_count, accepted=accepted, rejected=rejected, negotiating=negotiating, paid=paid, pending=pending,
                           campaign_names=campaign_names, allocated_budgets=allocated_budgets, spent_budgets=spent_budgets, influencer_names=influencer_names, influencer_reachs=influencer_reachs)

@app.route('/all_stats', methods=['GET', 'POST'])
def all_stats():
    today_date = datetime.today().date()
    nano_count = Influencer.query.filter(Influencer.category=='nano_influencer').count()
    micro_count = Influencer.query.filter(Influencer.category=='micro_influencer').count()
    mid_tier_count = Influencer.query.filter(Influencer.category=='mid-tier_influencer').count()
    macro_count = Influencer.query.filter(Influencer.category=='macro_influencer').count()
    mega_count = Influencer.query.filter(Influencer.category=='mega_influencer').count()

    accepted = AdRequest.query.filter(AdRequest.status == 'accepted').count()
    rejected = AdRequest.query.filter(AdRequest.status == 'rejected').count()
    paid = AdRequest.query.filter(AdRequest.status == 'paid').count()
    negotiating = AdRequest.query.filter(AdRequest.status == 'negotiating').count()
    pending = AdRequest.query.filter(AdRequest.status == 'Pending').count()

    active_count = Campaign.query.filter(Campaign.end_date >= today_date).count()
    inactive_count = Campaign.query.filter(Campaign.end_date < today_date).count()

    top_influencers = db.session.query(User.first_name, User.last_name)\
    .join(Influencer)\
    .order_by(desc(Influencer.reach))\
    .limit(5)\
    .all()

    reachs = db.session.query(Influencer.reach).order_by(desc(Influencer.reach)).limit(5).all()

    influencer_names=[]
    influencer_reachs=[]
    for f_name, l_name in top_influencers:
        influencer_names.append(str(f_name)+' '+str(l_name))

    for element in reachs:
        influencer_reachs.append(element.reach)

    
    top_sponsors = db.session.query(
    User.first_name,
    User.last_name,
    func.count(AdRequest.id).label('paid_ad_requests')
    ).select_from(
    User
    ).join(
    Sponsor
    ).join(
    AdRequest
    ).filter(
    AdRequest.status == 'paid'
    ).group_by(
    User.first_name,
    User.last_name
    ).order_by(
    func.count(AdRequest.id).desc()
    ).limit(5).all()
    
    sponsor_names=[]
    ads_num=[]
    for element in top_sponsors:
        sponsor_names.append(str(element[0])+' '+str(element[1]))
        ads_num.append(int(element[2]))
    

    top_campaigns = db.session.query(
        Campaign.name,
        User.first_name,
        User.last_name,
        func.sum(AdRequest.payment_amount).label('total_spent')
    ).join(Sponsor, Sponsor.id == Campaign.sponsor_id)\
    .join(User, User.id == Sponsor.user_id)\
    .join(AdRequest, AdRequest.campaign_id == Campaign.id)\
    .group_by(Campaign.id, User.first_name, User.last_name)\
    .order_by(desc(func.sum(AdRequest.payment_amount))).limit(5).all()

    campaign_labels = []
    total_spent = []

    for campaign in top_campaigns:
        campaign_labels.append(f"{campaign.name} ({campaign.first_name} {campaign.last_name})")
        total_spent.append(campaign.total_spent)

    duration_data = db.session.query(
        Sponsor.company_name,
        User.first_name,
        User.last_name,
        func.avg(func.julianday(Campaign.end_date) - func.julianday(Campaign.start_date)).label('average_duration')
    ).join(Campaign).group_by(Sponsor.company_name).join(User, User.id == Sponsor.user_id).all()

    company_names = []
    average_durations = []

    for data in duration_data:
        company_names.append(f"{data.company_name} ({data.first_name} {data.last_name})")
        average_durations.append(data.average_duration)

    
    
    return render_template('all_stats.html', 
                           nano_count=nano_count, 
                           micro_count=micro_count, 
                           mid_tier_count=mid_tier_count, 
                           macro_count=macro_count, 
                           mega_count=mega_count, 
                           accepted=accepted, rejected=rejected, 
                           paid=paid, negotiating=negotiating, 
                           pending=pending, active=active_count, 
                           inactive = inactive_count, influencer_names=influencer_names, influencer_reachs=influencer_reachs, campaign_names=campaign_labels,total_spent=total_spent,
                           company_names=company_names, average_durations=average_durations,sponsor_names=sponsor_names, ads_num=ads_num)

@app.route('/flag_user',methods=['GET','POST'])
def flag_user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    user.flagged = 'Yes'
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/flag_campaign',methods=['GET','POST'])
def flag_campaign():
    campaign_id = request.args.get('campaign_id')
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.flagged = 'Yes'
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/flagged_page',methods=['GET','POST'])
def flagged_page():
    flagged_campaigns = Campaign.query.filter_by(flagged='Yes').all()
    flagged_inf = db.session.query(User, Influencer).join(Influencer, Influencer.user_id == User.id).filter(User.role == 'influencer').filter(User.flagged == 'Yes').all()
    flagged_influencers = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'influencer_name':str(user.first_name)+' '+str(user.last_name),
            'phone_number':user.phone_number,
            'category':influencer.category,
            'niche':influencer.niche,
            'reach':influencer.reach,
            'flagged_messages':user.flagged_messages

        }
        for user, influencer in flagged_inf
    ]
    flagged_spon = db.session.query(User, Sponsor).join(Sponsor, Sponsor.user_id == User.id).filter(User.role == 'sponsor').filter(User.flagged == 'Yes').all()
    flagged_sponsors = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'sponsor_name':str(user.first_name)+ ' '+str(user.last_name),
            'phone_number':user.phone_number,
            'company_name':sponsor.company_name,
            'industry':sponsor.industry,
            'budget':sponsor.budget,
            'flagged_messages':user.flagged_messages

        }
        for user, sponsor in flagged_spon
    ]

    flagged_camp = [
            {
                'id': campaign.id,
                'name': campaign.name,
                'sponsor_first_name': db.session.query(User.first_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().first_name,
                'sponsor_last_name': db.session.query(User.last_name).join(Sponsor, User.id == Sponsor.user_id).filter(Sponsor.id == campaign.sponsor_id).first().last_name,
                'description': campaign.description,
                'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                'budget': campaign.budget,
                'visibility': campaign.visibility,
                'goals': campaign.goals,
                'flagged_messages':campaign.flagged_messages
            }
            for campaign in flagged_campaigns
    ]
    return render_template('flagged_page.html',flagged_campaigns=flagged_camp, flagged_sponsors=flagged_sponsors, flagged_influencers=flagged_influencers)

@app.route('/send_flag_message', methods=['POST'])
def send_flag_message():
    user_id = request.form.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    user.flagged_messages = request.form.get('flagged_message')
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/unflag_user/<int:user_id>', methods=['GET','POST'])
def unflag_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.flagged = 'No'
    user.flagged_messages=None
    db.session.commit()
    return redirect(url_for('flagged_page'))

@app.route('/send_campaign_flag_message', methods=['POST'])
def send_campaign_flag_message():
    campaign_id = request.form.get('campaign_id')
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.flagged_messages = request.form.get('flagged_campaign_message')
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/unflag_campaign/<int:campaign_id>', methods=['GET','POST'])
def unflag_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.flagged = 'No'
    campaign.flagged_messages=None
    db.session.commit()
    return redirect(url_for('flagged_page'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
