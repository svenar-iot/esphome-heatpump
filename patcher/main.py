import yaml
import os
import subprocess
import shutil
import re

def run_command(command, cwd=None):
    print(f"Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        exit(1)

def execute_task_item(item):
    # Match the pattern [command] arguments
    match = re.match(r'\[(.*?)\]\s*(.*)', item)
    if not match:
        print(f"Invalid task format: {item}")
        return

    cmd_type = match.group(1).strip().lower()
    args_str = match.group(2).strip()
    
    if cmd_type == 'rmdir':
        path = args_str
        print(f"Removing directory: {path}")
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        else:
            print(f"Path {path} does not exist, skipping.")
            
    elif cmd_type == 'mkdir':
        path = args_str
        print(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=True)
        
    elif cmd_type == 'clone':
        parts = args_str.split(' ')
        if len(parts) >= 2:
            repo_url = parts[0]
            dest_dir = parts[1]
            print(f"Cloning {repo_url} into {dest_dir}")
            run_command(f"git clone {repo_url} {dest_dir}")
        else:
            print(f"Invalid clone arguments: {args_str}")

    elif cmd_type == 'patch':
        parts = args_str.split(' ')
        if len(parts) >= 2:
            target_file = parts[0]
            patch_file = parts[1]
            print(f"Applying patch {patch_file} to {target_file}")
            run_command(f"patch {target_file} < {patch_file}")
        else:
            print(f"Invalid patch arguments: {args_str}")

    elif cmd_type == 'rename':
        parts = args_str.split(' ')
        if len(parts) >= 2:
            old_name = parts[0]
            new_name = parts[1]
            print(f"Renaming {old_name} to {new_name}")
            new_name_dir = os.path.dirname(new_name)
            if new_name_dir and not os.path.exists(new_name_dir):
                os.makedirs(new_name_dir, exist_ok=True)
            shutil.move(old_name, new_name)
        else:
            print(f"Invalid rename arguments: {args_str}")
    
    elif cmd_type == 'copy':
        parts = args_str.split(' ')
        if len(parts) >= 2:
            src = parts[0]
            dst = parts[1]
            print(f"Copying {src} to {dst}")
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            shutil.copy(src, dst)
        else:
            print(f"Invalid copy arguments: {args_str}")
    
    else:
        print(f"Unknown command type: {cmd_type}")

def main():
    config_path = 'config.yaml'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    task_order = config.get('tasks', [])

    for task_name in task_order:
        print(f"\n--- Running Task: {task_name} ---")
        task_items = config.get(task_name, [])
        if isinstance(task_items, list):
            for item in task_items:
                execute_task_item(item)
        else:
            print(f"Warning: Task '{task_name}' is not a list in the config.")

if __name__ == '__main__':
    main()