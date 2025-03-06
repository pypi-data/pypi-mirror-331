import base64
import os
import random
import string
import tempfile

from html2image import Html2Image

from ..utils.lazy_import import lazy_import

html2image = lazy_import("html2image")


def html_to_png_base64(code):
    # Convert the HTML into an image using html2image
    hti = html2image.Html2Image()

    # Generate a random filename for the temporary image
    temp_filename = "".join(random.choices(string.digits, k=10)) + ".png"
    
    # Use tempfile to create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        hti.output_path = temp_dir
        hti.screenshot(
            html_str=code,
            save_as=temp_filename,
            size=(960, 540),
        )

        # Get the full path of the temporary image file
        file_location = os.path.join(temp_dir, temp_filename)

        # Convert the image to base64
        with open(file_location, "rb") as image_file:
            screenshot_base64 = base64.b64encode(image_file.read()).decode()

    # The temporary directory and its contents will be automatically deleted
    # when exiting the 'with' block

    return screenshot_base64
