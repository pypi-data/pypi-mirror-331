import requests

class Image:
    def __init__(self, computer):
        self.computer = computer

    def generate(self, prompt: str, output_path: str = None):
        url = self.computer.ai.cloud("create_image", {"prompt": prompt})
        if output_path:
            print("Saving image to", output_path)
            response = requests.get(url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        else:
            return url

    def upscale(self, image_url: str, output_path: str = None, upload_first: bool = False):
        if upload_first:
            image_url = self.computer.files.upload(image_url)
        try:
            response = requests.head(image_url)
            if response.status_code != 200:
                print("This accepts URLs, so remember to run `lt files upload <path>` to upload the image first.")
        except:
            print("This accepts URLs, so remember to run `lt files upload <path>` to upload the image first.")
        url = self.computer.ai.cloud("upscale_image", {"image": image_url})
        if output_path:
            print("Saving image to", output_path)
            response = requests.get(url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        else:
            return url

    def restore(self, image_url: str, output_path: str = None, upload_first: bool = False):
        if upload_first:
            image_url = self.computer.files.upload(image_url)
        try:
            response = requests.head(image_url)
            if response.status_code != 200:
                print("This accepts URLs, so remember to run `lt files upload <path>` to upload the image first.")
        except:
            print("This accepts URLs, so remember to run `lt files upload <path>` to upload the image first.")
        url = self.computer.ai.cloud("restore_image", {"image": image_url})
        if output_path:
            print("Saving image to", output_path)
            response = requests.get(url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        else:
            return url
