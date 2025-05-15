import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import tempfile
from flask import send_file

# Configure logging
logger = logging.getLogger(__name__)

class PdfGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='ExerciseTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='Exercise',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='Solution',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.blue
        ))
    
    def _clean_tex(self, tex_content):
        """
        Clean TeX content for simplified PDF rendering.
        This is a simple version that just removes the most common TeX commands.
        In a real-world scenario, you would use a more sophisticated TeX-to-PDF converter.
        """
        # Remove common TeX environments and commands
        cleaned = tex_content
        # Replace \begin{...} and \end{...}
        cleaned = re.sub(r'\\begin{.*?}', '', cleaned)
        cleaned = re.sub(r'\\end{.*?}', '', cleaned)
        # Replace math mode delimiters
        cleaned = cleaned.replace('$', '')
        # Replace common math commands
        replacements = {
            r'\\frac{(.*?)}{(.*?)}': r'\1/\2',
            r'\\sqrt{(.*?)}': r'√(\1)',
            r'\\mathbb{R}': 'ℝ',
            r'\\rightarrow': '→',
            r'\\leftarrow': '←',
            r'\\geq': '≥',
            r'\\leq': '≤',
            r'\\neq': '≠',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\pi': 'π',
            r'\\times': '×',
            r'\\div': '÷',
            r'\\cdot': '·'
        }
        
        for pattern, replacement in replacements.items():
            cleaned = re.sub(pattern, replacement, cleaned)
        
        return cleaned

    def generate_exercise_pdf(self, exercises, include_solutions=False, title="Mathematics Exercises"):
        """
        Generate a PDF with exercises and optionally solutions.
        
        Args:
            exercises (list): List of Exercise objects
            include_solutions (bool): Whether to include solutions in the PDF
            title (str): Title for the PDF
            
        Returns:
            file: PDF file response
        """
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_filename = temp_file.name
            temp_file.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                temp_filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content
            content = []
            
            # Add title
            content.append(Paragraph(title, self.styles['ExerciseTitle']))
            content.append(Spacer(1, 0.25 * inch))
            
            # Add exercises
            for i, exercise in enumerate(exercises, 1):
                # Exercise number and content
                exercise_text = f"Exercise {i}: {self._clean_tex(exercise.content)}"
                content.append(Paragraph(exercise_text, self.styles['Exercise']))
                
                # Add solution if requested
                if include_solutions:
                    solution_text = f"Solution: {self._clean_tex(exercise.solution)}"
                    content.append(Paragraph(solution_text, self.styles['Solution']))
                
                content.append(Spacer(1, 0.25 * inch))
            
            # Build PDF
            doc.build(content)
            
            return temp_filename
        
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None

    def send_pdf_file(self, temp_filename, download_name):
        """
        Send the generated PDF file as a response.
        
        Args:
            temp_filename (str): Temporary file path
            download_name (str): Name for the downloaded file
            
        Returns:
            response: Flask response with the PDF file
        """
        try:
            return send_file(
                temp_filename,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/pdf'
            )
        except Exception as e:
            logger.error(f"Error sending PDF file: {str(e)}")
            return None
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")

import re  # Make sure to import re for regex
