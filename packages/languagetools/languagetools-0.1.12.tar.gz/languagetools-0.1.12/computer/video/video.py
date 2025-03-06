import os
import subprocess
import select
import time
import shutil

def run_with_output(cmd):
    """Helper function to run commands and stream their output."""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    output = []
    while True:
        reads = [process.stdout.fileno(), process.stderr.fileno()]
        ret = select.select(reads, [], [], 0.1)  # 0.1 second timeout
        
        for fd in ret[0]:
            if fd == process.stdout.fileno():
                line = process.stdout.readline()
                if line:
                    output.append(line)
            if fd == process.stderr.fileno():
                line = process.stderr.readline()
                if line:
                    output.append(line)
        
        if process.poll() is not None:
            for line in process.stdout.readlines():
                output.append(line)
            for line in process.stderr.readlines():
                output.append(line)
            break
        
        time.sleep(0.001)
    
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)
    
    return ''.join(output)

def install_docker():
    """
    Ensure Docker is installed and the daemon is running.
    This function checks if Docker is available and, if not, installs it and starts the daemon.
    """
    try:
        run_with_output(['docker', '--version'])
    except subprocess.CalledProcessError:
        print("Docker not found; installing...")
        run_with_output(['sudo', 'apk', 'add', '--no-cache', 'docker'])
    
    try:
        run_with_output(['sudo', 'rc-update', 'add', 'docker', 'default'])
    except subprocess.CalledProcessError:
        print("Warning: Could not add Docker to default services.")
    
    # Try starting Docker using several common methods
    started = False
    for cmd in (['sudo', 'service', 'docker', 'start'],
                ['sudo', '/etc/init.d/docker', 'start'],
                ['sudo', 'rc-service', 'docker', 'start']):
        try:
            run_with_output(cmd)
            started = True
            break
        except subprocess.CalledProcessError:
            continue
    
    if not started:
        raise Exception("Failed to start Docker daemon using multiple methods.")
    
    # Wait for the Docker daemon to become responsive
    max_retries = 10
    for i in range(max_retries):
        try:
            run_with_output(['sudo', 'docker', 'info'])
            print("Docker daemon is running.")
            return
        except subprocess.CalledProcessError:
            print(f"Waiting for Docker daemon to start (attempt {i+1}/{max_retries})...")
            time.sleep(2)
    
    raise Exception("Docker daemon failed to start after multiple attempts.")

def render_jsx(jsx_path, composition_id, output_path):
    """
    Renders a Remotion video by taking:
      - jsx_path: path to the JSX entry file
      - composition_id: the composition ID (e.g. "main")
      - output_path: the file path where the rendered video should be saved
    """
    # Ensure Docker is installed and running.
    install_docker()
    
    # Create a temporary Docker build context.
    context_dir = "/tmp/interpreter/render_context"
    if os.path.exists(context_dir):
        shutil.rmtree(context_dir)
    os.makedirs(context_dir, exist_ok=True)
    
    # Copy the JSX file into the context.
    jsx_filename = os.path.basename(jsx_path)
    shutil.copy(jsx_path, os.path.join(context_dir, jsx_filename))
    
    # Create an entry point that registers the root
    entry_filename = "entry.jsx"
    entry_content = f'''import {{ registerRoot }} from 'remotion';
import * as RemotionComponent from './{jsx_filename}';

// Handle both default and named exports
const Component = RemotionComponent.default || RemotionComponent;
registerRoot(Component);
'''
    with open(os.path.join(context_dir, entry_filename), "w") as f:
        f.write(entry_content)
    
    # Write a minimal package.json
    package_json_content = '''{
  "name": "render-project",
  "version": "1.0.0",
  "dependencies": {
    "remotion": "^4.0.258",
    "@remotion/cli": "^4.0.258"
  }
}'''
    with open(os.path.join(context_dir, "package.json"), "w") as f:
        f.write(package_json_content)
    
    # Create a Dockerfile that installs system dependencies and the Remotion CLI
    dockerfile_path = os.path.join(context_dir, "Dockerfile")
    dockerfile_content = '''FROM node:16-slim

# Set working directory
WORKDIR /app

# Install system packages for headless browser and display emulation
RUN apt-get update && apt-get install -y \\
    xvfb \\
    chromium \\
    && rm -rf /var/lib/apt/lists/*

# Install the Remotion CLI globally
RUN npm install -g @remotion/cli

# Copy package.json and install node dependencies
COPY package.json ./
RUN npm install

# Copy all files (including your JSX file)
COPY . .
'''
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    # Build the Docker image.
    image_tag = "remotion-render:latest"
    print("Building Docker image...")
    build_output = run_with_output(["sudo", "docker", "build", "-t", image_tag, context_dir])
    print("Build output:")
    print(build_output)
    
    # Run the Docker container with the render command
    print("Running Docker container...")
    run_cmd = [
        "sudo", "docker", "run", "--rm", image_tag,
        "remotion", "render", entry_filename, composition_id, output_path
    ]
    print("Running command:", " ".join(run_cmd))
    render_output = run_with_output(run_cmd)
    print("Render output:")
    print(render_output)
    return render_output

class Video:
    def __init__(self, computer):
        self.computer = computer
        
    def render(self, path, composition_id="main", output_file="output.mp4"):
        try:
            return render_jsx(path, composition_id, output_file)
        except Exception as e:
            print(f"Failed to render video: {e}")
            raise
