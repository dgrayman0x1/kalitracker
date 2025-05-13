#!/usr/bin/env python3

import os

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

    return {
        "monitor_dir": monitor_dir,
        "log_metadata": log_metadata,
        "copy_files": copy_files,
        "github_repo": github_repo,
        "auto_push": auto_push
    }

# Entry point
if __name__ == "__main__":
    config = get_user_input()
    print("[*] Your Config:")
    for key, value in config.items():
        print(f"    {key}: {value}")
