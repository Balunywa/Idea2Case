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

""""
def generate_business_case(idea_id):
    # Get the idea object from the database
    idea = Idea.query.get(idea_id)

    # Describe the desired structure in the prompt for the GPT API
    #-1-1-prompt = f"Generate a business case for adopting the proposed solution '{idea.title}', which addresses the problem '{idea.problem}' and targets the market '{idea.target_market}'. Consider the competition '{idea.competition}' and the key differentiators '{idea.key_differentiators}'. The business case should follow the structure provided and include actual data and metrics to support the case:\n\nExecutive Summary:\nProblem Statement:\nObjectives:\n1. Objective 1\n2. Objective 2\n3. Objective 3\n4. Objective 4\n5. Objective 5\n\nProposed Solution:\n1. Benefit 1\n2. Benefit 2\n3. Benefit 3\n4. Benefit 4\n5. Benefit 5\n6. Benefit 6\n\nCost Analysis:\n1. Initial setup and configuration costs\n2. Ongoing infrastructure and service costs\n3. Potential cost savings through optimization and efficiency gains\n4. Costs associated with training and knowledge transfer\n\nROI and Benefits Realization:\n1. KPI 1\n2. KPI 2\n3. KPI 3\n4. KPI 4\n\nNext Steps:\n1. Conduct a detailed cost-benefit analysis\n2. Develop a phased implementation plan\n3. Identify and prioritize applications and services to migrate\n4. Provide training and knowledge transfer\n5. Establish a governance model and assign roles and responsibilities\n\nConclusion:"
    prompt = f"Generate a business case for adopting the proposed solution '{idea.title}', which addresses the problem '{idea.problem}' and targets the market '{idea.target_market}'. Consider the competition '{idea.competition}' and the key differentiators '{idea.key_differentiators}'. The business case should follow the structure provided and include actual data and metrics to support the case:\n\nExecutive Summary:\nProblem Statement:\nObjectives:\n1. Objective 1\n2. Objective 2\n3. Objective 3\n4. Objective 4\n5. Objective 5\n\nProposed Solution:\n1. Benefit 1\n2. Benefit 2\n3. Benefit 3\n4. Benefit 4\n5. Benefit 5\n6. Benefit 6\n\nCost Analysis:\n1. Initial setup and configuration costs\n2. Ongoing infrastructure and service costs\n3. Potential cost savings through optimization and efficiency gains\n4. Costs associated with training and knowledge transfer\n\nROI and Benefits Realization:\n1. KPI 1\n2. KPI 2\n3. KPI 3\n4. KPI 4\n\nNext Steps:\n1. Conduct a detailed cost-benefit analysis\n2. Develop a phased implementation plan\n3. Identify and prioritize applications and services to migrate\n4. Provide training and knowledge transfer\n5. Establish a governance model and assign roles and responsibilities\n\nConclusion:"
    # Make the GPT API request
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract the generated business case from the API response
    generated_business_case = response.choices[0].text.strip()

    # Return the generated business case
    return generated_business_case
"""

def generate_business_case(idea_id):
    # Get the idea object from the database
    idea = Idea.query.get(idea_id)

    prompt = f"Generate a business case for adopting the proposed solution '{idea.title}', which addresses the problem '{idea.problem}' and targets the market '{idea.target_market}'. Please include the following sections:\n\n1. Problem statement and proposed solution\n2. Market analysis and target audience\n3. Financial projections, including cost and revenue estimates\n4. Project timeline and milestones\n\n"

    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    generated_business_case = response.choices[0].text.strip()
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





"""
@app.route('/generate_business_case/<int:idea_id>', methods=['GET'])
@login_required
def download_business_case(idea_id):
    # Generate the business case document
    business_case = generate_business_case(idea_id)

    # Create an in-memory file-like object to write the generated document to
    in_memory_file = BytesIO()

    # Convert the generated document to a Word document using python-docx
    document = python-docx.Document()
    document.add_paragraph(business_case)
    document.save(in_memory_file)

    # Return the file as an attachment with the specified filename
    response = Response(in_memory_file.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response.headers['Content-Disposition'] = 'attachment; filename=business_case.docx'

    # Close the in-memory file
    in_memory_file.close()

    return response

"""

"""
def generate_business_case(idea_id):
    # Get the idea object from the database
    idea = Idea.query.get(idea_id)

    # Describe the desired structure in the prompt for the GPT API
    prompt = f"Generate a business case for adopting the proposed solution '{idea.title}', which addresses the problem '{idea.problem}' and targets the market '{idea.target_market}'. Consider the competition '{idea.competition}' and the key differentiators '{idea.key_differentiators}'. The business case should follow the structure provided and include actual data and metrics to support the case:\n\nExecutive Summary:\nProblem Statement:\nObjectives:\n1. Objective 1\n2. Objective 2\n3. Objective 3\n4. Objective 4\n5. Objective 5\n\nProposed Solution:\n1. Benefit 1\n2. Benefit 2\n3. Benefit 3\n4. Benefit 4\n5. Benefit 5\n6. Benefit 6\n\nCost Analysis:\n1. Initial setup and configuration costs\n2. Ongoing infrastructure and service costs\n3. Potential cost savings through optimization and efficiency gains\n4. Costs associated with training and knowledge transfer\n\nROI and Benefits Realization:\n1. KPI 1\n2. KPI 2\n3. KPI 3\n4. KPI 4\n\nNext Steps:\n1. Conduct a detailed cost-benefit analysis\n2. Develop a phased implementation plan\n3. Identify and prioritize applications and services to migrate\n4. Provide training and knowledge transfer\n5. Establish a governance model and assign roles and responsibilities\n\nConclusion:"

    # Make the GPT API request
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract the generated business case from the API response
    generated_business_case = response.choices[0].text.strip()

    # Return the generated business case
    return generated_business_case


@app.route('/generate_business_case/<int:idea_id>', methods=['GET'])
@login_required
def download_business_case(idea_id):
    # Generate the business case document
    business_case = generate_business_case(idea_id)

    # Create an in-memory file-like object to write the generated document to
    in_memory_file = BytesIO()
    in_memory_file.write(business_case.encode('utf-8'))
    in_memory_file.seek(0)

    # Return the file as an attachment with the specified filename
    response = Response(in_memory_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response.headers['Content-Disposition'] = 'attachment; filename=business_case.docx'

    # Close the in-memory file
    in_memory_file.close()

    return response
"""