import os
import json
import logging
import subprocess
from datetime import datetime

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/git.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class GitManager:
    def __init__(self, config_path):
        """Initialize Git Manager with configuration."""
        self.config = self.load_config(config_path)
        self.base_dir = os.getcwd()
        self.init = os.path.exists(".git")  # Check if Git is initialized
        logging.info(f"Loaded configuration from {config_path}")

    def load_config(self, file_path):
        """Load configuration from JSON file."""
        with open(file_path, "r") as file:
            return json.load(file)

    def initialize_git(self):
        """Initialize Git repository if not already initialized."""
        if not self.init:
            subprocess.run(["git", "init"], check=True)
            logging.info("Initialized a new Git repository")
            self.init = True
        else:
            logging.info("Git repository already exists")

    def add_remote_url(self):
        """Add remote origin URL if not already added."""
        existing_remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout.strip()
        
        if not existing_remotes:
            if "remote_url" in self.config:
                subprocess.run(["git", "remote", "add", "origin", self.config["remote_url"]], check=True)
                logging.info(f"Added remote URL: {self.config['remote_url']}")
            else:
                logging.error("Remote URL not found in the configuration.")
        else:
            logging.info("Remote URL already exists.")

    def create_branch(self):
        """Create and switch to a new branch if not already on it."""
        branch_name = self.config.get("branch_name", "main")
        current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()

        if current_branch != branch_name:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            logging.info(f"Created and switched to branch {branch_name}")
        else:
            logging.info(f"Already on branch {branch_name}")

    def add_to_staging(self, file_pattern="."):
        """Stage files for commit, ensuring they exist."""
        if file_pattern != "." and not os.path.exists(file_pattern):
            logging.error(f"Cannot stage: '{file_pattern}' does not exist.")
            return
        
        subprocess.run(["git", "add", file_pattern], check=True)
        logging.info(f"Staged files matching pattern: {file_pattern}")

    def commit_and_push(self, message="Updated project", force = False):
        """Commit and push changes."""
        try:
            subprocess.run(["git", "commit", "-m", message], check=True)
            logging.info(f"Committed changes with message: {message}")

            branch_name = self.config.get("branch_name", "main")
            if not force:
                subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
            else:
                subprocess.run(["git", "push", "-f", "origin", branch_name], check = True)
                logging.info(f"Pushed changes to remote repository on branch {branch_name}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error in committing or pushing: {e}")

    def generate_report(self):
        """Generate a detailed Git report."""
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/git_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        with open(report_path, "w") as report:
            report.write("=" * 40 + "\n")
            report.write("              Git Report      \n")
            report.write(f"      Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}     \n")
            report.write("=" * 40 + "\n\n")

            last_commit = subprocess.run(["git", "log", "-1", "--pretty=format:%s"], capture_output=True, text=True).stdout
            last_commit_date = subprocess.run(["git", "log", "-1", "--pretty=format:%ci"], capture_output=True, text=True).stdout
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout

            changes_detected = "Uncommitted Changes Detected" if status else "Up to date"
            repo_name = self.config.get('remote_url', 'Unknown').split("/")[-1].replace(".git", "")

            report.write(f"Repository: {repo_name}\n")
            report.write(f"Branch: {self.config.get('branch_name', 'main')}\n")
            report.write(f"Last Commit: {last_commit if last_commit else '(No commits yet)'}\n")
            report.write(f"Last Commit Date: {last_commit_date if last_commit_date else 'N/A'}\n")
            report.write(f"Changes Pushed: {'No' if status else 'Yes'}\n")
            report.write(f"Status: {changes_detected}\n")

        logging.info(f"Git report saved at {report_path}")

if __name__ == "__main__":
    git_manager = GitManager(config_path = "config.json") 
    git_manager.initialize_git()
    git_manager.add_remote_url()
    git_manager.create_branch()

    git_manager.add_to_staging()

    git_manager.commit_and_push("Updated project", force = True)
    git_manager.generate_report()