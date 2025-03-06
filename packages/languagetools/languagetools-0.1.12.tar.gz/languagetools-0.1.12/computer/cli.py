"""
Command-line interface for the languagetools project.
"""
from typer import Typer
from typing import Any
import json
from .computer import Computer
import inspect

app = Typer(help="Command-line tool to interact with the languagetools suite.")

# Create a single Computer instance
computer = Computer()

# Create sub-apps for each module
ai_app = Typer(help="AI functionalities")
audio_app = Typer(help="Audio operations")
browser_app = Typer(help="Browser automation")
document_app = Typer(help="Document operations")
files_app = Typer(help="File operations")
vision_app = Typer(help="Vision and image operations")
image_app = Typer(help="Image operations")
video_app = Typer(help="Video operations")

# Map modules to their respective Typer apps
MODULE_APPS = {
    "ai": ai_app,
    "audio": audio_app,
    "browser": browser_app,
    "document": document_app,
    "files": files_app,
    "vision": vision_app,
    "image": image_app,
    "audio": audio_app,
    "video": video_app,
}

# Add all sub-apps to the main app
for name, typer_app in MODULE_APPS.items():
    app.add_typer(typer_app, name=name)

### These are needed because many methods just return their result, and we want to print it

def print_result(result: Any) -> None:
    """Print the result in a readable format"""
    if result is None:
        return
    
    if isinstance(result, (dict, list)):
        # Pretty print JSON-serializable objects
        print(json.dumps(result, indent=2))
    else:
        print(result)

def create_wrapper(func):
    """Create a wrapper that handles any function signature"""
    func_name = func.__name__
    sig = inspect.signature(func)
    
    # Create a wrapper that accepts *args and **kwargs
    def wrapper(*args, **kwargs):
        # print(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        if func_name == "cloud":
            tool = kwargs.get('tool')
            input_data = kwargs.get('input')
            tool_input = json.loads(input_data) if isinstance(input_data, str) else input_data
            result = func(tool, tool_input)
        else:
            result = func(*args, **kwargs)
        print_result(result)
        return result
    
    # Copy the signature and metadata to the wrapper
    wrapper.__signature__ = sig
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__
    return wrapper

# Automatically create CLI commands from the Computer class methods
for module_name, typer_app in MODULE_APPS.items():
    module = getattr(computer, module_name)
    for method_name in dir(module):
        if not method_name.startswith('_'):  # Skip private methods
            method = getattr(module, method_name)
            if callable(method):
                wrapped_method = create_wrapper(method)
                typer_app.command(method_name)(wrapped_method)

def main():
    app()

if __name__ == "__main__":
    main()