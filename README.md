# Generador de Ejercicios de Matemáticas

Una aplicación para la creación de ejercicios matemáticos con modos estudiante, profesor y editor. Permite generar hojas de ejercicios personalizadas a partir de archivos .tex.

## Características principales

- **Modo Descarga**: Generación de hojas de ejercicios con o sin soluciones (acceso público).
- **Modo Editor**: Subida de archivos .tex con ejercicios para ampliar la base de datos (acceso restringido).
- **Selección dinámica**: Elección de ejercicios por tema, subtema, nivel educativo y dificultad.
- **Generación de PDFs y .tex**: Creación de documentos descargables con los ejercicios seleccionados.
- **Control de acceso**: Protección del modo editor mediante autenticación de usuarios.

## Instrucciones de instalación

### Requisitos previos

- Python 3.7 o superior
- PostgreSQL

### Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tuusuario/generador-ejercicios-matematicas.git
   cd generador-ejercicios-matematicas
   ```

2. Ejecuta el script de configuración y ejecución:
   ```
   python setup_and_run.py
   ```

   Este script se encargará de:
   - Instalar las dependencias necesarias
   - Configurar la base de datos
   - Crear un usuario administrador inicial (si no existe)
   - Iniciar la aplicación
   
3. Durante la primera ejecución, el script te pedirá crear un usuario administrador para el acceso al modo editor.

### Configuración manual (alternativa)

Si prefieres configurar manualmente:

1. Instala las dependencias:
   ```
   pip install -r requerimientos.txt
   ```

2. Configura las variables de entorno:
   - `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL
   - `FLASK_SECRET_KEY`: Clave secreta para Flask (opcional)

3. Ejecuta la aplicación:
   ```
   python main.py
   ```

## Formato del archivo .tex

Para subir ejercicios en modo Editor, los archivos .tex deben seguir este formato:

```
% BEGIN_EXERCISE
% DIFFICULTY: 2
Este es el contenido del ejercicio en formato LaTeX.
% BEGIN_SOLUTION
Esta es la solución en formato LaTeX.
% END_SOLUTION
% END_EXERCISE
```

- `DIFFICULTY`: Debe ser 1 (fácil), 2 (medio) o 3 (difícil).
- Cada archivo puede contener múltiples ejercicios siguiendo este formato.

## Tecnologías utilizadas

- Flask: Framework web
- SQLAlchemy: ORM para la base de datos
- ReportLab: Generación de PDFs
- PostgreSQL: Base de datos
- Bootstrap: Interfaz de usuario