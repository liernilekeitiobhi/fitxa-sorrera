from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Education levels
EDUCATION_LEVELS = ['1ESO', '2ESO', '3ESO', '4ESO', '1BACHI', '2BACHI']

class Topic(db.Model):
    """Model for math topics (e.g., Algebra, Geometry)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    subtopics = db.relationship('Subtopic', backref='topic', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Topic {self.name}>'


class Subtopic(db.Model):
    """Model for math subtopics (e.g., Quadratic Equations, Pythagorean Theorem)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    
    # Relationships
    exercises = db.relationship('Exercise', backref='subtopic', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('name', 'topic_id', name='_subtopic_topic_uc'),)
    
    def __repr__(self):
        return f'<Subtopic {self.name}>'


class Exercise(db.Model):
    """Model for math exercises"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # Exercise content in TeX format
    solution = db.Column(db.Text, nullable=False)  # Solution in TeX format
    difficulty = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    education_level = db.Column(db.String(10), nullable=False)  # 1ESO, 2ESO, etc.
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'), nullable=False)
    file_source = db.Column(db.String(255), nullable=True)  # Original file name
    
    def __repr__(self):
        return f'<Exercise {self.id}, Difficulty: {self.difficulty}, Level: {self.education_level}>'


class User(UserMixin, db.Model):
    """Model for authorized users who can access editor mode"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Set user password (hashed)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        """Override UserMixin property to use our active field"""
        return self.active
    
    def __repr__(self):
        return f'<User {self.username}>'
