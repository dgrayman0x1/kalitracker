#! /usr/bin/env python3 
import os 

print("KaliTracker script started")

def get_user_input(): 

    print("[+] Welcome to KaliTracker")

    #Directory to monitor 
    default_dir = os.path.expanduser("~/")
    monitor_dir = input(f"Enter directory to monitor [{default_dir}]: ").strip()
    if monitor_dir == "":
        monitor_dir = default_dir
    monitor_dir = os.path.abspath(monitor_dir)

    # Log metadata?
    log_metadata = input("Log new files to changelog.json? [y/N]: ").strip().lower() == "y"

    # Copy new files to a tracked folder?
    copy_files = input("Copy new files to tracked_files/? [y/N]: ").strip().lower() == "y"

    # GitHub Repo URL
    github_repo = input("Enter your GitHub repo URL (leave blank to skip): ").strip()

    # Auto-push to GitHub?
    auto_push = False
    if github_repo:
        auto_push = input("Do you want to auto-commit & push to GitHub every run? [y/N]: ").strip().lower() == "y"
    print("\n[+] Configuration complete.\n")

    return {
        "monitor_dir": monitor_dir,
        "log_metadata": log_metadata,
        "copy_files": copy_files,
        "github_repo": github_repo,
        "auto_push": auto_push
    }