import subprocess
import time
from markdown_it import MarkdownIt
from AppKit import (
    NSFont, NSFontManager, NSAttributedString, NSMutableAttributedString,
    NSFontAttributeName, NSPasteboard, NSPasteboardTypeRTF, NSRange,
    NSDocumentTypeDocumentAttribute, NSRTFTextDocumentType
)

# Function to create attributed string
def create_attributed_string(text, font_name, size, is_bold=False):
    font = NSFont.fontWithName_size_(font_name, size)
    if is_bold:
        font = NSFontManager.sharedFontManager().convertFont_toHaveTrait_(font, 2)  # 2 is for bold
    attrs = {NSFontAttributeName: font}
    return NSAttributedString.alloc().initWithString_attributes_(text, attrs)

# Function to copy text to clipboard
def copy_text_to_clipboard(text):
    print("Starting to copy text to clipboard...")
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        print("Clipboard cleared")
        
        document_attributes = {NSDocumentTypeDocumentAttribute: NSRTFTextDocumentType}
        rtf_data, error = text.dataFromRange_documentAttributes_error_(
            NSRange(0, text.length()), 
            document_attributes,
            None
        )
        if error:
            print(f"Error generating RTF data: {error}")
            return
        
        print("RTF data generated")
        result = pasteboard.setData_forType_(rtf_data, NSPasteboardTypeRTF)
        print(f"Data set on pasteboard: {result}")
    except Exception as e:
        print(f"Exception occurred while copying to clipboard: {e}")
    print("Finished copying text to clipboard")

# Function to copy image to clipboard
def copy_image_to_clipboard(image_path):
    print(f"Copying image to clipboard: {image_path}")
    
    applescript_command = f'set the clipboard to (read (POSIX file "{image_path}") as JPEG picture)'
    subprocess.run(["osascript", "-e", applescript_command])

# Function to paste from clipboard
def paste_from_clipboard():
    print("Pasting from clipboard...")
    time.sleep(3)
    subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "v" using command down'])
    time.sleep(0.5)  # Small delay after pasting
    computer.keyboard.write("\n") 
    time.sleep(0.5)  # Small delay after pasting

# Function to parse markdown and type it
def parse_and_type_markdown(markdown):
    print("Parsing markdown...")
    md = MarkdownIt()
    tokens = md.parse(markdown)
    text_buffer = NSMutableAttributedString.alloc().init()
    bold = False
    
    for token in tokens:
        print(f"Token: {token.type}")
        if token.type == 'inline':
            for child in token.children:
                print(f"Child token: {child.type}")
                if child.type == 'text':
                    text_buffer.appendAttributedString_(create_attributed_string(child.content, "Helvetica", 14, is_bold=bold))
                elif child.type == 'strong_open':
                    bold = True
                elif child.type == 'strong_close':
                    bold = False￼
                elif child.type == 'image':
                    # Paste accumulated text
                    if text_buffer.length() > 0:
                        print("Copying text to clipboard...")
                        copy_text_to_clipboard(text_buffer)
                        paste_from_clipboard()
                    # Copy and paste the image
                    image_path = child.attrs['src']
                    copy_image_to_clipboard(image_path)
                    paste_from_clipboard()
                    # Clear the text buffer
                    text_buffer = NSMutableAttributedString.alloc().init()
    
    # Paste any remaining text
    if text_buffer.length() > 0:
        print("Copying remaining text to clipboard...")
        copy_text_to_clipboard(text_buffer)
        print("Pasting remaining text...")
        paste_from_clipboard()

# Example usage
markdown_input = """
**John Perkins**

![John Perkins](/Users/killianlucas/Desktop/JohnPerkins.jpg)

John Perkins is an American author and activist known for his book "Confessions of an Economic Hit Man," where he discusses his experiences working with international financial organizations.
"""

# Allow some time for the system to initialize
time.sleep(2)

# Parse and type the markdown
parse_and_type_markdown(markdown_input)