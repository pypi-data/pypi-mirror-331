"""
- Use CSS page-break-after: always; for page breaks.
- Set explicit height (e.g., height: 297mm; for A4) for full-page content.
- Example HTML structure for multi-page:

    <div style="page-break-after: always;">
        <!-- Content for page 1 -->
    </div>
    <div style="page-break-after: always;">
        <!-- Content for page 2 -->
    </div>
"""

from weasyprint import HTML
from weasyprint import CSS
from .template import template

class Document:
    def __init__(self, computer):
        self.computer = computer

    def template(self):
        template()

    def html_to_pdf(self, html_file, pdf_file):
        try:
            # Convert HTML to PDF using WeasyPrint
            print("Converting HTML to PDF...")
            HTML(filename=html_file).write_pdf(
                pdf_file,
                presentational_hints=True,  # Enables background graphics and other CSS hints
                stylesheets=[CSS(string='@page { margin: 0; }')]  # Create CSS object from string
            )
            print(f"PDF saved as {pdf_file}")

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise