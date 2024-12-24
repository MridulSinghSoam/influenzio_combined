from flask import Flask, request,render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    name = db.Column(db.String(100), nullable=False, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/influencer-register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['fname']
        email = request.form['email']
        password = request.form['pass']
        user = User.query.filter_by(email=email).first()
        if user:
           return render_template('signup.html')
        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/influencer-login')
    


    return render_template('signup.html')

@app.route('/influencer-login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('influencer_dashboard.html',user=user)
    
    return redirect('/login')

@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def error(e):
    return render_template('500.html'), 500
if __name__ == '__main__':
    app.run(debug=True)