from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Idea, Template, BusinessCase
from flask_login import current_user
import openai
from forms import RegistrationForm, LoginForm, SubmitIdeaForm

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
    if request.method == 'POST':
        title = request.form['title']
        problem = request.form['problem']
        target_market = request.form.get('target_market', None)
        competition = request.form.get('competition', None)
        key_differentiators = request.form.get('key_differentiators', None)

        idea = Idea(
            user_id=current_user.id,
            title=title,
            problem=problem,
            target_market=target_market,
            competition=competition,
            key_differentiators=key_differentiators
        )
        db.session.add(idea)
        db.session.commit()

        flash('Idea submitted successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('submit_idea.html')


@app.route('/select_template', methods=['GET'])
@login_required
def select_template():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    templates = Template.query.paginate(page, per_page, error_out=False)

    return render_template('select_template.html', templates=templates)

@app.route('/generate_business_case/<int:template_id>/<int:idea_id>')
@login_required
def generate_business_case(template_id, idea_id):
    template = Template.query.get(template_id)
    idea = Idea.query.get(idea_id)

    # Combine the template and idea information into a prompt for the GPT API
    prompt = f"Generate a business case using the following template: {template.content}\n\nIdea Information:\nTitle: {idea.title}\nProblem: {idea.problem}\nTarget Market: {idea.target_market}\nCompetition: {idea.competition}\nKey Differentiators: {idea.key_differentiators}\n\nBusiness Case:"

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

    # Render the business case in the 'business_case.html' template
    return render_template('business_case.html', business_case=generated_business_case)