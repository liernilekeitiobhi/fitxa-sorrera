import os
import sys
import subprocess
import platform
import getpass

def install_requirements():
    """Install required packages from requerimientos.txt"""
    print("Instalando paquetes requeridos...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_database():
    """Setup the database"""
    print("Configurando la base de datos...")
    
    # Set database URL if not already set
    if not os.environ.get("DATABASE_URL"):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        print(f"Usando base de datos SQLite en: {db_path}")
    
    # Import app only after requirements are installed
    from app import app, db
    
    with app.app_context():
        db.create_all()
        print("Base de datos configurada correctamente.")

def create_admin_user():
    """Create an admin user if none exists"""
    print("Verificando si existe un usuario administrador...")
    
    # Import models only after requirements are installed
    from models import User
    from app import app, db
    
    with app.app_context():
        # Check if any user exists
        if User.query.first() is None:
            print("No existe ningún usuario administrador. Vamos a crear uno.")
            
            while True:
                username = input("Nombre de usuario: ")
                if not username:
                    print("El nombre de usuario no puede estar vacío.")
                    continue
                
                # Check if username already exists
                if User.query.filter_by(username=username).first():
                    print("Este nombre de usuario ya está en uso. Por favor elige otro.")
                    continue
                
                # Get password with confirmation
                while True:
                    password = getpass.getpass("Contraseña: ")
                    if not password:
                        print("La contraseña no puede estar vacía.")
                        continue
                        
                    confirm_password = getpass.getpass("Confirma la contraseña: ")
                    if password != confirm_password:
                        print("Las contraseñas no coinciden. Inténtalo de nuevo.")
                        continue
                    
                    break
                
                # Create the user
                user = User()
                user.username = username
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                print(f"Usuario '{username}' creado exitosamente.")
                break
        else:
            print("Ya existe al menos un usuario en el sistema. No se ha creado ningún usuario nuevo.")

def run_application():
    """Run the Flask application"""
    print("Iniciando la aplicación...")
    
    # Set secret key if not already set
    if not os.environ.get("SESSION_SECRET"):
        os.environ["SESSION_SECRET"] = "desarrollo_clave_secreta_temporal"
        print("Aviso: Usando clave secreta temporal para desarrollo. Considera establecer SESSION_SECRET para producción.")
    
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
        create_admin_user()
        run_application()
    except Exception as e:
        print(f"Error durante la configuración: {str(e)}")
        sys.exit(1)