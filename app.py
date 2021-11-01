from flask import Flask, render_template, flash, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators
from wtforms.validators import DataRequired, ValidationError
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

#MODELS
#from flaskblog import db, login_manager
from flask_login import UserMixin
from flask_login import login_user, current_user, logout_user, login_required

#INIT
from flask_login import LoginManager


app = Flask(__name__)

#Add our database
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myusers.db"

#New database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://tansubaktiran:Avz9p9&9Dgsu_099@193.111.73.99/tansubaktiran"

""" user = "sql11445951",
    password = "xdvDL1Mz2q",
    host = "sql11.freemysqlhosting.net",
    database = "sql11445951"
"""
#Secret key
app.config['SECRET_KEY'] = "MYSUPERKEY"
#Initialize the adatabase
db = SQLAlchemy(app)

#ADDED TO CONFIG SECTION FOR TESTING USER LOGIN - 27.10.21
login_manager = LoginManager(app)
login_manager.login_view = 'form1' #Name of the route in charge of logging in
login_manager.login_message_category = 'info'




#ADDED FOR TESTING USER LOGIN - 27.10.21
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


#Create a model for database. What are we going to write to our database etc.?
#The model is like defining the columns/categorical names to be written to the database. 
#Data types, lengths etc. are defined here.

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Create a string - BUNA BİR BAKALIM NEYMİŞ.. As I understand, this is more for debugging and checking errors.. 
    # not used when app is working without problems
    def __repr__(self):
        return '<Name %r>' % self.name


class Customers(db.Model): #Customers db - NEW!!! - This is where we define our database variables and their types.
    id = db.Column(db.Integer, primary_key=True)
    comp_name_db = db.Column(db.String(100), nullable=False)
    staff_name_db = db.Column(db.String(100), nullable=False)
    telephone_db = db.Column(db.String(100), nullable=False)
    cust_email_db = db.Column(db.String(100), nullable=False, unique=True)
    cust_webpage_db = db.Column(db.String(100), nullable=False)
    notes_db = db.Column(db.String(100), nullable=False)
    company_country_db = db.Column(db.String(100), nullable=False)
    company_address_db = db.Column(db.String(100), nullable=False)
    date_added_db = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Create a string - BUNA BİR BAKALIM NEYMİŞ.. As I understand, this is more for debugging and checking errors.. 
    # not used when app is working without problems
    def __repr__(self):
        return '<Comp Name %r>' % self.comp_name_db


#Create a form class in here
class form_one(FlaskForm):
    name_field = StringField("Enter your password please..", validators=[DataRequired()])
    submit_field = SubmitField("For Entering System")

    #To be checked and fixed!!! ////////////////CONSTRUCTION FIELD
    def validate_username(self, name_field):
        user = Users.query.filter_by(name=name_field.data).first()
        if not user:
            raise ValidationError('This is not a valid password. Please use a correct one.')

#Create a form class in here - this will be initially used in testing SQAlchemy Database
class form_two(FlaskForm):
    name_field = StringField("Whats your name today?", validators=[DataRequired()])
    email_field = StringField("Whats your email today?", validators=[DataRequired()])
    submit_field = SubmitField("For Submitting")


#Create a form class in here
class customer_form(FlaskForm):
    company_name = StringField("Müşteri firma adı", validators=[DataRequired()])
    staff_name = StringField("Müşteri adı", validators=[DataRequired()])
    telephone = StringField("Müşteri telefonu", validators=[DataRequired()])
    email = StringField("İrtibat e-maili", validators=[DataRequired()])
    webpage = StringField("Müşteri web sayfası")
    notes = StringField("Müşterimiz hakkındaki notlar")
    company_country = StringField("Müşteri ülkesi ", validators=[DataRequired()])
    company_address = StringField("Müşteri adresi")
    submit_field = SubmitField("Kaydet")

@app.route('/')
@app.route('/index')
def index():
    name="Tansu"
    number = 10
    return  render_template("index.html", test_name=name, test_number=number)


@app.route('/user') 
def user():
    name2a="Mike"
    country_group = ["Germany", "Austria", "Italy", "Greece",]
    return  render_template("user.html", name2=name2a, country_group=country_group)

"""@app.route('/form1', methods=["GET", "POST"])
def form1():
    name = None
    form = form_one()
    #Validation of our form
    if form.validate_on_submit():
        name = form.name_field.data
        form.name_field.data = ""
        flash("Yes, this is a valid entry. Thank you!")
    #else: #If an entry is a mistake, a warning message should be worked on.
    #    flash("Please, check your entry once more... not a valid entry this time.")
    return  render_template("form1.html", name = name, form=form)"""

@app.route('/form2', methods=["GET", "POST"])
@login_required
def form2(): #Add user - ALSO TO DATABASE!!!
    name = None #For sending to "please enter your name/credentials page on html - if statement"
    form = form_two()
    #Validation of our form
    if form.validate_on_submit():
        #name = form.name_field.data
        user = Users.query.filter_by(email=form.email_field.data).first()
        if user is None:
            user = Users(name = form.name_field.data, email = form.email_field.data)
            db.session.add(user)
            db.session.commit()
        name = form.name_field.data #For sending to "hello -name-"" page on html. Otherwise will keep asking the name/credentials.
        #form.name_field.data = ""
        #form.email_field.data = ""

        flash("Entry recorded positively! Thank you!")
        
    our_users = Users.query.order_by(Users.date_added)
    return  render_template("form2.html", form=form, name=name, our_users=our_users)

#Route for updating our entries
@app.route('/update/<int:id>', methods=["GET", "POST"])
@login_required
def update(id):
    #id = None
    form = form_two()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        print("Yes this is a POST attempt")
        name_to_update.name = request.form["name_field"] #Check here out!!
        name_to_update.email = request.form["email_field"]
        try:
            db.session.commit()
            flash("Your update process is successful")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
            
        except:
            db.session.commit()
            flash("Update process failed! Try again later..")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

 
#Route for deleting our entries - NEW!! :)
@app.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None #For sending to "please enter your name/credentials page on html - if statement"
    form = form_two()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Entrey deleted. Thank you")
        our_users = Users.query.order_by(Users.date_added)
        print("Entry deleted.. now should be re-routing to form2??")
        return redirect(url_for("form2")) #Orjinal codemy videsounda bu satır yok. 
        # Bunun yerine aşağıdaki satır yazılmış ama delete/n urlinde kalıyordu. 
        # Dolayısı ile sildikten sonra yeni giriş hata veriyordu.
        #return  render_template("form2.html", form=form, name=name, our_users=our_users)
    except:
        flash("There seems to be a problem. Thank you")
        return  render_template("form2.html", form=form, name=name, our_users=our_users)

@app.route('/customer_form1', methods=["GET", "POST"])
@login_required
def customer_form1():
    #company_n =  staff_n = tel =  emai = webp = note = company_c = company_a = None
    form = customer_form()
    #Validation of our form
    if form.validate_on_submit():
        company = Customers.query.filter_by(cust_email_db=form.email.data).first()
        #print(company)
        if company is None:
            company = Customers(comp_name_db = form.company_name.data, staff_name_db = form.staff_name.data, telephone_db = form.telephone.data,
                cust_email_db = form.email.data, cust_webpage_db = form.webpage.data, notes_db = form.notes.data, company_country_db = form.company_country.data, company_address_db = form.company_address.data)
            
            db.session.add(company)
            db.session.commit()
        #company_n = form.company_name.data
        #staff_n = form.staff_name.data
        #tel = form.telephone.data
        #emai = form.email.data
        #webp = form.webpage.data
        #note = form.notes.data
        #company_c = form.company_country.data
        #company_a = form.company_address.data
        form.company_name.data = "" #Formdaki (html) ilk satırı kayıt sonrası siliyor. Diğerlerini de silmek için ayrıca eklemek gerek.
        flash("Yes, this is a valid entry. Thank you!")
    #else: #If an entry is a mistake, a warning message should be worked on.
    #    flash("Please, check your entry once more... not a valid entry this time.")
    our_customers = Customers.query.order_by(Customers.date_added_db)
    #print(our_customers)
    #company_n=company_n, staff_n=staff_n, tel=tel, 
    #emai=emai, webp=webp, note=note, company_c=company_c, company_a=company_a,
    return render_template("customer_form1.html",  form=form, our_customers=our_customers)


#/////////////////// CONSTRUCTION FIELD
#Fonksiyon / route Form 1 login yerine kullanılıyor. Aslında login fonksiyonu.
@app.route("/form1", methods=['GET', 'POST'])
def form1():
    name=None
    if current_user.is_authenticated:
        print("User is ALREADY LOGGED IN")
        return redirect(url_for('index'))
    form = form_one()
    if form.validate_on_submit():
        print("Form validated")
        user = Users.query.filter_by(email=form.name_field.data).first()
        name=form.name_field.data
        print(form.name_field.data)
        if user:
            print("/////////Found this user!!!//////")
            login_user(user)
            name=form.name_field.data
            print("User seems to be logged in beybisi..")
            flash('Login Successful. Have a nice day!!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('form1.html', title='Login', form=form, name=name)


@app.route("/logout")
def logout():
    logout_user()
    print("The user should have been LOGGED OUT NOW!!!")
    return redirect(url_for('index'))



#/////////////////// CONSTRUCTION FIELD


if __name__ == "__main__":
    app.run(debug=True)
