#!/usr/bin/env python3
"""
Automated release script for pypubmech.
Run this script to test, build, and release the package.
./release.py --version 0.1.0 --github-username your-username

"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil
import venv
import time

class ReleaseManager:
    def __init__(self, version: str, github_username: str, repo_name: str):
        self.version = version
        self.github_username = github_username
        self.repo_name = repo_name
        self.venv_path = Path("venv")
        self.python_exe = self.venv_path / "bin" / "python"
        if os.name == "nt":  # Windows
            self.python_exe = self.venv_path / "Scripts" / "python.exe"

    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        print(f"\n=== Running: {command} ===")
        result = subprocess.run(command, shell=True, check=check, text=True)
        print(f"=== Command completed with return code: {result.returncode} ===\n")
        return result

    def setup_virtual_environment(self):
        """Create and activate a virtual environment."""
        print("Setting up virtual environment...")
        if self.venv_path.exists():
            shutil.rmtree(self.venv_path)
        venv.create(self.venv_path, with_pip=True)

    def install_dependencies(self):
        """Install all necessary dependencies."""
        print("Installing dependencies...")
        self.run_command(f'"{self.python_exe}" -m pip install --upgrade pip')
        self.run_command(f'"{self.python_exe}" -m pip install build pytest twine wheel')
        self.run_command(f'"{self.python_exe}" -m pip install -e ".[dev]"')

    def run_tests(self):
        """Run the test suite."""
        print("Running tests...")
        self.run_command(f'"{self.python_exe}" -m pytest tests/')

    def build_package(self):
        """Build the package."""
        print("Building package...")
        self.run_command(f'"{self.python_exe}" -m build')

    def git_setup_and_push(self):
        """Initialize git repository and push to GitHub."""
        print("Setting up git repository...")
        commands = [
            "git init",
            "git add .",
            f'git commit -m "Release version {self.version}"',
            f"git remote add origin https://github.com/{self.github_username}/{self.repo_name}.git",
            "git branch -M main",
            "git push -u origin main",
            f'git tag -a v{self.version} -m "Release version {self.version}"',
            f"git push origin v{self.version}"
        ]
        
        for command in commands:
            try:
                self.run_command(command)
                time.sleep(1)  # Small delay between git commands
            except subprocess.CalledProcessError as e:
                print(f"Error during git operations: {e}")
                choice = input("Continue anyway? (y/n): ")
                if choice.lower() != 'y':
                    sys.exit(1)

    def update_version_in_files(self):
        """Update version number in necessary files."""
        print("Updating version numbers...")
        # Update __init__.py
        init_file = Path("pypubmech/__init__.py")
        content = init_file.read_text()
        new_content = content.replace(
            '__version__ = "0.1.0"',
            f'__version__ = "{self.version}"'
        )
        init_file.write_text(new_content)

    def clean_previous_builds(self):
        """Remove previous build artifacts."""
        print("Cleaning previous builds...")
        for path in ["dist", "build", "*.egg-info"]:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass

    def release(self):
        """Execute the full release process."""
        try:
            self.clean_previous_builds()
            self.setup_virtual_environment()
            self.install_dependencies()
            self.update_version_in_files()
            self.run_tests()
            self.build_package()
            self.git_setup_and_push()
            
            print("\nRelease process completed successfully!")
            print("\nNext steps:")
            print("1. Go to GitHub repository:")
            print(f"   https://github.com/{self.github_username}/{self.repo_name}")
            print("2. Go to the 'Releases' section")
            print("3. Click 'Create a new release'")
            print(f"4. Select the tag 'v{self.version}'")
            print("5. Add release notes")
            print("6. Publish the release")
            
        except Exception as e:
            print(f"Error during release process: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Release automation for pypubmech")
    parser.add_argument("--version", required=True, help="Version number for the release")
    parser.add_argument("--github-username", required=True, help="Your GitHub username")
    parser.add_argument("--repo-name", default="pypubmech", help="Repository name")
    
    args = parser.parse_args()
    
    manager = ReleaseManager(args.version, args.github_username, args.repo_name)
    manager.release()

if __name__ == "__main__":
    main()