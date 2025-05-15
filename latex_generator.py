"""
Módulo para generar código LaTeX a partir de los ejercicios seleccionados.
"""

class LatexGenerator:
    """Clase para generar código LaTeX a partir de ejercicios"""
    
    @staticmethod
    def generate_latex_content(exercises, title="Ejercicios de Matemáticas"):
        """
        Genera el contenido LaTeX para los ejercicios seleccionados.
        
        Args:
            exercises (list): Lista de objetos Exercise
            title (str): Título para el documento
            
        Returns:
            dict: Diccionario con el código LaTeX en diferentes formatos
        """
        # Generar código LaTeX para ejercicios sin soluciones
        exercises_latex = LatexGenerator._generate_exercises_only(exercises, title)
        
        # Generar código LaTeX para ejercicios con soluciones
        solutions_latex = LatexGenerator._generate_with_solutions(exercises, title)
        
        # Generar documento LaTeX completo
        complete_latex = LatexGenerator._generate_complete_document(exercises, title)
        
        return {
            'exercises': exercises_latex,
            'solutions': solutions_latex,
            'complete': complete_latex
        }
    
    @staticmethod
    def _generate_exercises_only(exercises, title):
        """Genera código LaTeX con sólo los enunciados de los ejercicios"""
        exercises_latex = ""
        
        for i, exercise in enumerate(exercises, 1):
            exercises_latex += f"\\begin{{ejercicio}}[{i}]\n"
            exercises_latex += f"{exercise.content}\n"
            exercises_latex += "\\end{ejercicio}\n\n"
        
        return exercises_latex
    
    @staticmethod
    def _generate_with_solutions(exercises, title):
        """Genera código LaTeX con ejercicios y soluciones"""
        solutions_latex = ""
        
        for i, exercise in enumerate(exercises, 1):
            solutions_latex += f"\\begin{{ejercicio}}[{i}]\n"
            solutions_latex += f"{exercise.content}\n"
            solutions_latex += "\\end{ejercicio}\n\n"
            
            solutions_latex += "\\begin{solucion}\n"
            solutions_latex += f"{exercise.solution}\n"
            solutions_latex += "\\end{solucion}\n\n"
        
        return solutions_latex
    
    @staticmethod
    def _generate_complete_document(exercises, title):
        """Genera un documento LaTeX completo con preámbulo, ejercicios y soluciones"""
        # Preámbulo
        preamble = "\\documentclass[11pt,a4paper]{article}\n"
        preamble += "\\usepackage[spanish]{babel}\n"
        preamble += "\\usepackage[utf8]{inputenc}\n"
        preamble += "\\usepackage{amsmath,amssymb,amsfonts}\n"
        preamble += "\\usepackage{graphicx}\n"
        preamble += "\\usepackage{enumitem}\n\n"
        
        # Definir entornos personalizados
        preamble += "\\newcounter{ejercicio}\n"
        preamble += "\\newenvironment{ejercicio}[1][]{\\refstepcounter{ejercicio}\\par\\medskip\n"
        preamble += "   \\noindent\\textbf{Ejercicio~\\theejercicio.} #1\\rmfamily}{\\medskip}\n\n"
        
        preamble += "\\newenvironment{solucion}{\\par\\noindent\\textbf{Solución: }}{\\par\\medskip}\n\n"
        
        # Comienzo del documento
        doc_begin = "\\begin{document}\n\n"
        doc_begin += f"\\title{{{title}}}\n"
        doc_begin += "\\author{Generador de Ejercicios de Matemáticas}\n"
        doc_begin += "\\date{\\today}\n\n"
        doc_begin += "\\maketitle\n\n"
        
        # Ejercicios con soluciones
        content = LatexGenerator._generate_with_solutions(exercises, title)
        
        # Fin del documento
        doc_end = "\\end{document}"
        
        return preamble + doc_begin + content + doc_end