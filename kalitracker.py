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

def find_new_files(directory, known_files):
    new_files = []
    for root, dirs, files in os.walk(directory, topdown=True, followlinks=False):
        # Optionally skip system directories to reduce noise (optional)
        # dirs[:] = [d for d in dirs if not d.startswith("proc")]

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


# Entry point
if __name__ == "__main__":
    config = get_user_input()
    print("[*] Your Config:")
    for key, value in config.items():
        print(f"    {key}: {value}")
