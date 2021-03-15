from flask import render_template, url_for, flash, redirect, request
from handy import app, db, bcrypt, mail
from handy.models import User, Post, AppliedJop, HireWorker, Reviews
from handy.forms import (RegistrationForm, LoginForm, UpdateAccount, CreateRequestForm,
                         ApplyForJopForm, HireForm, AcceptanceRejection, RequestResetForm,
                         ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from PIL import Image
from handy.NLP_classifier import run, Modify
import os
import secrets
from googletrans import Translator

# posts = [
#     {
#         'Name' : 'John Wesley',
#         'Jop' : 'Carpenter',
#         'Rate' : '3.5',
#         'color' : 'green',
#         'State' : 'Online'
#     },
#     {
#         'Name' : 'Mikel Wesley',
#         'Jop' : 'Electrition',
#         'Rate' : '2.5',
#         'color' : 'red',
#         'State' : 'Offline'
#     },
#     {
#         'Name' : 'Sophie Wesley',
#         'Jop' : 'Plumber',
#         'Rate' : '4.5',
#         'color' : 'green',
#         'State' : 'Online'
#     }
# ]

def send_email(email, cont):
    msg = Message('Notification', sender='handi.services.2021@gmail.com', recipients=[email])
    msg.body = cont
    mail.send(msg)

@app.route("/")
@app.route("/home")
def home():
    
    if current_user.is_authenticated:
        if current_user.account_type != 'Client':
            data = Post.query.filter_by(major=current_user.major)
        else:
            data = User.query.filter_by(account_type='Handicraft', city=current_user.city)
        return render_template('home.html', data=data, check="specify")
    
    return render_template('home.html', check="general")

@app.route("/about")
def about():
    return render_template('about.html', title="About")

def save_picture(Picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(Picture.filename)
    picture_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics/', picture_name)
    image_size = (125, 125)
    image = Image.open(Picture)
    image.thumbnail(image_size)
    image.save(picture_path)
    return picture_name




@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            current_user.image_file = picture_name
        if current_user.account_type != 'Client':
            current_user.major = form.major.data
            current_user.description = form.description.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account info has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if current_user.account_type != 'Client':
            if not current_user.major:
                form.description.data = current_user.description
                flash('you are now in default major, please specify one major!!', 'danger')
            else:
                form.major.data = current_user.major
                form.description.data = current_user.description
        else:
            form.major.data = 'Client'
        

    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        flash('You can\'t register while you\'e already LOGEDIN!!, please logout first.', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, account_type=form.usertype.data, firstname=form.firstname.data, lastname=form.lastname.data, phone=form.phone.data, city=form.city.data, state=form.state.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Yout account has been created, you can now log in', 'success')
        return redirect(url_for('login'))
    else:
        flash('Please specify your account type!', 'danger')
    return render_template('registration.html', title="Register", form=form)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash('You can\'t login to another account while you\'e already LOGEDIN!!, please logout first.', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login error, please check your email and password!', 'danger')
    return render_template('login.html', title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/request/new/<string:action>", methods=['POST', 'GET'])
@login_required
def new_request(action):
        form = CreateRequestForm()
        major = ""
        result = []
        if action == "Request":
            if request.method == "POST":
                result = request.form
                jop_description = result['JopDesc']
                translator = Translator(service_urls=['translate.googleapis.com'])
                r = translator.translate(jop_description, dest="en")
                jop_description = r.text
                print(jop_description)
                _, major = run([jop_description])
                jop_description = r.origin
                r = translator.translate(major, dest="ar")
                major = r.text
                print(result)
                flash("Please Confirm your request, and check the category", "info")
                return redirect(url_for('new_request_final', action="Confirm", title=result['JopTitle'], major=major, desc=jop_description))
        return render_template('make_request.html', title='New Request', form=form, action=action)

@app.route("/request/new/<string:action>/<string:title>/<string:major>/<string:desc>", methods=['POST', 'GET'])
@login_required
def new_request_final(action, title, major, desc):
    translator = Translator(service_urls=['translate.googleapis.com'])
    form = CreateRequestForm()
    form.jop_description.data = desc
    form.jop_title.data = title
    if form.validate_on_submit():
        print(form.jop_major.data)
        r = translator.translate(form.jop_major.data, dest="en")
        form.jop_major.data = r.text
        print(r.text)
        if form.jop_major.data == major:
            print("Not error")
            post = Post(title=form.jop_title.data, content=form.jop_description.data, author=current_user, major=form.jop_major.data)
            db.session.add(post)
            db.session.commit()
            flash("The request had been created!", "success")
            return redirect(url_for('home'))
        else:
            print("error")
            Modify(form.jop_major.data, desc)
            post = Post(title=form.jop_title.data, content=form.jop_description.data, author=current_user, major=form.jop_major.data)
            db.session.add(post)
            db.session.commit()
            flash("The request had been created!", "success")
            return redirect(url_for('home'))

    return render_template('make_request.html', title='New Request', form=form, action=action, major=major, data={'JopTitle' : title, 'JopDesc' : desc})


@app.route("/request/<int:post_id>", methods=['POST', 'GET'])
@login_required
def Request(post_id):
    RequestPost = Post.query.get_or_404(post_id)
    form = ApplyForJopForm()
    AcceptanceRejectionForm = AcceptanceRejection()
    if form.validate_on_submit():
        for jop in current_user.jops:
            if jop.id == post_id:
                flash("You've already aplied", 'info')
                return redirect(url_for('Request', post_id=post_id))
        appliedjop = AppliedJop(worker_id=current_user.id, post_id=RequestPost.id)
        db.session.add(appliedjop)
        db.session.commit()
        flash("You've Applied for the jop, wait for the client response", 'success')
        email = RequestPost.author.email
        cont = f''' {current_user.username} has applied for your jop, check the following link for more inforemation {url_for('Request', post_id=post_id, _external=True)} '''
        send_email(email, cont)
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
    
    if request.method == "POST":
        result = request.form
        id = result['id']
        filtered = AppliedJop.query.filter_by(worker_id=result['id'], post_id=RequestPost.id).first()
        filtered.status = result['result']
        db.session.commit()
        flash(f"You've {result['result']} {User.query.get(id).username}", 'info')
        email = result['email']
        cont = f''' {current_user.username} has {result['result']} your ask for the jop, check the following link for more inforemation {url_for('dashboard', _external=True)} '''
        send_email(email, cont)
        return redirect(url_for('home'))
    return render_template('request.html', title=RequestPost.title, request=RequestPost, form=form, hireform=AcceptanceRejectionForm)


@app.route("/hire/<int:account_id>", methods=['POST', 'GET'])
def Hire(account_id):
    RequestAccount = User.query.get_or_404(account_id)
    form = HireForm()
    if form.validate_on_submit():
        for hire in current_user.Hires:
            if hire.worker_id == RequestAccount.id:
                flash("You've already aplied", 'info')
                return redirect(url_for('Hire', account_id=RequestAccount.id ))
        Hire_Worker = HireWorker(user_id=current_user.id, worker_id=RequestAccount.id)
        db.session.add(Hire_Worker)
        db.session.commit()
        flash("You've Hired the worker to the jop, wait for his response", 'success')
        email = RequestAccount.email
        cont = f''' {current_user.username} has hired you for a jop, check the following link for more inforemation {url_for('dashboard', _external=True)} '''
        send_email(email, cont)
        return redirect(url_for('home'))
    return render_template('hire.html', title=RequestAccount.username , hire=RequestAccount, form=form)

@app.route("/account/dashboard/my_jops/<int:jop_id>", methods=["POST", "GET"])
def MyJops(jop_id):
    for jop in current_user.jops:
        if jop.id == jop_id:
            if jop.status == "Rejected":
                flash("Unfortnatly you can't open that jop info, you've been rejected by the client", 'danger')
                return redirect(url_for('home'))
            elif jop.status == "Not revised":
                flash("Unfortnatly you can't open that jop info, your request hasn't revised yet", 'info')
                return redirect(url_for('home'))
            else:
                if request.method == "POST":
                    jop.status = 'Finished'
                    db.session.commit()
                    flash(f"you've finished {jop.jop.author.firstname}'s jop successfully", "success")
                    return redirect(url_for('MyJops', jop_id=jop.id))
                return render_template('jop.html', title="Dashboard", jop=jop)
    

@app.route("/account/dashboard")
@login_required
def dashboard():
    return render_template('dashboardExt.html', title="Dashboard", route='General')

@app.route("/account/dashboard/<string:route>", methods=['POST', 'GET'])
def dashboard_route(route):
    if request.method == 'POST':
        result = request.form
        post_id = int(result['post_id'])
        jop_id = int(result['jop_id'])
        rate = float(result['Rate'])
        review = result['review']
        for post in current_user.posts:
            if post.id == post_id:
                for jop in post.jops:
                    if jop.id == jop_id:
                        jop.status = 'Finished'
                        old = jop.author.rate
                        if old != 0:
                            rate = (old+rate)/2
                        else:
                            rate = rate
                        jop.author.rate = rate
                        db.session.commit()
                        
                        review = Reviews(Review=review, rate=rate, user_id=current_user.id, worker_id=jop.author.id)
                        db.session.add(review)
                        db.session.commit()

                        flash("Your problem has been fixed", "success")
                        return redirect(url_for('dashboard'))
    return render_template('dashboardExt.html', title=route, route=route, User=User, Reviews=Reviews, AppliedJop=AppliedJop)

def send_reset_email(user):
    token = user.reset_token()
    msg = Message('Password Reset Request', sender='handi.services.2021@gmail.com', recipients=[user.email])
    msg.body = f'''
To reset your password you've to visit the following link : 
{url_for('reset_password', token=token, _external=True)}
If you don't make that request just ignore this email
'''
    mail.send(msg)


@app.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset to your password", 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_token(token)
    if user is None:
        flash("That's an invaild token or expired!", 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title="Reset Password", form=form)