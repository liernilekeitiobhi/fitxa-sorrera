"""
Script para crear un usuario administrador inicial.

Uso:
    python create_admin.py username password

Este script debe ejecutarse después de configurar la base de datos, pero antes
de usar el sistema por primera vez.
"""

import sys
import os
from app import app, db
from models import User

def create_admin_user(username, password):
    """Crea un usuario administrador con las credenciales especificadas."""
    with app.app_context():
        # Verificar si ya existe el usuario
        if User.query.filter_by(username=username).first():
            print(f"El usuario '{username}' ya existe. No se ha creado ningún usuario nuevo.")
            return False
        
        # Crear nuevo usuario
        user = User()
        user.username = username
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Usuario administrador '{username}' creado exitosamente.")
        return True

def main():
    """Función principal que procesa los argumentos de línea de comandos."""
    if len(sys.argv) != 3:
        print("Uso: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    success = create_admin_user(username, password)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()