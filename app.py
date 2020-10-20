from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import sys
import urllib.parse
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField

db_name = 'konta.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = open('secret_key', 'rb').read()
login = LoginManager(app)

def currency_to_string(amount, precision = 2):
    try:
        return "{:.{}f}".format(amount, precision)
    except:
        raise Exception('ConvertToStringException')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<House {}>'.format(self.id)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=True)
    debt = db.Column(db.Float, default=0.0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Member {}>'.format(self.id)

    def pay(self, amount):
        self.debt -= float(amount)

    def charge_bill(self, amount):
        self.debt += float(amount)

    def get_debt(self):
        return currency_to_string(self.debt)

    def get_int_debt(self):
        return str(round(self.debt))

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Bill {}>'.format(self.id)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Log {}>'.format(self.id)

    @staticmethod
    def pay(name, amount):
        desc = name + ' paid €' + currency_to_string(amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('PayLogException')

    @staticmethod
    def new_bill(bill):
        desc = 'Added bill ' + bill.description + ' of €' + currency_to_string(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewBillLogException')

    @staticmethod
    def delete_bill(bill):
        desc = 'Deleted bill ' + bill.description + ' of €' + currency_to_string(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('DeleteBillLogException')

    @staticmethod
    def update_bill(bill):
        desc = 'Updated bill ' + bill.description + ' of €' + currency_to_string(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('UpdateBillLogException')

    @staticmethod
    def new_member(member):
        desc = 'Added member ' + member.name + ' with debt of €' + currency_to_string(member.debt)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewMemberLogException')

    @staticmethod
    def delete_member(member):
        desc = 'Deleted member ' + member.name + ' with debt of €' + member.get_debt()
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewMemberLogException')

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Submit')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout/', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login/')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    members = Member.query.order_by(Member.date_created).all()
    return render_template('index.html', members=members)

@app.route('/add_house/', methods=['GET', 'POST'])
@login_required
def add_house():
    houses = House.query.order_by(House.date_created).all()
    return render_template('add_house.html', houses=houses)

@app.route('/update_/<int:id>', methods=['GET', 'POST'])
@login_required
def update_house(id):
    house_to_update = House.query.get_or_404(id)

    if request.method == 'POST':
        house_to_update.name = request.form.get('name')
        house_to_update.mail = request.form.get('mail')

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating that house.'
    else:
        return render_template('update_house.html', house=house_to_update)

def italian_month(num):
    ita_months = {
            1  : 'Gennaio',
            2  : 'Febbraio',
            3  : 'Marzo',
            4  : 'Aprile',
            5  : 'Maggio',
            6  : 'Giugno',
            7  : 'Luglio',
            8  : 'Agosto',
            9  : 'Settembre',
            10 : 'Ottobre',
            11 : 'Novembre',
            12 : 'Dicembre'
    }
    return ita_months.get(num, 'Error.')

@app.route('/email/', methods=['GET'])
@login_required
def email():
    members = Member.query.order_by(Member.date_created).all()
    now = datetime.now()
    recipients = ''
    for m in members:
        recipients += m.mail + ','
    month = int(now.strftime('%-m'))
    subject = 'Affitto + Bollette ' + italian_month(month) + now.strftime(' %Y')
    body = '\n\nBills payment updated at ' + now.strftime('%c') + '\n'
    for m in members:
        body += m.name + ' €' + m.get_int_debt() + '\n'
    body += '\n\n'
    recipients = urllib.parse.quote(recipients)
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    return redirect('mailto:' + recipients +
                    '?subject=' + subject +
                    '&body=' + body)

@app.route('/pay_member/<int:id>', methods=['GET', 'POST'])
@login_required
def pay_member(id):
    member = Member.query.get_or_404(id)

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        try:
            member.pay(amount)
            db.session.commit()
            Log.pay(member.name, amount)
            return redirect('/')
        except:
            return 'There was an issue updating the debt.'
    else:
        return render_template('pay_member.html', member=member)

@app.route('/pay_batch/', methods=['GET', 'POST'])
@login_required
def pay_batch():
    members = Member.query.all()

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        try:
            for member in members:
                member.pay(amount)
            db.session.commit()
            Log.pay('Everyone', amount)
            return redirect('/')
        except:
            return 'There was an issue updating debts.'
    else:
        return render_template('pay_batch.html', members=members)

@app.route('/add_bill/', methods=['GET', 'POST'])
@login_required
def add_bill():
    if request.method == 'POST':
        form = request.form
        new_bill = Bill(description=form.get('description'), amount=form.get('amount'))

        try:
            db.session.add(new_bill)
            members = Member.query.all()
            debt_increment_apiece = float(new_bill.amount) / len(members)
            for member in members:
                member.charge_bill(debt_increment_apiece)
            db.session.commit() 
            Log.new_bill(new_bill)
            return redirect('/add_bill/')
        except:
            return 'There was an issue adding that bill.'
    else:
        bills = Bill.query.order_by(desc(Bill.date_created)).all()
        return render_template('add_bill.html', bills=bills)

@app.route('/delete_bill/<int:id>', methods=['GET'])
@login_required
def delete_bill(id):
    bill_to_delete = Bill.query.get_or_404(id)
    try:
        amount = bill_to_delete.amount
        members = Member.query.all()
        debt_decrease_apiece = -(float(amount) / len(members))
        for member in members:
            member.charge_bill(debt_decrease_apiece)
        db.session.delete(bill_to_delete)
        db.session.commit()
        Log.delete_bill(bill_to_delete)
        # flash('Member succesfully deleted')
        return redirect('/add_bill/')
    except:
        return 'There was an issue deleting that bill.'

@app.route('/update_bill/<int:id>', methods=['GET', 'POST'])
@login_required
def update_bill(id):
    bill_to_update = Bill.query.get_or_404(id)

    if request.method == 'POST':
        try:
            old_amount = bill_to_update.amount
            bill_to_update.description = request.form.get('description')
            bill_to_update.amount = float(request.form.get('amount'))
            delta = bill_to_update.amount - old_amount
            members = Member.query.all()
            debt_increase_apiece = float(delta) / len(members)
            for member in members:
                member.charge_bill(debt_increase_apiece)
            db.session.commit()
            Log.update_bill(bill_to_update)
            return redirect('/add_bill/')
        except:
            return 'There was an issue updating that bill.'
    else:
        return render_template('update_bill.html', bill=bill_to_update)

@app.route('/add_member/', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        form = request.form
        
        name = form.get('name')
        if name == '':
            return redirect('/add_member/')
        
        debt = form.get('debt')
        if debt == '':
            debt = 0.0
        
        new_member = Member(name=form.get('name'), mail=form.get('mail'), debt=debt)

        try:
            db.session.add(new_member)
            db.session.commit()
            Log.new_member(new_member)
            return redirect('/add_member/')
        except:
            return 'There was an issue adding that member.'
    else:
        members = Member.query.order_by(Member.date_created).all()
        return render_template('add_member.html', members=members)

@app.route('/delete_member/<int:id>', methods=['GET'])
@login_required
def delete_member(id):
    member_to_delete = Member.query.get_or_404(id)

    Log.delete_member(member_to_delete)


    try:
        db.session.delete(member_to_delete)
        db.session.commit()
        # flash('Member succesfully deleted')
        return redirect('/add_member/')
    except:
        return 'There was an issue deleting that member.'

@app.route('/update_member/<int:id>', methods=['GET', 'POST'])
@login_required
def update_member(id):
    member_to_update = Member.query.get_or_404(id)

    if request.method == 'POST':
        member_to_update.name = request.form.get('name')
        member_to_update.mail = request.form.get('mail')

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating that member.'
    else:
        return render_template('update_member.html', member=member_to_update)

@app.route('/events_log/', methods=['GET'])
@login_required
def events_log():
    logs = Log.query.order_by(desc(Log.date_created)).all()
    return render_template('events_log.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
