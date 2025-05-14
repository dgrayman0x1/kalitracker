import os
import subprocess
import json
from datetime import datetime

CHANGELOG_FILE = "changelog.json"

def get_user_input():
    print("[+] Welcome to KaliTracker Setup")

    # Prompt for directory and expand ~ to full home directory
    default_dir = os.path.expanduser("~/")
    monitor_dir = input(f"Enter directory to monitor [{default_dir}]: ").strip() or default_dir
    monitor_dir = os.path.abspath(os.path.expanduser(monitor_dir))  # Ensure ~ is expanded to full path

    log_metadata = input("Log new files to changelog.json? [y/N]: ").strip().lower() == "y"
    copy_files = input("Copy new files to tracked_files/? [y/N]: ").strip().lower() == "y"
    github_repo = input("Enter your GitHub repo URL (leave blank to skip): ").strip()
    auto_push = github_repo and input("Auto-commit & push to GitHub every run? [y/N]: ").strip().lower() == "y"

    # If GitHub repo is provided, ask for GitHub credentials
    if github_repo:
        github_user_name = input("Enter your GitHub username: ").strip()
        github_user_email = input("Enter your GitHub email: ").strip()

        # Set up Git config for the user
        try:
            subprocess.run(['git', 'config', '--global', 'user.name', github_user_name], check=True)
            subprocess.run(['git', 'config', '--global', 'user.email', github_user_email], check=True)
            print(f"Git configured with name: {github_user_name} and email: {github_user_email}")
        except subprocess.CalledProcessError:
            print("[!] Error setting up Git configuration. Please check your Git setup.")

    return {
        "monitor_dir": monitor_dir,
        "log_metadata": log_metadata,
        "copy_files": copy_files,
        "github_repo": github_repo,
        "auto_push": auto_push
    }

def log_to_changelog(new_files):
    entries = []
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "r") as f:
            try:
                entries = json.load(f)
            except json.JSONDecodeError:
                pass  # Invalid JSON or empty file

    for path, mtime in new_files:
        entries.append({
            "path": path,
            "timestamp": datetime.fromtimestamp(mtime).isoformat()
        })

    with open(CHANGELOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"[+] Logged {len(new_files)} new files to {CHANGELOG_FILE}")

def push_to_github(repo_url, files_to_commit):
    try:
        # Ensure we're in a git repo
        if not os.path.isdir(".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

        # Stage files
        subprocess.run(["git", "add"] + files_to_commit, check=True)

        # Commit
        subprocess.run(["git", "commit", "-m", "KaliTracker update"], check=True)

        # Set default branch if needed
        subprocess.run(["git", "branch", "-M", "main"], check=True)

        # Push
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("[+] Pushed changes to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Git error: {e}")

def find_new_files(directory, known_files):
    new_files = []
    for root, dirs, files in os.walk(directory, topdown=True, followlinks=False):
        for name in files:
            try:
                full_path = os.path.join(root, name)

                # Skip if it's a symlink
                if os.path.islink(full_path):
                    continue

                mtime = os.path.getmtime(full_path)
                if full_path not in known_files:
                    new_files.append((full_path, mtime))
            except Exception as e:
                # Print or log errors, but don’t crash the script
                print(f"  [!] Skipping {full_path}: {e}")
                continue
    return new_files

def main():
    config = get_user_input()
    print("[*] Your Config:")
    for key, value in config.items():
        print(f"    {key}: {value}")

    # Simulate known files (can be modified as needed)
    known_files = set()

    # Find new files
    new_files = find_new_files(config["monitor_dir"], known_files)

    if config["log_metadata"]:
        log_to_changelog(new_files)

    if config["auto_push"]:
        push_to_github(config["github_repo"], [CHANGELOG_FILE])

# Entry point
if __name__ == "__main__":
    main()
