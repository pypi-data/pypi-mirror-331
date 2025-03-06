import os
from pathlib import Path
import re
from .template_system import TEMPLATE_CLASSES

def display_options(options, show_back=False):
    """Display available options with letter choices"""
    print("\nAvailable options:")
    for i, option in enumerate(options):
        print(f"({chr(97 + i)}) {option}")
    if show_back:
        print("(z) Go back")
    print("\nEnter your choice (letter):")

def get_valid_choice(options, show_back=False):
    """Get and validate user input"""
    while True:
        choice = input().lower().strip()
        if choice == 'z' and show_back:
            return 'BACK'
        if len(choice) == 1 and ord(choice) - ord('a') in range(len(options)):
            return list(options)[ord(choice) - ord('a')]
        print("Invalid choice. Please select a valid option:")

def select_template():
    """Main function to select template through CLI"""
    print("Welcome to the Template Selector!")
    
    history = []  # Stack to keep track of navigation
    current_level = TEMPLATE_CLASSES
    template_path = []  # Keep track of selections for final template name
    
    while True:
        print("\nPlease select an option:")
        display_options(current_level.keys(), bool(history))
        
        choice = get_valid_choice(current_level.keys(), bool(history))
        
        if choice == 'BACK':
            if history:
                current_level = history.pop()
                if template_path:
                    template_path.pop()
                continue
        else:
            template_path.append(choice)
            next_level = current_level[choice]
            if isinstance(next_level, dict):
                history.append(current_level)
                current_level = next_level
            else:
                # Return the template class and the full path for naming
                return ' - '.join(template_path), next_level

def template():
    # Get template selection
    template_path, template_class = select_template()
    
    # Instantiate and fill template
    template = template_class()
    filled_data = template.fill_template()
    
    # Export the template
    filepath = template.export()
    
    # Display results
    print("\nTemplate filled successfully!")
    print(f"Template type: {template_path}")
    print(f"Saved to: {filepath}")
    print("\nFinal Data:")
    print("=" * 40)
    for key, value in filled_data.items():
        if key == 'content':
            print(f"{key}: [Long content omitted]")
        else:
            print(f"{key}: {value}")
