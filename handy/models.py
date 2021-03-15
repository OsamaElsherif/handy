from handy import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as serializer
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        pass

class User(db.Model, UserMixin):
    default = " I am an Handicraft who search about any jop here, I'm new here; so if you want any help in my major so please contact me"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    account_type = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    major = db.Column(db.String(), nullable=False, default='General')
    rate = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False, default=default)
    posts = db.relationship('Post', backref='author', lazy=True)
    jops = db.relationship('AppliedJop', backref='author', lazy=True)
    Hires = db.relationship('HireWorker', backref='author', lazy=True)
    reviews = db.relationship('Reviews', backref='author', lazy=True)

    def reset_token(self, expires_sec=1800):
        s = serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id' : self.id}).decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        s = serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.account_type}', '{self.rate}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    major = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jops = db.relationship('AppliedJop', backref='jop', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}')"


class AppliedJop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False, default='Not revised')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Jop('{self.author.username}, {self.jop.author.username}, {self.status}')"

class HireWorker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False, default='No Response')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Hire('{self.author.username}, {self.worker_id}, {self.status}')"

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Review = db.Column(db.String(), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker_id = db.Column(db.Integer, nullable=False) 

    def __repr__(self):
        return f"Review('{self.author.username}, {self.worker_id}, {self.Review}')"

