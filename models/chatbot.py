from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import random

db = SQLAlchemy()  #Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # customer, agent, admin

class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)

class ChatSessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    escalated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)

class MessageObserver:  
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

class Chatbot:
    _instance = None

    def __new__(cls):   #Singleton pattern
        if cls._instance is None:
            cls._instance = super(Chatbot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.observer = MessageObserver()

    def add_observer(self, observer):
        self.observer.add_observer(observer)

    def get_response_from_kb(self, message):
        
        kb_entries = KnowledgeBase.query.all()
        message_words = set(message.lower().split())
        best_match = None
        best_overlap = 0
        for entry in kb_entries:
            question_words = set(entry.question.lower().split())
            overlap = len(message_words.intersection(question_words))
            overlap_ratio = overlap / len(question_words) if question_words else 0
            # Require at least 2 overlapping words and ratio > 0.7 to avoid false matches
            if overlap >= 2 and overlap_ratio > 0.7 and overlap_ratio > best_overlap:
                best_match = entry.answer
                best_overlap = overlap_ratio
        return best_match

    def get_default_response(self, message):
        responses = {
            'hello': ['Hello! How can I help you today?', 'Hi there!', 'Greetings!'],
            'how are you': ['I\'m doing well, thank you!', 'I\'m fine, how about you?'],
            'bye': ['Goodbye!', 'See you later!', 'Take care!'],
            'default': ["I'm sorry, I couldn't find an answer to your question. Please escalate to an agent for further assistance."]
        }
        message_lower = message.lower()
        if 'hello' in message_lower or 'hi' in message_lower:
            return random.choice(responses['hello'])
        elif 'how are you' in message_lower:
            return random.choice(responses['how are you'])
        elif 'bye' in message_lower or 'goodbye' in message_lower:
            return random.choice(responses['bye'])
        else:
            return responses['default'][0]  # Return the escalate message directly

    def get_response(self, message, conversation_id=None):
        response = self.get_response_from_kb(message)
        if not response:
            response = self.get_default_response(message)

        # Notify observers
        self.observer.notify_observers({'type': 'bot_response', 'content': response, 'conversation_id': conversation_id})

        return response
