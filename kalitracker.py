import os
import subprocess
import json
import time
from datetime import datetime

SNAPSHOT_FILE = ".kalitracker_snapshot.json"

def get_user_input():
    print("[+] Welcome to KaliTracker Setup")

    # Prompt for directory and expand ~ to full home directory
    default_dir = os.path.expanduser("~/")
    monitor_dir = input(f"Enter directory to monitor [{default_dir}]: ").strip() or default_dir
    monitor_dir = os.path.abspath(os.path.expanduser(monitor_dir))

    log_metadata = input("Log new/deleted files to changelog? [y/N]: ").strip().lower() == "y"
    copy_files = input("Copy new files to tracked_files/? [y/N]: ").strip().lower() == "y"
    
    github_repo = ""
    auto_push = False

    if input("Do you want to link a GitHub repository? [y/N]: ").strip().lower() == "y":
        print("\n[!] GitHub now requires a Personal Access Token (PAT) for HTTPS Git operations.")
        print("    Example format: https://<PAT>@github.com/username/repo.git")
        print("    You can generate a PAT at: https://github.com/settings/tokens\n")

        while True:
            github_repo = input("Enter your GitHub repo URL (with PAT embedded): ").strip()
            if github_repo.startswith("https://") and "@github.com" in github_repo:
                break
            else:
                print("[!] Invalid format. Please include the PAT in the URL.")

        auto_push = input("Auto-commit & push to GitHub every run? [y/N]: ").strip().lower() == "y"

    return {
        "monitor_dir": monitor_dir,
        "log_metadata": log_metadata,
        "copy_files": copy_files,
        "github_repo": github_repo,
        "auto_push": auto_push
    }

def find_recent_files(directory):
    new_files = []
    deleted_files = []

    now = time.time()
    cutoff = now - 86400  # 24 hours ago

    current_files = set()

    for root, dirs, files in os.walk(directory, topdown=True, followlinks=False):
        for name in files:
            try:
                full_path = os.path.join(root, name)
                if os.path.islink(full_path):
                    continue

                mtime = os.path.getmtime(full_path)
                current_files.add(full_path)

                if mtime >= cutoff:
                    new_files.append((full_path, mtime))
                print(f"  [*] Found file: {full_path} | Modified: {mtime}")  # Debug print
            except Exception as e:
                print(f"  [!] Skipping {full_path}: {e}")
                continue

    # Reading the previous snapshot to detect deletions
    previous_files = set()
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, "r") as f:
                previous_files = set(json.load(f))
        except:
            pass

    deleted_files = list(previous_files - current_files)

    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(list(current_files), f)

    return new_files, deleted_files

def log_to_changelog(new_files, deleted_files):
    date_str = datetime.now().strftime("%Y-%m-%d")
    changelog_file = f"changelog-{date_str}.json"

    entries = []

    for path, mtime in new_files:
        entries.append({
            "event": "created",
            "path": path,
            "timestamp": datetime.fromtimestamp(mtime).isoformat()
        })

    for path in deleted_files:
        entries.append({
            "event": "deleted",
            "path": path,
            "timestamp": datetime.now().isoformat()
        })

    with open(changelog_file, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"[+] Logged {len(new_files)} new and {len(deleted_files)} deleted files to {changelog_file}")
    return changelog_file

def push_to_github(repo_url, files_to_commit):
    try:
        # Initialize Git if not already a repo
        if not os.path.isdir(".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

        # Set main branch if needed
        subprocess.run(["git", "branch", "-M", "main"], check=True)

        # Stage all relevant changes (adds, deletions)
        subprocess.run(["git", "add", "-A"], check=True)

        # Check if there's anything to commit
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("[*] No changes to commit.")
            return

        # Commit and push
        subprocess.run(["git", "commit", "-m", "KaliTracker update"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("[+] Pushed changes to GitHub.")

    except subprocess.CalledProcessError as e:
        print(f"[!] Git error: {e}")

def main():
    config = get_user_input()
    print("[*] Your Config:")
    for key, value in config.items():
        print(f"    {key}: {value}")

    new_files, deleted_files = find_recent_files(config["monitor_dir"])

    if config["log_metadata"]:
        changelog_file = log_to_changelog(new_files, deleted_files)
    else:
        changelog_file = None

    if config["auto_push"] and changelog_file:
        push_to_github(config["github_repo"], [changelog_file])

if __name__ == "__main__":
    main()
