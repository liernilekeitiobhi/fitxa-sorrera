import os
import sys
import subprocess
import platform

def install_requirements():
    """Install required packages from requerimientos.txt"""
    print("Instalando paquetes requeridos...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requerimientos.txt"])

def setup_database():
    """Setup the database"""
    print("Configurando la base de datos...")
    # Import app only after requirements are installed
    from app import app, db
    
    with app.app_context():
        db.create_all()
        print("Base de datos configurada correctamente.")

def run_application():
    """Run the Flask application"""
    print("Iniciando la aplicación...")
    
    if platform.system() == 'Windows':
        # For Windows systems
        os.environ['FLASK_APP'] = 'main.py'
        os.environ['FLASK_ENV'] = 'development'
        subprocess.run([sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"])
    else:
        # For Unix-based systems (Linux, macOS)
        subprocess.run(["gunicorn", "--bind", "0.0.0.0:5000", "main:app"])

if __name__ == "__main__":
    try:
        install_requirements()
        setup_database()
        run_application()
    except Exception as e:
        print(f"Error durante la configuración: {str(e)}")
        sys.exit(1)