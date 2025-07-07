#!/usr/bin/env python3
"""
AI Link Scraper Setup

Setup script for deploying the AI Link Scraper daemon in various modes.
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.absolute()

def check_requirements():
    """Check if requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} found")
    
    # Check if .env file exists
    env_file = get_project_root() / ".env"
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example and configure it.")
        return False
    
    print("✅ .env file found")
    
    # Check if virtual environment is recommended
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        print("⚠️  Virtual environment recommended but not detected")
    else:
        print("✅ Virtual environment detected")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, cwd=get_project_root())
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_configuration():
    """Test the Slack connection and configuration"""
    print("🧪 Testing configuration...")
    try:
        result = subprocess.run([sys.executable, "daemon.py", "--test"], 
                              capture_output=True, text=True, cwd=get_project_root())
        if result.returncode == 0:
            print("✅ Configuration test passed")
            return True
        else:
            print(f"❌ Configuration test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def setup_systemd(user=None):
    """Setup systemd service (Linux)"""
    print("🐧 Setting up systemd service...")
    
    if os.geteuid() == 0:
        print("❌ Don't run this as root. Use --user flag for user service.")
        return False
    
    # Get current user and project path
    current_user = os.getenv("USER")
    project_path = get_project_root()
    python_path = sys.executable
    
    # Read template and customize
    service_template = project_path / "systemd" / "ai-link-scraper-daemon.service"
    if not service_template.exists():
        print("❌ Systemd service template not found")
        return False
    
    # Create user systemd directory
    systemd_dir = Path.home() / ".config" / "systemd" / "user"
    systemd_dir.mkdir(parents=True, exist_ok=True)
    
    # Read and customize service file
    with open(service_template) as f:
        service_content = f.read()
    
    service_content = service_content.replace("your-username", current_user)
    service_content = service_content.replace("/path/to/ai-link-scraper", str(project_path))
    service_content = service_content.replace("/path/to/your/python/bin/python", python_path)
    service_content = service_content.replace("/path/to/your/python/bin", str(Path(python_path).parent))
    
    # Write service file
    service_file = systemd_dir / "ai-link-scraper-daemon.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    
    print(f"✅ Service file created: {service_file}")
    
    # Reload systemd and enable service
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "ai-link-scraper-daemon.service"], check=True)
        print("✅ Systemd service enabled")
        print("To start: systemctl --user start ai-link-scraper-daemon")
        print("To check status: systemctl --user status ai-link-scraper-daemon")
        print("To view logs: journalctl --user -u ai-link-scraper-daemon -f")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup systemd service: {e}")
        return False

def setup_launchd():
    """Setup launchd service (macOS)"""
    print("🍎 Setting up launchd service...")
    
    current_user = os.getenv("USER")
    project_path = get_project_root()
    python_path = sys.executable
    
    # Read template and customize
    plist_template = project_path / "launchd" / "com.user.ai-link-scraper-daemon.plist"
    if not plist_template.exists():
        print("❌ Launchd plist template not found")
        return False
    
    # Create LaunchAgents directory
    launchd_dir = Path.home() / "Library" / "LaunchAgents"
    launchd_dir.mkdir(parents=True, exist_ok=True)
    
    # Read and customize plist file
    with open(plist_template) as f:
        plist_content = f.read()
    
    plist_content = plist_content.replace("/usr/bin/python3", python_path)
    plist_content = plist_content.replace("/path/to/ai-link-scraper", str(project_path))
    
    # Write plist file
    plist_file = launchd_dir / "com.user.ai-link-scraper-daemon.plist"
    with open(plist_file, "w") as f:
        f.write(plist_content)
    
    print(f"✅ Plist file created: {plist_file}")
    
    # Load the service
    try:
        subprocess.run(["launchctl", "load", str(plist_file)], check=True)
        print("✅ Launchd service loaded")
        print("To start: launchctl start com.user.ai-link-scraper-daemon")
        print("To stop: launchctl stop com.user.ai-link-scraper-daemon")
        print("To unload: launchctl unload ~/Library/LaunchAgents/com.user.ai-link-scraper-daemon.plist")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup launchd service: {e}")
        return False

def setup_docker():
    """Setup Docker deployment"""
    print("🐳 Setting up Docker deployment...")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker first.")
        return False
    
    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ docker-compose not found. Please install docker-compose first.")
        return False
    
    project_path = get_project_root()
    
    print("Building Docker image...")
    try:
        subprocess.run(["docker-compose", "build"], check=True, cwd=project_path)
        print("✅ Docker image built successfully")
        print("To start daemon: docker-compose up -d")
        print("To view logs: docker-compose logs -f")
        print("To stop: docker-compose down")
        print("To run manual job: docker-compose run --rm ai-link-scraper-manual")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Docker image: {e}")
        return False

def manual_setup():
    """Setup for manual execution"""
    print("🖥️  Manual setup complete!")
    print("\nUsage examples:")
    print("  # Run daemon manually:")
    print("  python daemon.py --interval 60 --verbose")
    print("")
    print("  # Test daemon:")
    print("  python daemon.py --test")
    print("")
    print("  # Run one-time processing:")
    print("  python main.py --check-all-channels")
    print("")
    print("  # Run weekly summary:")
    print("  python main.py --create-weekly-document --send-to-slack")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="AI Link Scraper Setup")
    parser.add_argument(
        "--mode",
        choices=["systemd", "launchd", "docker", "manual"],
        help="Deployment mode"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--skip-test",
        action="store_true",
        help="Skip configuration test"
    )
    
    args = parser.parse_args()
    
    print("🚀 AI Link Scraper Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            return 1
    
    # Test configuration
    if not args.skip_test:
        if not test_configuration():
            print("⚠️  Configuration test failed. Please check your .env file.")
            return 1
    
    # Setup based on mode
    if args.mode == "systemd":
        if not setup_systemd():
            return 1
    elif args.mode == "launchd":
        if not setup_launchd():
            return 1
    elif args.mode == "docker":
        if not setup_docker():
            return 1
    elif args.mode == "manual":
        manual_setup()
    else:
        # Auto-detect platform
        if sys.platform.startswith("linux"):
            print("🐧 Linux detected - recommending systemd")
            if not setup_systemd():
                print("Falling back to manual setup...")
                manual_setup()
        elif sys.platform == "darwin":
            print("🍎 macOS detected - recommending launchd")
            if not setup_launchd():
                print("Falling back to manual setup...")
                manual_setup()
        else:
            print(f"Platform {sys.platform} detected - using manual setup")
            manual_setup()
    
    print("\n✅ Setup complete!")
    print("Check logs/ directory for daemon logs when running.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
