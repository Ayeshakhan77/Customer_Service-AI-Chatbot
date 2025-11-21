from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models.chatbot import Chatbot, db, MessageObserver, User, ChatSessions, Message, KnowledgeBase, Feedback

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()
    
    if KnowledgeBase.query.count() == 0:
        kb_entries = [
            KnowledgeBase(question="What are your business hours?", answer="Our business hours are Monday to Friday, 9 AM to 5 PM."),
            KnowledgeBase(question="What time do you open?", answer="We open at 9 AM on weekdays."),
            KnowledgeBase(question="When are you open?", answer="Our business hours are Monday to Friday, 9 AM to 5 PM."),
            KnowledgeBase(question="How can I contact support?", answer="You can contact support via email at support@example.com or by phone at 1-800-123-4567."),
            KnowledgeBase(question="How do I reach customer service?", answer="Contact us at support@example.com or call 1-800-123-4567."),
            KnowledgeBase(question="What products do you offer?", answer="We offer a range of products including software solutions, consulting services, and hardware devices. Visit our website for more details."),
            KnowledgeBase(question="What services do you provide?", answer="Our services include software development, consulting, and hardware sales."),
            KnowledgeBase(question="Do you sell software?", answer="Yes, we offer various software solutions. Check our website for details."),
            KnowledgeBase(question="How do I reset my password?", answer="To reset your password, click on 'Forgot Password' on the login page and follow the instructions sent to your email."),
            KnowledgeBase(question="I forgot my password", answer="Use the 'Forgot Password' link on the login page to reset it."),
            KnowledgeBase(question="What is your return policy?", answer="Our return policy allows returns within 30 days of purchase for a full refund, provided the item is in original condition."),
            KnowledgeBase(question="Can I return items?", answer="Yes, returns are accepted within 30 days for a full refund if in original condition."),
            KnowledgeBase(question="Do you offer international shipping?", answer="Yes, we offer international shipping to select countries. Shipping costs and times vary by location."),
            KnowledgeBase(question="Do you ship overseas?", answer="We ship to select international locations. Contact us for details."),
            KnowledgeBase(question="How can I track my order?", answer="You can track your order using the tracking number provided in your confirmation email on our website."),
            KnowledgeBase(question="Where is my order?", answer="Use the tracking number from your email to check order status on our site."),
            KnowledgeBase(question="What payment methods do you accept?", answer="We accept credit cards, PayPal, and bank transfers."),
            KnowledgeBase(question="How can I pay?", answer="We accept credit cards, PayPal, and bank transfers."),
            KnowledgeBase(question="Are there any discounts available?", answer="We offer seasonal discounts and promotions. Check our website or subscribe to our newsletter for updates."),
            KnowledgeBase(question="Do you have promotions?", answer="Yes, we have seasonal promotions. Subscribe to our newsletter for updates."),
            KnowledgeBase(question="How do I cancel my subscription?", answer="To cancel your subscription, log in to your account and go to the subscription settings, or contact support."),
            KnowledgeBase(question="I want to unsubscribe", answer="Log in to your account to manage subscriptions or contact support."),
            KnowledgeBase(question="What is your warranty policy?", answer="We offer a 1-year warranty on all hardware products. Contact support for details."),
            KnowledgeBase(question="Do you provide warranties?", answer="Yes, 1-year warranty on hardware. Software support is available via our help desk."),
            KnowledgeBase(question="How do I update my account information?", answer="Log in to your account and go to settings to update your information."),
            KnowledgeBase(question="Can I change my email?", answer="Yes, update it in your account settings after logging in."),
            KnowledgeBase(question="What are your pricing plans?", answer="Our pricing varies by product. Visit our website or contact sales for quotes."),
            KnowledgeBase(question="How much do your services cost?", answer="Pricing depends on the service. Please contact sales for a customized quote."),
            KnowledgeBase(question="Do you offer training?", answer="Yes, we provide training sessions for our software products. Schedule via our website."),
            KnowledgeBase(question="How do I get support for your software?", answer="Use our help desk at support@example.com or call 1-800-123-4567."),
           # KnowledgeBase(question="What is your privacy policy?", answer="Our privacy policy is available on our website. We protect your data in compliance with regulations."),
           # KnowledgeBase(question="How do you handle my data?", answer="We follow strict privacy guidelines. See our privacy policy on the website.")
        ]
        db.session.add_all(kb_entries)
        db.session.commit()

chatbot = Chatbot()
observer = MessageObserver()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('agent', 'Agent'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')

class KBForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    submit = SubmitField('Add')

class FeedbackForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Feedback')

@app.route('/')
@login_required
def index():
    if current_user.role == 'customer':
        return render_template('customer.html')
    elif current_user.role == 'agent':
        return render_template('agent.html')
    elif current_user.role == 'admin':
        return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                flash('Username already exists')
            else:
                flash('An error occurred during registration')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    if current_user.role != 'customer':
        return jsonify({'error': 'Unauthorized'}), 403
    user_message = request.json.get('message')
    conversation_id = request.json.get('conversation_id')
    if not conversation_id:
        new_session = ChatSessions(customer_id=current_user.id)
        db.session.add(new_session)
        db.session.commit()
        conversation_id = new_session.id
    # Save user message
    new_message = Message(conversation_id=conversation_id, sender_id=current_user.id, content=user_message)
    db.session.add(new_message)
    db.session.commit()
    bot_response = chatbot.get_response(user_message, conversation_id)
    # Save bot message
    new_bot_message = Message(conversation_id=conversation_id, sender_id=0, content=bot_response)
    db.session.add(new_bot_message)
    db.session.commit()
    return jsonify({'response': bot_response, 'conversation_id': conversation_id})

@app.route('/escalate', methods=['POST'])
@login_required
def escalate():
    if current_user.role != 'customer':
        return jsonify({'error': 'Unauthorized'}), 403
    conversation_id = request.json.get('conversation_id')
    if not conversation_id:
        new_session = ChatSessions(customer_id=current_user.id)
        db.session.add(new_session)
        db.session.commit()
        conversation_id = new_session.id
    conv = ChatSessions.query.get(conversation_id)
    if conv:
        conv.escalated = True
        db.session.commit()
        # Return feedback URL
        feedback_url = url_for('feedback', conv_id=conversation_id, _external=True)
        return jsonify({'status': 'escalated', 'feedback_url': feedback_url})
    return jsonify({'error': 'Failed to escalate'}), 400

@app.route('/agent/messages')
@login_required
def agent_messages():
    if current_user.role != 'agent':
        return jsonify({'error': 'Unauthorized'}), 403
    # Available escalated chats
    available_conversations = ChatSessions.query.filter_by(escalated=True, agent_id=None).all()
    available_data = []
    for conv in available_conversations:
        messages = Message.query.filter_by(conversation_id=conv.id).all()
        available_data.append({'id': conv.id, 'messages': [{'content': m.content, 'timestamp': m.timestamp.isoformat()} for m in messages]})
    # Active chats assigned to this agent
    active_conversations = ChatSessions.query.filter_by(escalated=True, agent_id=current_user.id).all()
    active_data = []
    for conv in active_conversations:
        messages = Message.query.filter_by(conversation_id=conv.id).all()
        active_data.append({'id': conv.id, 'messages': [{'content': m.content, 'timestamp': m.timestamp.isoformat()} for m in messages]})
    return jsonify({'available': available_data, 'active': active_data})

@app.route('/agent/take_chat/<int:conv_id>', methods=['POST'])
@login_required
def take_chat(conv_id):
    if current_user.role != 'agent':
        return jsonify({'error': 'Unauthorized'}), 403
    conv = ChatSessions.query.get(conv_id)
    if conv and conv.escalated and conv.agent_id is None:
        conv.agent_id = current_user.id
        db.session.commit()
        return jsonify({'status': 'taken'})
    return jsonify({'error': 'Chat not available'}), 400

@app.route('/agent/reply', methods=['POST'])
@login_required
def agent_reply():
    if current_user.role != 'agent':
        return jsonify({'error': 'Unauthorized'}), 403
    conv_id = request.json.get('conversation_id')
    reply = request.json.get('reply')
    conv = ChatSessions.query.get(conv_id)
    if conv and conv.agent_id == current_user.id:
        new_message = Message(conversation_id=conv_id, sender_id=current_user.id, content=reply)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'status': 'replied'})
    return jsonify({'error': 'Unauthorized or invalid conversation'}), 403

@app.route('/admin/kb', methods=['GET', 'POST'])
@login_required
def admin_kb():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    form = KBForm()
    if form.validate_on_submit():
        new_kb = KnowledgeBase(question=form.question.data, answer=form.answer.data)
        db.session.add(new_kb)
        db.session.commit()
        flash('KB entry added')
    kb_entries = KnowledgeBase.query.all()
    return render_template('admin_kb.html', form=form, kb=kb_entries)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/feedback/<int:conv_id>', methods=['GET', 'POST'])
@login_required
def feedback(conv_id):
    form = FeedbackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(conversation_id=conv_id, rating=form.rating.data, comment=form.comment.data)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback submitted')
        return redirect(url_for('index'))
    return render_template('feedback.html', form=form)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
