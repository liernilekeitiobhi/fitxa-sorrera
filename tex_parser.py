import re
import logging
from models import Exercise, Topic, Subtopic, EDUCATION_LEVELS
from app import db

# Configure logging
logger = logging.getLogger(__name__)

def parse_tex_file(file_content, filename, education_level, topic_name, subtopic_name):
    """
    Parse a .tex file to extract exercises, solutions, and metadata.
    
    Format expected in the .tex file:
    % BEGIN_EXERCISE
    % DIFFICULTY: 1-3
    Exercise content here...
    % BEGIN_SOLUTION
    Solution content here...
    % END_SOLUTION
    % END_EXERCISE
    
    Args:
        file_content (str): Content of the .tex file
        filename (str): Name of the uploaded file
        education_level (str): Education level for the exercises
        topic_name (str): Topic name for the exercises
        subtopic_name (str): Subtopic name for the exercises
        
    Returns:
        tuple: (success, message, exercise_count)
    """
    # Validate education level
    if education_level not in EDUCATION_LEVELS:
        return False, f"Invalid education level: {education_level}", 0
    
    # Get or create topic
    topic = Topic.query.filter_by(name=topic_name).first()
    if not topic:
        topic = Topic(name=topic_name)
        db.session.add(topic)
        db.session.flush()
    
    # Get or create subtopic
    subtopic = Subtopic.query.filter_by(name=subtopic_name, topic_id=topic.id).first()
    if not subtopic:
        subtopic = Subtopic(name=subtopic_name, topic_id=topic.id)
        db.session.add(subtopic)
        db.session.flush()
    
    # Pattern to extract exercises with metadata
    exercise_pattern = r'% BEGIN_EXERCISE\s+% DIFFICULTY: (\d+)\s+(.*?)% BEGIN_SOLUTION\s+(.*?)% END_SOLUTION\s+% END_EXERCISE'
    
    exercises = re.findall(exercise_pattern, file_content, re.DOTALL)
    
    if not exercises:
        return False, "No exercises found in the file. Please check the format.", 0
    
    exercise_count = 0
    
    for difficulty, content, solution in exercises:
        try:
            # Validate difficulty
            difficulty = int(difficulty)
            if difficulty not in [1, 2, 3]:
                logger.warning(f"Invalid difficulty level: {difficulty}, setting to 1")
                difficulty = 1
            
            # Create exercise
            exercise = Exercise(
                content=content.strip(),
                solution=solution.strip(),
                difficulty=difficulty,
                education_level=education_level,
                subtopic_id=subtopic.id,
                file_source=filename
            )
            
            db.session.add(exercise)
            exercise_count += 1
            
        except Exception as e:
            logger.error(f"Error processing exercise: {str(e)}")
            continue
    
    try:
        db.session.commit()
        return True, f"Successfully processed {exercise_count} exercises", exercise_count
    except Exception as e:
        db.session.rollback()
        return False, f"Error saving exercises to database: {str(e)}", 0
