import os
import subprocess
import sys
import platform

class Audio:
    def __init__(self, computer):
        self.computer = computer

    def transcribe(self, audio_path, display=True):
        # Define the directory to store the model
        # ~/interpreters/models ??
        model_dir = os.path.expanduser('~/models')
        os.makedirs(model_dir, exist_ok=True)
        
        # Define the model file path
        model_path = os.path.join(model_dir, 'whisper-tiny.en.llamafile')
        
        # Download the model if it doesn't exist
        if not os.path.exists(model_path):
            # Try different download methods across platforms
            download_success = False
            download_url = 'https://huggingface.co/Mozilla/whisperfile/resolve/main/whisper-tiny.en.llamafile'
            
            def try_download_with_python():
                try:
                    import urllib.request
                    urllib.request.urlretrieve(download_url, model_path)
                    return True
                except Exception:
                    return False
            
            # Try platform-specific methods first
            if os.name == 'nt':  # Windows
                try:
                    # Try powershell first
                    ps_command = f'Invoke-WebRequest -Uri "{download_url}" -OutFile "{model_path}"'
                    subprocess.run(['powershell', '-Command', ps_command], check=True)
                    download_success = True
                except Exception:
                    # Try curl (included in recent Windows versions)
                    try:
                        subprocess.run(['curl', '-L', '-o', model_path, download_url], check=True)
                        download_success = True
                    except Exception:
                        download_success = try_download_with_python()
            
            else:  # macOS or Linux
                # Try curl first (pre-installed on macOS)
                try:
                    subprocess.run(['curl', '-L', '-o', model_path, download_url], check=True)
                    download_success = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Try wget
                    try:
                        subprocess.run(['wget', '-O', model_path, download_url], check=True)
                        download_success = True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # If wget/curl failed, try to install them
                        if sys.platform == 'darwin':  # macOS
                            try:
                                # Try installing wget via homebrew
                                subprocess.run(['brew', 'install', 'wget'], check=True)
                                subprocess.run(['wget', '-O', model_path, download_url], check=True)
                                download_success = True
                            except Exception:
                                download_success = try_download_with_python()
                        else:  # Linux
                            # Try Alpine Linux first (for ffmpeg installation if needed)
                            try:
                                subprocess.run(['apk', '--version'], check=True)
                                # We're on Alpine, try to install wget
                                subprocess.run(['sudo', 'apk', 'add', 'wget'], check=True)
                                subprocess.run(['wget', '-O', model_path, download_url], check=True)
                                download_success = True
                            except Exception:
                                # Fall back to Python's urllib
                                download_success = try_download_with_python()
            
            if not download_success:
                raise RuntimeError("Failed to download model file. Please ensure you have internet access and try again.")

        # Add ffmpeg check
        def check_ffmpeg():
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                # Try to install ffmpeg if we're on Alpine
                try:
                    subprocess.run(['apk', '--version'], check=True)
                    # We're on Alpine, install ffmpeg
                    subprocess.run(['sudo', 'apk', 'add', 'ffmpeg'], check=True)
                    return True
                except Exception:
                    return False

        # Convert the audio file to a supported format
        # Check if the format is supported
        supported_formats = ['wav']
        _, ext = os.path.splitext(audio_path)
        
        converted_file = None
        if ext[1:].lower() not in supported_formats:
            # Check if ffmpeg is installed
            if not check_ffmpeg():
                raise RuntimeError("ffmpeg is required for audio conversion. Please install it first.")
                
            # Convert to a supported format in a temp directory
            temp_dir = os.path.join(os.path.dirname(model_path), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_output = os.path.join(temp_dir, f"temp_audio.wav")
            try:
                subprocess.run(['ffmpeg', '-i', audio_path, temp_output], check=True)
                audio_path = temp_output
                converted_file = temp_output
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error converting audio file: {e}")

        command = [model_path, '-f', "'" + audio_path + "'", '--no-prints']
        print("Running command: " + " ".join(command))

        # Make the file executable (only on Unix-like systems)
        if os.name != 'nt':  # Skip on Windows
            # Make file executable for user
            os.chmod(model_path, os.stat(model_path).st_mode | 0o755)
            
            # Only need special handling for Mac M1/M2
            if sys.platform == 'darwin' and platform.machine() == 'arm64':
                command = ['arch', '-x86_64'] + command

        # Run the transcription
        process = subprocess.run(
            " ".join(command),  # Join command into a single string
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # Add shell=True to properly execute the llamafile
        )
        
        full_output = process.stdout
        return_code = process.returncode
        
        # Clean up converted file if it exists
        if converted_file and os.path.exists(converted_file):
            os.remove(converted_file)
        
        if return_code == 0:
            return full_output
        else:
            error_output = process.stderr.read()
            return f"Transcription failed with return code {return_code}: {error_output}"