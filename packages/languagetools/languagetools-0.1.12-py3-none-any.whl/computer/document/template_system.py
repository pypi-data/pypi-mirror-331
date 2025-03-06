from abc import ABC, abstractmethod
from datetime import datetime
import re
import pypandoc
from pathlib import Path
import subprocess
import os

class Field:
    def __init__(self, name, description, required=True, default=None):
        self.name = name
        self.description = description
        self.required = required
        self.default = default

    def get_input(self):
        while True:
            print(f"\n{self.description}")
            if not self.required and self.default:
                print(f"(Press Enter for default: {self.default})")
            value = input("> ").strip()
            
            if not value and not self.required and self.default:
                return self.default
            
            try:
                validated = self.validate(value)
                return validated
            except ValueError as e:
                print(f"Error: {str(e)}")

    @abstractmethod
    def validate(self, value):
        pass

class TextField(Field):
    def __init__(self, name, description, min_length=1, max_length=1000, **kwargs):
        super().__init__(name, description, **kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        if len(value) < self.min_length:
            raise ValueError(f"Text must be at least {self.min_length} characters long")
        if len(value) > self.max_length:
            raise ValueError(f"Text must be no more than {self.max_length} characters long")
        return value

class DateField(Field):
    def __init__(self, name, description, format="%Y-%m-%d", **kwargs):
        super().__init__(name, description, **kwargs)
        self.format = format

    def validate(self, value):
        try:
            return datetime.strptime(value, self.format)
        except ValueError:
            raise ValueError(f"Invalid date format. Please use {self.format} (e.g., 2024-03-20)")

class EmailField(Field):
    def validate(self, value):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        return value

class AuthorsField(Field):
    def __init__(self, name, description, **kwargs):
        super().__init__(name, description, **kwargs)

    def validate(self, value):
        authors = [author.strip() for author in value.split(',')]
        if not authors:
            raise ValueError("At least one author is required")
        return authors

class ReferenceField(Field):
    def __init__(self, name, description, **kwargs):
        super().__init__(name, description, **kwargs)

    def get_input(self):
        references = []
        print(f"\n{self.description}")
        print("Enter reference details (or type 'done' when finished):")
        
        while True:
            print("\nReference type? (or 'done' to finish)")
            print("(a) Article")
            print("(b) Book")
            print("(c) Book Chapter")
            
            ref_type = input("> ").strip().lower()
            if ref_type == 'done':
                break
                
            if ref_type not in ['a', 'b', 'c']:
                print("Invalid reference type. Please try again.")
                continue
            
            ref = {}
            if ref_type == 'a':  # Article
                ref['type'] = 'Article'
                ref['authors'] = input("Authors (format: Last, First and Last2, First2): ").strip()
                ref['year'] = input("Year: ").strip()
                ref['title'] = input("Title: ").strip()
                ref['journal'] = input("Journal: ").strip()
                ref['volume'] = input("Volume: ").strip()
                ref['number'] = input("Number (optional, press enter to skip): ").strip()
                ref['pages'] = input("Pages: ").strip()
            elif ref_type == 'b':  # Book
                ref['type'] = 'Book'
                ref['authors'] = input("Authors (format: Last, First and Last2, First2): ").strip()
                ref['year'] = input("Year: ").strip()
                ref['title'] = input("Title: ").strip()
                ref['publisher'] = input("Publisher: ").strip()
                ref['address'] = input("Address (optional, press enter to skip): ").strip()
            else:  # Book Chapter
                ref['type'] = 'InBook'
                ref['authors'] = input("Chapter Authors (format: Last, First and Last2, First2): ").strip()
                ref['year'] = input("Year: ").strip()
                ref['title'] = input("Chapter Title: ").strip()
                ref['booktitle'] = input("Book Title: ").strip()
                ref['editors'] = input("Editors (format: Last, First and Last2, First2): ").strip()
                ref['publisher'] = input("Publisher: ").strip()
                ref['pages'] = input("Pages: ").strip()
            
            # Generate citation key
            first_author_last = ref['authors'].split(',')[0].strip()
            citation_key = f"{first_author_last}{ref['year']}"
            ref['citation_key'] = citation_key
            
            references.append(ref)
            print(f"\nReference added! Citation key: {citation_key}")
        
        return references

    def validate(self, value):
        # References are validated during input
        return value

    def to_bibtex(self, references):
        """Convert references to BibTeX format"""
        bibtex = ""
        for ref in references:
            if ref['type'] == 'Article':
                bibtex += f"""@Article{{{ref['citation_key']},
    author = {{{ref['authors']}}},
    title = {{{{{ref['title']}}}}},
    journal = {{{ref['journal']}}},
    year = {{{ref['year']}}},
    volume = {{{ref['volume']}}},"""
                if ref['number']:
                    bibtex += f"""
    number = {{{ref['number']}}},"""
                bibtex += f"""
    pages = {{{ref['pages']}}},
    }}

"""
            elif ref['type'] == 'Book':
                bibtex += f"""@Book{{{ref['citation_key']},
    author = {{{ref['authors']}}},
    title = {{{{{ref['title']}}}}},
    publisher = {{{ref['publisher']}}},
    year = {{{ref['year']}}},"""
                if ref['address']:
                    bibtex += f"""
    address = {{{ref['address']}}},"""
                bibtex += """
    }

"""
            elif ref['type'] == 'InBook':
                bibtex += f"""@InBook{{{ref['citation_key']},
    author = {{{ref['authors']}}},
    title = {{{{{ref['title']}}}}},
    booktitle = {{{{{ref['booktitle']}}}}},
    publisher = {{{ref['publisher']}}},
    year = {{{ref['year']}}},
    editor = {{{ref['editors']}}},
    pages = {{{ref['pages']}}},
    }}

"""
        return bibtex

class Template(ABC):
    def __init__(self):
        self.fields = self.define_fields()
        self.data = {}
        # Create a unique timestamp-based directory for this document
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = Path('/tmp/lt_documents') / timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def define_fields(self):
        pass

    def fill_template(self):
        print(f"\nFilling out {self.__class__.__name__}")
        print("=" * 40)
        
        # Get all fields except content first
        for field in self.fields:
            if field.name != 'content':
                self.data[field.name] = field.get_input()
        
        # After collecting references, show citation instructions
        if 'references' in self.data:
            print("\nYour references have been saved. You can cite them in your content using:")
            for ref in self.data['references']:
                print(f"\\cite{{{ref['citation_key']}}} - {ref['authors']} ({ref['year']}): {ref['title']}")
            print("\nFor example:")
            print("As mentioned by \\cite{Smith2024}, this theory has merit.")
            print("\\textcite{Smith2024} argued that...")
            print("\nNow you can enter your content:")
        
        # Now get the content
        for field in self.fields:
            if field.name == 'content':
                self.data[field.name] = field.get_input()
        
        return self.data

    def sanitize_filename(self, title):
        """Convert title to a valid filename"""
        # Remove invalid chars and convert spaces to underscores
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '_', filename).strip('-_')
        return filename.lower()

    @abstractmethod
    def export(self):
        """Export the template to a file in the appropriate format"""
        pass

class TextTemplate(Template):
    def define_fields(self):
        return [
            TextField("title", "Enter the text title:"),
            TextField("body", "Enter the body text:", min_length=1, max_length=5000),
        ]

    def export(self):
        title = self.data['title']
        filename = self.sanitize_filename(title) + '.html'
        filepath = self.output_dir / filename
        
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.data['title']}</title>
</head>
<body>
    <h1>{self.data['title']}</h1>
    <div class="content">
        <p>{self.data['body']}</p>
    </div>
</body>
</html>
"""
        with open(filepath, 'w') as f:
            f.write(content)
            
        return filepath

class LaTeXAPATemplate(Template):
    def define_fields(self):
        return [
            # Metadata fields
            TextField("paper_title", "Enter the paper title:", max_length=200),
            TextField("short_title", "Enter a short title (for headers):", max_length=50),
            TextField("author_name", "Enter your name:"),
            DateField("due_date", "Enter due date (YYYY-MM-DD):"),
            TextField("school_name", "Enter school name:"),
            TextField("course_number", "Enter course number:"),
            TextField("professor_name", "Enter professor name:"),
            TextField("abstract", "Enter abstract (50-500 characters):", min_length=50, max_length=500),
            TextField("keywords", "Enter keywords (comma-separated):", required=False, default=""),
            TextField("content", "Enter your paper content in Markdown format. Use # for major sections, ## for subsections:", 
                     min_length=1, max_length=50000),
            # New references field
            ReferenceField("references", "Let's add your references"),
        ]

    def markdown_to_latex(self, markdown_text):
        """Convert markdown to LaTeX format."""
        # First, replace literal \n with actual newlines
        markdown_text = markdown_text.replace('\\n', '\n')
        
        # Convert markdown to LaTeX using pypandoc
        latex_content = pypandoc.convert_text(markdown_text, 'latex', format='markdown')
        
        # Clean up any remaining problematic characters
        latex_content = latex_content.replace('\\\\', '\\')  # Fix double backslashes
        latex_content = latex_content.replace('\\#', '#')    # Fix escaped hashtags
        
        return latex_content

    def export(self):
        title = self.data['paper_title']
        base_filename = self.sanitize_filename(title)
        
        # Create bibliography file
        bib_filename = base_filename + '.bib'
        bib_filepath = self.output_dir / bib_filename
        
        # Convert references to BibTeX and save
        reference_field = next(field for field in self.fields if isinstance(field, ReferenceField))
        bibtex_content = reference_field.to_bibtex(self.data['references'])
        with open(bib_filepath, 'w') as f:
            f.write(bibtex_content)
        
        # Create main tex file
        tex_filename = base_filename + '.tex'
        tex_filepath = self.output_dir / tex_filename
        
        # Convert markdown content to LaTeX
        latex_content = self.markdown_to_latex(self.data['content'])
        
        # LaTeX template with proper document structure
        content = r"""\documentclass[stu,12pt,floatsintext]{apa7}

\usepackage[american]{babel}
\usepackage{csquotes}
\usepackage[style=apa,sortcites=true,sorting=nyt,backend=biber]{biblatex}
\DeclareLanguageMapping{american}{american-apa}
\addbibresource{""" + bib_filename + r"""}

\usepackage[T1]{fontenc}
\usepackage{mathptmx}

\title{""" + self.data['paper_title'] + r"""}
\shorttitle{""" + self.data['short_title'] + r"""}
\author{""" + self.data['author_name'] + r"""}
\affiliation{""" + self.data['school_name'] + r"""}
\course{""" + self.data['course_number'] + r"""}
\professor{""" + self.data['professor_name'] + r"""}
\duedate{""" + self.data['due_date'].strftime('%B %d, %Y') + r"""}

\abstract{""" + self.data['abstract'] + r"""}

""" + (r"\keywords{" + self.data['keywords'] + "}" if self.data['keywords'] else "% No keywords provided") + r"""

\begin{document}
\maketitle

""" + latex_content + r"""

\printbibliography

\end{document}"""
        
        with open(tex_filepath, 'w') as f:
            f.write(content)
        
        try:
            # First pdflatex run
            cmd = ['pdflatex', '-interaction=nonstopmode', f'-output-directory={self.output_dir}', str(tex_filepath)]
            print(f"\nRunning command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Run biber for bibliography
            cmd = ['biber', '--output-directory', str(self.output_dir), base_filename]
            print(f"\nRunning command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Second pdflatex run to incorporate bibliography
            cmd = ['pdflatex', '-interaction=nonstopmode', f'-output-directory={self.output_dir}', str(tex_filepath)]
            print(f"\nRunning command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Final pdflatex run for references
            cmd = ['pdflatex', '-interaction=nonstopmode', f'-output-directory={self.output_dir}', str(tex_filepath)]
            print(f"\nRunning command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
        except subprocess.CalledProcessError as e:
            print(f"\nError during LaTeX compilation:")
            print(f"Command '{' '.join(e.cmd)}' failed")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
            raise
        
        # Return the path to the generated PDF
        pdf_filepath = self.output_dir / f"{base_filename}.pdf"
        return pdf_filepath

# Update the TEMPLATES dictionary to use the new template classes
TEMPLATE_CLASSES = {
    'TXT': {
        'Simple': TextTemplate  # Add the simple text template
    },
    'PDF': {
        'Academic': {
            'APA': LaTeXAPATemplate,  # Updated to use the LaTeX APA template
        },
    },
}