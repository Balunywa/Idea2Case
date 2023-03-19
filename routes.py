from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
import os
from models import User, Idea, Template, BusinessCase
from flask_login import current_user
import openai
from forms import RegistrationForm, LoginForm, SubmitIdeaForm, IdeaForm, AddTemplateForm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from flask import send_file
import tempfile
from io import BytesIO
from flask import render_template, Response
from docx import Document
import requests





# Replace 'your_app' with the name of your Flask application
openai.api_key = "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"
# Routes and views

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('You are now signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Use Flask-Login's login_user function
            flash('You are now logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    ideas = Idea.query.filter_by(user_id=user_id).all()
    business_cases = BusinessCase.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', ideas=ideas, business_cases=business_cases)

@app.route('/submit_idea', methods=['GET', 'POST'])
@login_required
def submit_idea():
    form = IdeaForm()

    if form.validate_on_submit():
        idea = Idea(
            user_id=current_user.id,
            title=form.title.data,
            problem=form.problem.data,
            target_market=form.target_market.data,
            competition=form.competition.data,
            key_differentiators=form.key_differentiators.data
        )
        db.session.add(idea)
        db.session.commit()

        flash('Idea submitted successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('submit_idea.html', form=form)


@app.route('/add_template', methods=['GET', 'POST'])
@login_required
def add_template():
    form = AddTemplateForm()

    if form.validate_on_submit():
        new_template = Template(name=form.name.data, content=form.content.data)
        db.session.add(new_template)
        db.session.commit()

        flash('Template has been added successfully', 'success')
        return redirect(url_for('select_template'))

    return render_template('add_template.html', form=form)


@app.route('/select_template/<int:idea_id>', methods=['GET'])
@login_required
def select_template(idea_id):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    templates = Template.query.order_by(Template.id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('select_template.html', templates=templates, idea_id=idea_id)



def generate_business_case(idea_id):
    idea = Idea.query.get(idea_id)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Generate a business case for adopting the proposed solution '{idea.title}', which addresses the problem '{idea.problem}' and targets the market '{idea.target_market}'. Consider the competition '{idea.competition}' and the key differentiators '{idea.key_differentiators}'. The business case should follow the structure provided and include actual data and metrics to support the case."}
    ]

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 500,
        "n": 1,
        "stop": None,
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    generated_business_case = response_json['choices'][0]['message']['content'].strip()

    return generated_business_case



@app.route('/generate_business_case/<int:idea_id>', methods=['GET'])
@login_required
def download_business_case(idea_id):
    # Generate the business case document
    business_case = generate_business_case(idea_id)

    # Create an in-memory file-like object to write the generated document to
    in_memory_file = BytesIO()

    # Convert the generated document to a Word document using python-docx
    document = Document()
    document.add_paragraph(business_case)
    document.save(in_memory_file)

    # Return the file as an attachment with the specified filename
    response = Response(in_memory_file.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response.headers['Content-Disposition'] = 'attachment; filename=business_case.docx'

    # Close the in-memory file
    in_memory_file.close()

    return response