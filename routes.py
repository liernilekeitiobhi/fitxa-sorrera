import os
import random
from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
from app import app, db
from models import Exercise, Topic, Subtopic, User, EDUCATION_LEVELS
from tex_parser import parse_tex_file
from pdf_generator import PdfGenerator
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
import logging

# Configure logging
logger = logging.getLogger(__name__)

# PDF Generator instance
pdf_generator = PdfGenerator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'tex'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    """
    Student mode route:
    - GET: Show the exercise selection form
    - POST: Generate and download exercise sheet
    """
    # Get all topics and subtopics for the form
    topics = Topic.query.all()
    
    if request.method == 'POST':
        try:
            # Get form data
            selected_exercises = []
            selections = request.form.getlist('selection')
            
            for selection in selections:
                parts = selection.split('-')
                if len(parts) >= 3:
                    subtopic_id = int(parts[0])
                    education_level = parts[1]
                    difficulty = int(parts[2])
                    count = int(request.form.get(f'count-{selection}', 1))
                    
                    # Get random exercises based on criteria
                    exercises = Exercise.query.filter_by(
                        subtopic_id=subtopic_id,
                        education_level=education_level,
                        difficulty=difficulty
                    ).all()
                    
                    # Randomly select requested number of exercises
                    selected = random.sample(exercises, min(count, len(exercises)))
                    selected_exercises.extend(selected)
            
            if not selected_exercises:
                flash('No exercises found with the specified criteria.', 'warning')
                return redirect(url_for('student'))
            
            # Generate PDF
            pdf_file = pdf_generator.generate_exercise_pdf(
                selected_exercises, 
                include_solutions=False,
                title="Mathematics Exercises"
            )
            
            if pdf_file:
                return pdf_generator.send_pdf_file(pdf_file, 'math_exercises.pdf')
            else:
                flash('Error generating PDF file.', 'danger')
                
        except Exception as e:
            logger.error(f"Error in student mode: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Get education levels for form
    education_levels = EDUCATION_LEVELS
    
    return render_template('student.html', topics=topics, education_levels=education_levels)

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    """
    Teacher mode route:
    - GET: Show the exercise selection form
    - POST: Generate and download exercise sheets with and without solutions
    """
    # Get all topics and subtopics for the form
    topics = Topic.query.all()
    
    if request.method == 'POST':
        try:
            # Get form data
            selected_exercises = []
            selections = request.form.getlist('selection')
            
            for selection in selections:
                parts = selection.split('-')
                if len(parts) >= 3:
                    subtopic_id = int(parts[0])
                    education_level = parts[1]
                    difficulty = int(parts[2])
                    count = int(request.form.get(f'count-{selection}', 1))
                    
                    # Get random exercises based on criteria
                    exercises = Exercise.query.filter_by(
                        subtopic_id=subtopic_id,
                        education_level=education_level,
                        difficulty=difficulty
                    ).all()
                    
                    # Randomly select requested number of exercises
                    selected = random.sample(exercises, min(count, len(exercises)))
                    selected_exercises.extend(selected)
            
            if not selected_exercises:
                flash('No exercises found with the specified criteria.', 'warning')
                return redirect(url_for('teacher'))
                
            # Generate PDF without solutions
            pdf_file_no_solutions = pdf_generator.generate_exercise_pdf(
                selected_exercises, 
                include_solutions=False,
                title="Mathematics Exercises"
            )
            
            # Generate PDF with solutions
            pdf_file_with_solutions = pdf_generator.generate_exercise_pdf(
                selected_exercises, 
                include_solutions=True,
                title="Mathematics Exercises with Solutions"
            )
            
            # Store filenames in session for download links
            session['pdf_no_solutions'] = pdf_file_no_solutions
            session['pdf_with_solutions'] = pdf_file_with_solutions
            
            flash('Exercise sheets generated successfully. You can download them below.', 'success')
            
            return render_template(
                'teacher.html', 
                topics=topics, 
                education_levels=EDUCATION_LEVELS,
                pdf_generated=True
            )
                
        except Exception as e:
            logger.error(f"Error in teacher mode: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('teacher.html', topics=topics, education_levels=EDUCATION_LEVELS)

@app.route('/download-exercises')
def download_exercises():
    """Download exercises without solutions"""
    pdf_file = session.get('pdf_no_solutions')
    if pdf_file and os.path.exists(pdf_file):
        return pdf_generator.send_pdf_file(pdf_file, 'math_exercises.pdf')
    flash('PDF file not available.', 'danger')
    return redirect(url_for('teacher'))

@app.route('/download-solutions')
def download_solutions():
    """Download exercises with solutions"""
    pdf_file = session.get('pdf_with_solutions')
    if pdf_file and os.path.exists(pdf_file):
        return pdf_generator.send_pdf_file(pdf_file, 'math_exercises_with_solutions.pdf')
    flash('PDF file not available.', 'danger')
    return redirect(url_for('teacher'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route for editor mode access"""
    if current_user.is_authenticated:
        return redirect(url_for('editor'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'¡Bienvenido, {username}!', 'success')
            
            # Redirect to the page the user was trying to access
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('editor'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))


@app.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add a new editor user (restricted to authenticated users)"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        admin_password = request.form.get('admin_password')
        
        # Verify current user's password
        if not current_user.check_password(admin_password):
            flash('Tu contraseña es incorrecta.', 'danger')
            return redirect(url_for('add_user'))
        
        # Verify passwords match
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('add_user'))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Este nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('add_user'))
        
        # Create new user
        new_user = User()
        new_user.username = username
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Usuario {username} creado correctamente.', 'success')
        return redirect(url_for('editor'))
    
    return render_template('add_user.html')


@app.route('/editor', methods=['GET', 'POST'])
@login_required
def editor():
    """
    Editor mode route (restricted to authenticated users):
    - GET: Show the .tex file upload form
    - POST: Process uploaded .tex file
    """
    # Get all topics and subtopics for the form
    topics = Topic.query.all()
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'tex_file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.url)
        
        file = request.files['tex_file']
        
        # Check if the file has a name
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        # Check if the file is a .tex file
        if file and allowed_file(file.filename):
            try:
                # Get form data
                education_level = request.form.get('education_level')
                topic_name = request.form.get('topic_name')
                subtopic_name = request.form.get('subtopic_name')
                
                # Secure the filename
                filename = secure_filename(file.filename or "")
                
                # Read file content
                file_content = file.read().decode('utf-8')
                
                # Parse the file
                success, message, count = parse_tex_file(
                    file_content, 
                    filename, 
                    education_level, 
                    topic_name, 
                    subtopic_name
                )
                
                if success:
                    flash(f'{message}', 'success')
                else:
                    flash(f'Error: {message}', 'danger')
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                flash(f'An error occurred: {str(e)}', 'danger')
        else:
            flash('Invalid file type. Only .tex files are allowed.', 'danger')
    
    # Get education levels for form
    education_levels = EDUCATION_LEVELS
    
    return render_template('editor.html', topics=topics, education_levels=education_levels)

@app.route('/api/subtopics/<int:topic_id>')
def get_subtopics(topic_id):
    """API endpoint to get subtopics for a specific topic"""
    subtopics = Subtopic.query.filter_by(topic_id=topic_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in subtopics])

@app.route('/api/available-exercises')
def available_exercises():
    """API endpoint to get available exercises based on criteria"""
    subtopic_id = request.args.get('subtopic_id', type=int)
    education_level = request.args.get('education_level')
    difficulty = request.args.get('difficulty', type=int)
    
    if not all([subtopic_id, education_level, difficulty]):
        return jsonify({'count': 0})
    
    count = Exercise.query.filter_by(
        subtopic_id=subtopic_id,
        education_level=education_level,
        difficulty=difficulty
    ).count()
    
    return jsonify({'count': count})
