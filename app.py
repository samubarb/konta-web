from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import sys
import urllib.parse
from datetime import datetime

db_name = 'konta.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=True)
    debt = db.Column(db.Float, default=0.0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Member %r>' % self.id

    def pay(self, amount):
        self.debt -= float(amount)

    def charge_bill(self, amount):
        self.debt += float(amount)

    def get_debt(self):
        return str("%.3f" % round(self.debt, 3))

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Bill %r>' % self.id

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Log %r>' % self.id

    @staticmethod
    def pay(name, amount):
        desc = name + ' paid €' + str(amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('PayLogException')

    @staticmethod
    def new_bill(bill):
        desc = 'Added bill ' + bill.description + ' of €' + str(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewBillLogException')

    @staticmethod
    def delete_bill(bill):
        desc = 'Deleted bill ' + bill.description + ' of €' + str(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('DeleteBillLogException')

    @staticmethod
    def update_bill(bill):
        desc = 'Updated bill ' + bill.description + ' of €' + str(bill.amount)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('UpdateBillLogException')

    @staticmethod
    def new_member(member):
        desc = 'Added member ' + member.name + ' with debt of €' + str(member.debt)
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewMemberLogException')

    @staticmethod
    def delete_member(member):
        desc = 'Deleted member ' + member.name + ' with debt of €' + str(member.get_debt())
        new_log = Log(description=desc)
        try:
            db.session.add(new_log)
            db.session.commit()
        except:
            raise Exception('NewMemberLogException')


@app.route('/', methods=['GET'])
def index():
    members = Member.query.order_by(Member.date_created).all()
    return render_template('index.html', members=members)

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
def email():
    members = Member.query.order_by(Member.date_created).all()
    now = datetime.now()
    recipients = ''
    for m in members:
        recipients += m.mail + ' '
    month = int(now.strftime('%-m'))
    subject = 'Affitto + Bollette ' + italian_month(month) + now.strftime(' %Y')
    body = '\n\nBills payment updated at ' + now.strftime('%c') + '\n'
    for m in members:
        body += m.name + ' €' + str(round(m.debt)) + '\n'
    body += '\n\n'
    recipients = urllib.parse.quote(recipients)
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    return redirect('mailto:' + recipients +
                    '?subject=' + subject +
                    '&body=' + body)

@app.route('/pay_member/<int:id>', methods=['GET', 'POST'])
def pay_member(id):
    member = Member.query.get_or_404(id)

    if request.method == 'POST':
        amount = float(request.form['amount'])
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
def pay_batch():
    members = Member.query.all()

    if request.method == 'POST':
        amount = float(request.form['amount'])
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
def add_bill():
    if request.method == 'POST':
        form = request.form
        new_bill = Bill(description=form['description'], amount=form['amount'])

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
def update_bill(id):
    bill_to_update = Bill.query.get_or_404(id)

    if request.method == 'POST':
        try:
            old_amount = bill_to_update.amount
            bill_to_update.description = request.form['description']
            bill_to_update.amount = float(request.form['amount'])
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
def add_member():
    if request.method == 'POST':
        form = request.form
        
        name = form['name']
        if name == '':
            return redirect('/add_member/')
        
        debt = form['debt']
        if debt == '':
            debt = 0.0
        
        new_member = Member(name=form['name'], mail=form['mail'], debt=debt)

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
def update_member(id):
    member_to_update = Member.query.get_or_404(id)

    if request.method == 'POST':
        member_to_update.name = request.form['name']
        member_to_update.mail = request.form['mail']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating that member.'
    else:
        return render_template('update_member.html', member=member_to_update)

@app.route('/events_log/', methods=['GET'])
def events_log():
    logs = Log.query.order_by(desc(Log.date_created)).all()
    return render_template('events_log.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
