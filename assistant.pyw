import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Install packages from requirements.txt if they are missing
requirements_file = "requirements.txt"
if os.path.exists(requirements_file):
    with open(requirements_file) as f:
        required_packages = f.read().splitlines()

    for package in required_packages:
        try:
            __import__(package.split('==')[0])  # Import package (handles version specifiers)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from management import ChatApplication

if __name__ == "__main__":
    app = ChatApplication()
    app.run()