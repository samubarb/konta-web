from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import sys

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

@app.route('/', methods=['GET'])
def index():
    members = Member.query.order_by(Member.date_created).all()
    return render_template('index.html', members=members)

@app.route('/pay_member/<int:id>', methods=['GET', 'POST'])
def pay_member(id):
    member = Member.query.get_or_404(id)

    if request.method == 'POST':
        amount = float(request.form['amount'])
        try:
            member.pay(amount)
            db.session.commit()
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
            return redirect('/add_bill/')
        except:
            return 'There was an issue adding that bill.'
    else:
        bills = Bill.query.order_by(desc(Bill.date_created)).all()
        return render_template('add_bill.html', bills=bills)

@app.route('/delete_bill/<int:id>', methods=['GET', 'POST'])
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
            return redirect('/add_member/')
        except:
            return 'There was an issue adding that member.'
    else:
        members = Member.query.order_by(Member.date_created).all()
        return render_template('add_member.html', members=members)

@app.route('/delete_member/<int:id>')
def delete_member(id):
    member_to_delete = Member.query.get_or_404(id)

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


if __name__ == '__main__':
    app.run(debug=True)
