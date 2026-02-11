from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Use built-in PDF fonts instead of registering external ones
PDF_FONT = 'Helvetica'
PDF_FONT_BOLD = 'Helvetica-Bold'
PDF_FONT_ITALIC = 'Helvetica-Oblique'
PDF_FONT_BOLD_ITALIC = 'Helvetica-BoldOblique'

# Database schema information
db_schema = {
    'admin': {
        'description': 'Stores administrator account information',
        'fields': {
            'id': 'Primary key, auto-increment',
            'username': 'Admin username (unique)',
            'password': 'Hashed password',
            'plain_password': 'Plain text password (for demo purposes only)'
        }
    },
    'careers': {
        'description': 'Stores information about different career paths',
        'fields': {
            'id': 'Primary key, auto-increment',
            'title': 'Career title (e.g., Data Analyst, Software Developer)',
            'description': 'Detailed description of the career',
            'required_skills': 'Comma-separated list of required skills',
            'category': 'Career category (e.g., Data, Technical, Creative)',
            'salary_range': 'Expected salary range for the career',
            'courses': 'Recommended courses for this career',
            'path': 'Typical career progression path'
        }
    },
    'career_progress': {
        'description': 'Tracks user progress in their chosen career path',
        'fields': {
            'id': 'Primary key, auto-increment',
            'user_id': 'Foreign key to users table',
            'career_id': 'Foreign key to careers table',
            'milestone': 'Specific milestone in the career path',
            'status': 'Status of the milestone (Not Started/In Progress/Completed)',
            'resume_id': 'Foreign key to resumes table',
            'note': 'Additional notes about the progress'
        }
    },
    'jobs': {
        'description': 'Stores job postings and opportunities',
        'fields': {
            'id': 'Primary key, auto-increment',
            'title': 'Job title',
            'company': 'Company name',
            'location': 'Job location',
            'job_type': 'Type of job (Full-time/Part-time/Internship/Remote)',
            'salary': 'Salary information',
            'url': 'URL to apply for the job',
            'description': 'Job description',
            'requirements': 'Required skills and qualifications',
            'posted_at': 'When the job was posted',
            'career_id': 'Foreign key to careers table'
        }
    },
    'users': {
        'description': 'Stores registered user information',
        'fields': {
            'id': 'Primary key, auto-increment',
            'name': 'User\'s full name',
            'email': 'User\'s email address (unique)',
            'password': 'Hashed password',
            'plain_password': 'Plain text password (for demo purposes only)',
            'profile_pic': 'Path to profile picture',
            'headline': 'Professional headline',
            'linkedin_url': 'LinkedIn profile URL',
            'is_admin': 'Boolean flag for admin status'
        }
    },
    'resumes': {
        'description': 'Stores user-uploaded resumes and parsed information',
        'fields': {
            'id': 'Primary key, auto-increment',
            'user_id': 'Foreign key to users table',
            'name': 'Name from resume',
            'summary': 'Professional summary/objective',
            'education': 'Education details',
            'experience': 'Work experience',
            'skills': 'Technical and soft skills',
            'projects': 'Projects completed',
            'certifications': 'Certifications earned',
            'contact_info': 'Contact information',
            'created_at': 'When the resume was uploaded/created'
        }
    },
    'interests': {
        'description': 'Stores user interests based on quizzes and preferences',
        'fields': {
            'id': 'Primary key, auto-increment',
            'user_id': 'Foreign key to users table',
            'interest_area': 'Area of interest (e.g., Technical, Creative, Data)',
            'resume_id': 'Foreign key to resumes table',
            'quiz_answers': 'JSON string of quiz answers'
        }
    },
    'projects': {
        'description': 'Stores user projects and portfolio items',
        'fields': {
            'id': 'Primary key, auto-increment',
            'user_id': 'Foreign key to users table',
            'title': 'Project title',
            'description': 'Project description',
            'skills': 'Technologies/skills used',
            'link': 'URL to project/demo',
            'created_at': 'When the project was added'
        }
    }
}

def create_data_dictionary():
    # Create PDF document
    doc = SimpleDocTemplate("Career_Guidance_Data_Dictionary.pdf", 
                           pagesize=letter,
                           rightMargin=36, leftMargin=36,
                           topMargin=36, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Update existing styles
    styles['Title'].fontName = PDF_FONT_BOLD
    styles['Title'].textColor = colors.HexColor('#1B5E20')
    styles['Title'].alignment = 1  # Center alignment
    
    # Create custom styles with unique names
    table_header_style = ParagraphStyle(
        'CustomTableHeader', 
        parent=styles['Normal'],
        fontSize=10, 
        textColor=colors.white,
        fontName=PDF_FONT_BOLD,
        alignment=1,  # Center alignment
        backColor=colors.HexColor('#2E7D32')  # Dark green background
    )
    
    table_text_style = ParagraphStyle(
        'CustomTableText',
        parent=styles['Normal'],
        fontSize=9, 
        textColor=colors.black,
        fontName=PDF_FONT
    )
    
    timestamp_style = ParagraphStyle(
        'CustomTimestamp',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.grey,
        fontName=PDF_FONT_ITALIC,
        alignment=2  # Right alignment
    )
    
    intro_style = ParagraphStyle(
        'CustomIntro',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName=PDF_FONT,
        leading=14
    )
    
    toc_style = ParagraphStyle(
        'CustomTOC',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#1B5E20'),
        fontName=PDF_FONT_BOLD
    )
    
    # TOC item style
    toc_item_style = ParagraphStyle(
        'CustomTOCItem',
        parent=styles['Normal'],
        textColor=colors.HexColor('#2E7D20'),
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=6
    )
    
    # Initialize story list
    story = []
    
    # Add title
    story.append(Paragraph("Career Guidance AI - Data Dictionary", styles['Title']))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated on: {timestamp}", timestamp_style))
    
    story.append(Spacer(1, 24))  # Add some space
    
    # Add introduction
    intro_text = """
    This document provides a comprehensive overview of the database schema for the Career Guidance AI system. 
    It includes details about each table, its columns, data types, and descriptions.
    """
    story.append(Paragraph(intro_text, intro_style))
    
    story.append(Spacer(1, 24))  # Add some space
    
    # Add TOC header
    story.append(Paragraph("Table of Contents", toc_style))
    story.append(Spacer(1, 12))  # Add some space
    
    # Add TOC items
    for i, table_name in enumerate(db_schema.keys(), 1):
        story.append(Paragraph(f"{i}. {table_name.capitalize()}", 
                             toc_item_style,
                             bulletText=str(i)))
    
    story.append(Spacer(1, 36))
    
    # Add tables for each database table
    for table_name, table_info in db_schema.items():
        # Add table name as section header
        header_style = ParagraphStyle(
            'TableHeader',
            fontSize=12,
            textColor=colors.HexColor('#1B5E20'),
            fontName=PDF_FONT_BOLD,
            spaceAfter=6
        )
        
        story.append(Paragraph(f"Table: {table_name.upper()}", header_style))
        
        # Add table description
        desc_style = ParagraphStyle(
            'TableDesc',
            fontSize=9,
            textColor=colors.black,
            fontName=PDF_FONT_ITALIC,
            spaceAfter=12
        )
        
        story.append(Paragraph(f"Description: {table_info['description']}", desc_style))
        
        # Create table data
        table_data = [
            [
                Paragraph('<b>Field Name</b>', table_header_style),
                Paragraph('<b>Data Type</b>', table_header_style),
                Paragraph('<b>Description</b>', table_header_style),
                Paragraph('<b>Constraints</b>', table_header_style)
            ]
        ]
        
        # Add rows for each field
        for field, description in table_info['fields'].items():
            # Extract data type from description (simplified for this example)
            data_type = 'VARCHAR(255)'
            if 'key' in field.lower():
                data_type = 'INT'
            elif field in ['created_at', 'posted_at']:
                data_type = 'TIMESTAMP'
            elif field == 'is_admin':
                data_type = 'BOOLEAN'
                
            # Determine constraints
            constraints = []
            if field == 'id':
                constraints.append('PRIMARY KEY')
            if 'password' in field:
                constraints.append('HASHED')
            if 'email' in field:
                constraints.append('UNIQUE')
                
            table_data.append([
                Paragraph(field, table_text_style),
                Paragraph(data_type, table_text_style),
                Paragraph(description, table_text_style),
                Paragraph(', '.join(constraints) if constraints else '-', table_text_style)
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 3*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                bg_color = colors.HexColor('#E8F5E9')  # Light green
            else:
                bg_color = colors.white
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bg_color),
            ]))
        
        story.append(table)
        story.append(Spacer(1, 24))  # Add space between tables
    
    # Add footer
    footer_style = ParagraphStyle(
        'Footer',
        fontSize=8,
        textColor=colors.grey,
        fontName=PDF_FONT_ITALIC,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph(
        "This data dictionary was automatically generated. "
        "For any questions, please contact the database administrator.",
        footer_style))
    
    # Build the PDF
    doc.build(story)
    print("Data dictionary generated successfully: Career_Guidance_Data_Dictionary.pdf")

if __name__ == "__main__":
    create_data_dictionary()
