import os
import subprocess
import select
import time

def run_with_output(cmd):
    """Helper function to run commands and stream their output"""

    # print("Running command:", " ".join(cmd), flush=True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    output = []
    # Use select to read from whichever pipe has data
    while True:
        reads = [process.stdout.fileno(), process.stderr.fileno()]
        ret = select.select(reads, [], [], 0.1)  # 0.1 second timeout
        
        for fd in ret[0]:
            if fd == process.stdout.fileno():
                line = process.stdout.readline()
                if line:
                    # print(line, end='', flush=True)
                    output.append(line)
            if fd == process.stderr.fileno():
                line = process.stderr.readline()
                if line:
                    # print("STDERR:", line, end='', flush=True)  # Clearly mark stderr output
                    output.append(line)
        
        # Check if process has finished
        if process.poll() is not None:
            # Read any remaining output
            for line in process.stdout.readlines():
                print(line, end='', flush=True)
                output.append(line)
            for line in process.stderr.readlines():
                print("STDERR:", line, end='', flush=True)
                output.append(line)
            break
        
        # Add a small sleep to prevent CPU spinning
        time.sleep(0.001)
    
    if process.returncode != 0:
        print(''.join(output))
        raise subprocess.CalledProcessError(process.returncode, cmd)
    
    return ''.join(output)

def install_docker():
    # Check if Docker is installed
    try:
        run_with_output(['docker', '--version'])
    except subprocess.CalledProcessError:
        # Install Docker if not installed
        run_with_output(['sudo', 'apk', 'add', '--no-cache', 'docker'])
    
    # Add current user to docker group
    try:
        run_with_output(['sudo', 'addgroup', os.getenv('USER'), 'docker'])
    except subprocess.CalledProcessError:
        print("Warning: Could not add user to docker group")
    
    # Make sure Docker service is enabled and started
    try:
        # Create required directories
        run_with_output(['sudo', 'mkdir', '-p', '/etc/docker'])
        
        # Configure Docker daemon with custom DNS
        docker_config = {
            "dns": ["1.1.1.1", "8.8.8.8"],  # Try Cloudflare DNS first
            "mtu": 1400,
            "registry-mirrors": ["https://mirror.gcr.io"]  # Add Google's mirror
        }
        
        with open('/tmp/daemon.json', 'w') as f:
            import json
            json.dump(docker_config, f)
        run_with_output(['sudo', 'mv', '/tmp/daemon.json', '/etc/docker/daemon.json'])
        
        # Start Docker with new configuration
        run_with_output(['sudo', 'rc-service', 'docker', 'start'])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Error configuring Docker: {str(e)}")
        # Try alternative start methods
        try:
            run_with_output(['sudo', '/etc/init.d/docker', 'start'])
        except subprocess.CalledProcessError:
            raise Exception("Failed to start Docker daemon")
    
    # Wait for Docker daemon to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            run_with_output(['sudo', 'docker', 'info'])
            return  # Docker is running successfully
        except subprocess.CalledProcessError:
            if i < max_retries - 1:
                print(f"Waiting for Docker daemon to start (attempt {i+1}/{max_retries})...")
                time.sleep(2)
            else:
                raise Exception("Docker daemon failed to start after multiple attempts")


def create_dockerfile(path, api_key, api_base):
    dockerfile_content = f'''FROM python:3.11-slim

WORKDIR /app

# Install xvfb, bash, and additional debugging tools
RUN apt-get update && apt-get install -y \
    bash \
    xvfb \
    x11vnc \
    xterm && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

ENV OPENAI_API_KEY={api_key}
ENV OPENAI_BASE_URL={api_base}
ENV ANONYMIZED_TELEMETRY=false
ENV BROWSER_USE_LOGGING_LEVEL=debug
# ENV BROWSER_USE_HEADLESS=true
# ENV DEBUG=true
# ENV LOG_LEVEL=DEBUG

COPY . .
'''
    with open(path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)


def create_requirements_txt(path):
    requirements_content = '''
browser-use
    '''.strip()
    with open(path, 'w') as requirements:
        requirements.write(requirements_content)


def create_basic_test_script(path, task):
    basic_test_content = '''
import sys, os
import asyncio
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use import Agent, Controller

# print("Starting basic test script...", flush=True)
# print("Python version:", sys.version, flush=True)
# print("Checking if we can import required modules...", flush=True)

try:
    from langchain_openai import ChatOpenAI
    print("All modules imported successfully!", flush=True)
except Exception as e:
    print("Failed to import modules:", str(e), flush=True)
    sys.exit(1)

task = "{task}"
print("Task:", task, flush=True)

api_key = os.environ["OPENAI_API_KEY"]
base_url = os.environ["OPENAI_BASE_URL"]

print("API Key:", api_key, flush=True)
print("Base URL:", base_url, flush=True)

async def main():
    try:
        # print("Setting up browser configuration...", flush=True)
        browser = Browser(
            config=BrowserConfig(
                headless=True  # Enable headless mode
            )
        )
        
        controller = Controller()
        
        # print("Defining agent...", flush=True)
        agent = Agent(
            task=task,
            llm=ChatOpenAI(
                model="gpt-4o", 
                api_key=api_key, 
                base_url=base_url
            ),
            controller=controller,
            browser=browser,
            generate_gif=False
        )
        
        # print("Running agent...", flush=True)
        result = await agent.run()
        # print("Result:", result, flush=True)
        
        # Create history gif if needed
        agent.create_history_gif()
        
    except Exception as e:
        print("Error during execution:", str(e), flush=True)
        sys.exit(1)

# print("Starting asyncio.run(main())...", flush=True)
asyncio.run(main())
'''.strip()
    basic_test_content = basic_test_content.format(task=task.replace('"', '\\"'))
    
    # Write the file
    with open(path, 'w') as test_script:
        test_script.write(basic_test_content)


def build_and_run_docker():
    # Configure DNS for Docker daemon if needed
    docker_daemon_config = {
        "dns": ["8.8.8.8", "8.8.4.4"],  # Google's DNS servers
        "dns-opts": ["use-vc"],  # Use TCP for DNS queries
        "dns-search": [],  # Clear DNS search domains
        "mtu": 1400  # Lower MTU for better compatibility
    }
    
    try:
        # Test DNS resolution first
        try:
            run_with_output(['ping', '-c', '1', '8.8.8.8'])
        except subprocess.CalledProcessError:
            print("Warning: Cannot ping Google DNS, network might be unreachable")
        
        # Ensure /etc/docker directory exists
        run_with_output(['sudo', 'mkdir', '-p', '/etc/docker'])
        
        # Backup existing resolv.conf and create new one
        run_with_output(['sudo', 'cp', '/etc/resolv.conf', '/etc/resolv.conf.backup'])
        with open('/tmp/resolv.conf', 'w') as f:
            f.write("nameserver 8.8.8.8\nnameserver 8.8.4.4\n")
        run_with_output(['sudo', 'mv', '/tmp/resolv.conf', '/etc/resolv.conf'])
        
        # Write DNS configuration for Docker
        with open('/tmp/daemon.json', 'w') as f:
            import json
            json.dump(docker_daemon_config, f)
        run_with_output(['sudo', 'mv', '/tmp/daemon.json', '/etc/docker/daemon.json'])
        
        # Stop Docker completely
        try:
            run_with_output(['sudo', 'service', 'docker', 'stop'])
        except subprocess.CalledProcessError:
            pass
        
        # Small delay
        time.sleep(2)
        
        # Start Docker with new configuration
        try:
            run_with_output(['sudo', 'service', 'docker', 'start'])
        except subprocess.CalledProcessError:
            try:
                run_with_output(['sudo', 'rc-service', 'docker', 'start'])
            except subprocess.CalledProcessError:
                run_with_output(['sudo', '/etc/init.d/docker', 'start'])
        
        # Wait for Docker daemon to be ready
        time.sleep(3)
        
        # Test Docker connectivity
        try:
            run_with_output(['sudo', 'docker', 'info'])
        except subprocess.CalledProcessError:
            print("Warning: Docker daemon not responding properly")
            raise
        
        # Check if image already exists
        image_check = run_with_output(['sudo', 'docker', 'images', '-q', 'playwright-python-test'])
        if not image_check.strip():  # Image doesn't exist
            # Pull base image explicitly first with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    run_with_output(['sudo', 'docker', 'pull', 'python:3.11-slim'])
                    break
                except subprocess.CalledProcessError as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Pull attempt {attempt + 1} failed, retrying...")
                    time.sleep(5)
            
            # Build Docker image
            build_output = run_with_output(['sudo', 'docker', 'build', '-t', 'playwright-python-test', '/tmp/interpreter'])
    except subprocess.CalledProcessError as e:
        print(f"Docker build failed with error code {e.returncode}")
        print(f"Build error output: {e.output}")
        raise

    # Run Docker container with flags to ensure unbuffered output
    cmd = "sudo docker run -i --init --rm playwright-python-test python -u basic_test.py".split()
    
    try:
        return run_with_output(cmd)
    except subprocess.CalledProcessError as e:
        raise


def advanced_browser(task, api_key, api_base):
    # print("Starting advanced browser...")
    os.makedirs('/tmp/interpreter', exist_ok=True)
    # print("Creating Dockerfile...")
    create_dockerfile('/tmp/interpreter/Dockerfile', api_key, api_base)
    # print("Creating requirements.txt...")
    create_requirements_txt('/tmp/interpreter/requirements.txt')
    # print("Creating basic test script...")
    create_basic_test_script('/tmp/interpreter/basic_test.py', task)
    # print("Installing Docker...")
    install_docker()
    # print("Building and running Docker container...")
    return build_and_run_docker()  # Return the output from the Docker run