#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
import logging
import shutil
import importlib.metadata
import re
import shlex
import tempfile

# Get version using importlib.metadata
try:
    __version__ = importlib.metadata.version('fitrepo')
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.53"

# Set up logging for user feedback
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Default constants
FOSSIL_REPO = 'fitrepo.fossil'
CONFIG_FILE = 'fitrepo.json'
GIT_CLONES_DIR = '.fitrepo/git_clones'
MARKS_DIR = '.fitrepo/marks'

# Helper functions for common operations
def run_command(cmd, check=True, capture_output=False, text=False, fossil_args=None, apply_args=True):
    """Run a command and return its result, with unified error handling."""
    try:
        # Add fossil args if applicable
        if fossil_args and cmd[0] == 'fossil' and apply_args and len(cmd) > 1:
            # Insert args after fossil command and subcommand
            cmd = [cmd[0], cmd[1]] + fossil_args + cmd[2:]
            
        logger.debug(f"Running: {' '.join(cmd)}")
        return subprocess.run(cmd, check=check, capture_output=capture_output, text=text)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            logger.error(f"Error output: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error(f"Command not found: {cmd[0]}")
        raise

def ensure_directories(*dirs):
    """Ensure required directories exist."""
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True, parents=True)

def check_dependencies():
    """Check if all required dependencies are installed."""
    dependencies = [
        (['git', '--version'], "Git"),
        (['fossil', 'version'], "Fossil"),
        (['git-filter-repo', '--version'], "git-filter-repo")
    ]
    
    for cmd, name in dependencies:
        try:
            run_command(cmd, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error(f"{name} is not installed or not working properly.")
            if name == "git-filter-repo":
                logger.error("Install it with: pip install git-filter-repo")
            return False
    return True

@contextmanager
def cd(path):
    """Context manager to change directory and return to original directory."""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)

# Configuration handling
def load_config(config_file=CONFIG_FILE):
    """Load the configuration file, returning an empty dict if it doesn't exist."""
    return json.load(open(config_file, 'r')) if Path(config_file).exists() else {}

def save_config(config, config_file=CONFIG_FILE):
    """Save the configuration to the config file."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def is_fossil_repo_open():
    """Check if we are already in a Fossil checkout."""
    try:
        return run_command(['fossil', 'status'], check=False).returncode == 0
    except:
        return False

def get_workspace_file():
    """Find the .code-workspace file in the .vscode directory, if it exists."""
    vscode_dir = Path('.vscode')
    if not vscode_dir.exists():
        return None
    
    workspace_files = list(vscode_dir.glob('*.code-workspace'))
    if not workspace_files:
        return None
    
    # Return the first workspace file found (normally there should be only one)
    return workspace_files[0]

def add_to_workspace(subdir_path, no_vscode=False):
    """Add a subdirectory to the VSCode workspace file."""
    if no_vscode:
        return False
    
    # Find workspace file
    workspace_file = get_workspace_file()
    if not workspace_file:
        return False
    
    # Load workspace configuration
    try:
        with open(workspace_file, 'r') as f:
            workspace_config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logger.warning(f"Could not read workspace file: {workspace_file}")
        return False
    
    # Ensure the folders section exists
    workspace_config.setdefault('folders', [])
    
    # Create the new folder entry
    norm_path = normalize_path(subdir_path)
    new_folder = {"path": norm_path}
    
    # Check if folder is already in workspace
    for folder in workspace_config['folders']:
        if folder.get('path') == norm_path:
            logger.debug(f"Folder {norm_path} already exists in workspace")
            return True
    
    # Add the new folder to workspace
    workspace_config['folders'].append(new_folder)
    
    # Save updated workspace file
    try:
        with open(workspace_file, 'w') as f:
            json.dump(workspace_config, f, indent=4)
        logger.info(f"Added {norm_path} to workspace file: {workspace_file}")
        return True
    except Exception as e:
        logger.warning(f"Failed to update workspace file: {e}")
        return False

def create_vscode_settings():
    """Create .vscode/<name>.code-workspace file with settings for fitrepo."""
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    # Get project name from config or use directory name
    try:
        config = load_config()
        project_name = config.get('name', Path.cwd().name)
    except:
        project_name = Path.cwd().name
    
    # Create workspace file with project name
    workspace_file = vscode_dir / f"{project_name}.code-workspace"
    
    workspace_config = {
        "folders": [],
        "settings": {
            "git.ignoredRepositories": [
                ".fitrepo/git_clones/**"
            ],
            "files.exclude": {
                ".fitrepo": True,
                ".fitrepo/**": True
            },
            "search.exclude": {
                ".fitrepo/**": True
            }
        }
    }
    
    # Write settings to file with appropriate formatting
    with open(workspace_file, 'w') as f:
        json.dump(workspace_config, f, indent=4)
    
    logger.info(f"Created VSCode workspace file: {workspace_file}")

def init_fossil_repo(fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_open_args=None, fossil_init_args=None, no_vscode=False):
    """Initialize the Fossil repository and configuration file."""
    try:
        repo_path = Path(fossil_repo)
        
        # Create and/or open repository as needed
        if not repo_path.exists():
            logger.info(f"Creating Fossil repository {fossil_repo}...")
            run_command(['fossil', 'init', fossil_repo], fossil_args=fossil_init_args)
            need_open = True
        else:
            need_open = not is_fossil_repo_open()
            
        if need_open:
            logger.info(f"Opening Fossil repository {fossil_repo}...")
            run_command(['fossil', 'open', fossil_repo], fossil_args=fossil_open_args)
        else:
            logger.info(f"Fossil repository is already open.")
            
        if not Path(config_file).exists():
            logger.info(f"Creating configuration file {config_file}...")
            # Use directory name as project name
            save_config({'name': Path.cwd().name, 'repositories': {}}, config_file)
        
        # Create VSCode settings file unless no_vscode flag is set
        if not no_vscode:
            create_vscode_settings()
            
        logger.info("Initialization complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during initialization: {e}")
        raise

# Path handling functions
def normalize_path(path_str):
    """Normalize a path for use as a subdirectory."""
    return str(Path(path_str)).replace('\\', '/').strip('/')

def path_to_branch_prefix(path_str):
    """Convert a normalized path to a branch prefix suitable for fossil."""
    return normalize_path(path_str).replace('/', '__')

def branch_prefix_to_path(prefix):
    """Convert a branch prefix back to its path representation."""
    return prefix.replace('__', '/')

# Validation functions
def validate_git_url(url):
    """Validate Git repository URL or path."""
    if not url:
        logger.error("Git URL or path cannot be empty")
        return False
    
    # Accept URLs or existing paths
    if url.startswith(('http', 'git', 'ssh')):
        return True
    
    path = Path(url)
    if path.exists():
        if (path / '.git').exists():
            return True
        logger.warning(f"Path exists but may not be a Git repository: {url}")
        return True
        
    logger.error(f"Path does not exist: {url}")
    return False

def validate_subdir_name(name):
    """Validate subdirectory path."""
    if not name:
        logger.error("Subdirectory name cannot be empty")
        return False
        
    if name.startswith('/') or name.endswith('/'):
        logger.error(f"Invalid subdirectory path: {name}. Must not start or end with '/'")
        return False
        
    if any(part.startswith('.') for part in name.split('/')):
        logger.error(f"Invalid subdirectory path: {name}. Path components must not start with '.'")
        return False
        
    if re.search(r'[<>:"|?*\x00-\x1F]', name):
        logger.error(f"Invalid characters in subdirectory path: {name}")
        return False
        
    return True

# Git operations
def process_git_repo(git_clone_path, subdir_path, force=False):
    """Apply subdirectory filter and rename branches with prefix."""
    norm_subdir = normalize_path(subdir_path)
    branch_prefix = path_to_branch_prefix(norm_subdir)
    
    # Apply git-filter-repo to move files to a subdirectory
    logger.info(f"Moving files to subdirectory '{norm_subdir}'...")
    filter_cmd = ['git-filter-repo', '--to-subdirectory-filter', norm_subdir]
    if force:
        filter_cmd.append('--force')
    run_command(filter_cmd)
    
    # Rename branches with subdirectory prefix
    logger.info(f"Renaming branches with prefix '{branch_prefix}/'...")
    result = run_command(['git', 'branch'], capture_output=True, text=True)
    branches = [b.strip().lstrip('* ') for b in result.stdout.splitlines() if b.strip()]
    
    # Rename each branch that doesn't already have the prefix
    for branch in branches:
        if branch and not branch.startswith(f"{branch_prefix}/"):
            try:
                # Check if target branch already exists
                if run_command(['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch_prefix}/{branch}'], check=False).returncode == 0:
                    logger.info(f"Branch '{branch_prefix}/{branch}' already exists, skipping rename")
                    # Since we can't have two branches with the same name, delete the current one
                    # The existing prefixed one already has all our changes
                    run_command(['git', 'branch', '-D', branch])
                else:
                    # Safe to rename
                    run_command(['git', 'branch', '-m', branch, f"{branch_prefix}/{branch}"])
            except subprocess.CalledProcessError:
                logger.warning(f"Failed to rename branch '{branch}'")

def export_import_git_to_fossil(subdir_path, git_marks_file, fossil_marks_file, fossil_repo, import_marks=False):
    """Export from Git and import into Fossil with appropriate marks files."""
    logger.info(f"{'Updating' if import_marks else 'Exporting'} Git history to Fossil...")
    
    # Build git command with marks files
    git_cmd = ['git', 'fast-export', '--all']
    if import_marks and Path(git_marks_file).exists():
        git_cmd.extend(['--import-marks', str(git_marks_file)])
    git_cmd.extend(['--export-marks', str(git_marks_file)])
    
    # Build fossil command with marks files
    fossil_cmd = ['fossil', 'import', '--git', '--incremental']
    if import_marks and Path(fossil_marks_file).exists():
        fossil_cmd.extend(['--import-marks', str(fossil_marks_file)])
    fossil_cmd.extend(['--export-marks', str(fossil_marks_file), str(fossil_repo)])
    
    # Execute the pipeline
    git_export = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    fossil_import = subprocess.Popen(fossil_cmd, stdin=git_export.stdout)
    git_export.stdout.close()
    fossil_import.communicate()
    
    if fossil_import.returncode != 0:
        raise subprocess.CalledProcessError(fossil_import.returncode, 'fossil import')

def update_fossil_checkout(subdir_path):
    """Update the fossil checkout to a branch with the given subdirectory prefix."""
    branch_prefix = path_to_branch_prefix(normalize_path(subdir_path))
    
    result = run_command(['fossil', 'branch', 'list'], capture_output=True, text=True)
    
    # Find first branch with the expected prefix and update to it
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith(f"{branch_prefix}/"):
            logger.info(f"Updating checkout to branch '{line}'...")
            run_command(['fossil', 'update', line])
            return
            
    logger.warning(f"No branches starting with '{branch_prefix}/' were found. Your checkout was not updated.")

# Common setup for repository operations
def setup_repo_operation(subdir_path=None, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_args=None):
    """Common setup for repository operations."""
    config = load_config(config_file)
    
    # Ensure config has repositories section
    config.setdefault('repositories', {})
    
    # Check if subdir exists in config if provided
    if subdir_path:
        norm_path = normalize_path(subdir_path)
        if norm_path not in config.get('repositories', {}):
            msg = f"Subdirectory '{norm_path}' not found in configuration."
            logger.error(msg)
            raise ValueError(msg)
        
    # Ensure fossil repository is open
    if not is_fossil_repo_open():
        logger.info(f"Opening Fossil repository {fossil_repo}...")
        run_command(['fossil', 'open', fossil_repo], fossil_args=fossil_args)
    else:
        logger.info(f"Using already open Fossil repository.")
        
    return config

# Repository operations
def setup_git_worktree(git_clone_path, target_dir, norm_path):
    """Setup a proper Git worktree for the imported subdirectory."""
    # Create the target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Get absolute paths to avoid path resolution issues
    git_clone_path_abs = os.path.abspath(git_clone_path)
    target_dir_abs = os.path.abspath(target_dir)
    git_dir_abs = os.path.join(git_clone_path_abs, '.git')
    
    # Create a .git file in the target directory that points to the actual Git repo
    git_link_path = os.path.join(target_dir_abs, '.git')
    with open(git_link_path, 'w') as f:
        # Use absolute path to avoid any resolution issues
        f.write(f"gitdir: {git_dir_abs}")
    
    # Configure Git to treat this directory as a working tree
    with cd(git_clone_path):
        # Set the core.worktree to the absolute target directory path
        run_command(['git', 'config', 'core.worktree', target_dir_abs])
        
        # Set up sparse checkout to limit visibility to only this directory
        run_command(['git', 'config', 'core.sparseCheckout', 'true'])
        
        # Hide untracked files in status output - this prevents Git internals from showing
        run_command(['git', 'config', 'status.showUntrackedFiles', 'no'])
        
        # Create sparse-checkout file
        sparse_checkout_dir = os.path.join(git_dir_abs, 'info')
        os.makedirs(sparse_checkout_dir, exist_ok=True)
        
        # Write the sparse checkout configuration - explicitly include dotfiles
        with open(os.path.join(sparse_checkout_dir, 'sparse-checkout'), 'w') as f:
            # Include all files at root of target dir, including dotfiles
            f.write("/*\n")
            f.write("/.*\n")  # Explicitly include dotfiles
            # Exclude other directories at the same level
            f.write("!/*/\n")
            # Also include original path pattern for compatibility
            f.write(f"{norm_path}/*\n")
            f.write(f"{norm_path}/.*\n")  # Include dotfiles in the target path
        
        # Reset the index to match HEAD
        run_command(['git', 'reset', '--mixed'], check=False)
        
        # Fix index if needed with a forced checkout
        run_command(['git', 'checkout', '-f', '--', '.'], check=False)
        
        # Force index update to recognize all files
        run_command(['git', 'add', '-A', '.'], check=False)
        run_command(['git', 'reset', '--mixed'], check=False)

    # Also configure the status setting in the target directory itself
    with cd(target_dir_abs):
        run_command(['git', 'config', '--local', 'status.showUntrackedFiles', 'no'], check=False)
        # Refresh working tree with a forced checkout
        run_command(['git', 'checkout', '-f', '--', '.'], check=False)
        
        # Ensure .gitignore is tracked if it exists
        gitignore_path = os.path.join(target_dir_abs, '.gitignore')
        if os.path.exists(gitignore_path):
            logger.info("Adding .gitignore to Git tracking...")
            run_command(['git', 'add', '.gitignore'], check=False)
            run_command(['git', 'commit', '-m', 'Track .gitignore file'], check=False)

def post_worktree_setup(git_clone_path, target_dir):
    """Additional setup to ensure the worktree is properly maintained."""
    # Create a post-checkout hook to ensure Git status works properly in the subdirectory
    hook_dir = os.path.join(git_clone_path, '.git', 'hooks')
    os.makedirs(hook_dir, exist_ok=True)
    post_checkout_hook = os.path.join(hook_dir, 'post-checkout')
    with open(post_checkout_hook, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('# Auto-generated by fitrepo\n')
        f.write('git config --local status.showUntrackedFiles no\n')
    # Make hook executable
    os.chmod(post_checkout_hook, 0o755)

def import_git_repo(git_repo_url, subdir_path, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, 
                    git_clones_dir=GIT_CLONES_DIR, marks_dir=MARKS_DIR, fossil_args=None, no_vscode=False):
    """Import a Git repository into the Fossil repository under a subdirectory."""
    if not validate_git_url(git_repo_url) or not validate_subdir_name(subdir_path):
        raise ValueError("Invalid input parameters")
    
    # Normalize the subdirectory path
    norm_path = normalize_path(subdir_path)
    config = setup_repo_operation(fossil_repo=fossil_repo, config_file=config_file, fossil_args=fossil_args)
    if norm_path in config.get('repositories', {}):
        msg = f"Subdirectory '{norm_path}' is already imported."
        logger.error(msg)
        raise ValueError(msg)
    
    # Use sanitized subdirectory name for file/directory names
    sanitized_name = norm_path.replace('/', '_')
    original_cwd = Path.cwd()
    git_clone_path = original_cwd / git_clones_dir / sanitized_name
    git_marks_file = original_cwd / marks_dir / f"{sanitized_name}_git.marks"
    fossil_marks_file = original_cwd / marks_dir / f"{sanitized_name}_fossil.marks"
    target_dir = original_cwd / norm_path
    
    # Clean existing clone directory if needed
    if git_clone_path.exists():
        logger.warning(f"Clone directory '{git_clone_path}' already exists. Removing it...")
        shutil.rmtree(git_clone_path)
    git_clone_path.mkdir(exist_ok=True, parents=True)
    
    try:
        # Clone the Git repository
        logger.info(f"Cloning Git repository from {git_repo_url}...")
        run_command(['git', 'clone', '--no-local', git_repo_url, str(git_clone_path)])
        
        with cd(git_clone_path):
            # Process Git repo and import into Fossil
            process_git_repo(git_clone_path, norm_path)
            export_import_git_to_fossil(norm_path, git_marks_file, fossil_marks_file, original_cwd / fossil_repo)
        
        # Set up Git worktree after Fossil import to properly link the directory
        setup_git_worktree(git_clone_path, target_dir, norm_path)
        post_worktree_setup(git_clone_path, target_dir)
        
        # Explicitly handle .gitignore if present
        gitignore_path = os.path.join(target_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            with cd(target_dir):
                logger.info("Ensuring .gitignore is tracked...")
                run_command(['git', 'add', '.gitignore'], check=False)
                run_command(['git', 'commit', '-m', 'Track .gitignore file'], check=False)
        
        # Update configuration
        config['repositories'][norm_path] = {
            'git_repo_url': git_repo_url,
            'git_clone_path': str(git_clone_path),
            'git_marks_file': str(git_marks_file),
            'fossil_marks_file': str(fossil_marks_file),
            'target_dir': str(target_dir)
        }
        save_config(config, config_file)
        
        # Update checkout and report success
        update_fossil_checkout(norm_path)
        
        # Add to VSCode workspace if applicable
        add_to_workspace(norm_path, no_vscode)
        
        logger.info(f"Successfully imported '{git_repo_url}' into subdirectory '{norm_path}'.")
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        raise

def update_git_repo(subdir_path, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_args=None):
    """Update the Fossil repository with new changes from a Git repository."""
    norm_path = normalize_path(subdir_path)
    config = setup_repo_operation(norm_path, fossil_repo, config_file, fossil_args=fossil_args)
    try:
        repo_details = config['repositories'][norm_path]
        git_clone_path = Path(repo_details['git_clone_path'])
        git_marks_file = Path(repo_details['git_marks_file'])
        fossil_marks_file = Path(repo_details['fossil_marks_file'])
        git_repo_url = repo_details['git_repo_url']
        original_cwd = Path.cwd()
        target_dir = original_cwd / norm_path if 'target_dir' not in repo_details else Path(repo_details['target_dir'])
        
        # Clean the existing clone and create a fresh one to avoid git-filter-repo issues
        logger.info(f"Re-cloning Git repository for '{norm_path}'...")
        if git_clone_path.exists():
            shutil.rmtree(git_clone_path)
        git_clone_path.mkdir(exist_ok=True, parents=True)
        
        # Clone the Git repository
        run_command(['git', 'clone', '--no-local', git_repo_url, str(git_clone_path)])
        
        with cd(git_clone_path):
            # Process Git repo and update Fossil
            process_git_repo(git_clone_path, norm_path, force=True)
            export_import_git_to_fossil(norm_path, git_marks_file, fossil_marks_file, 
                                      original_cwd / fossil_repo, import_marks=True)
        
        # Re-setup the Git worktree to maintain proper isolation
        setup_git_worktree(git_clone_path, target_dir, norm_path)
        post_worktree_setup(git_clone_path, target_dir)
        
        # Update config with target_dir if not present
        if 'target_dir' not in repo_details:
            repo_details['target_dir'] = str(target_dir)
            save_config(config, config_file)
            
        logger.info(f"Successfully updated '{norm_path}' in the Fossil repository.")
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        raise

def push_to_git(subdir_path, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_args=None, message=None):
    """Push Fossil changes to the original Git repository using bidirectional synchronization."""
    norm_path = normalize_path(subdir_path)
    config = setup_repo_operation(norm_path, fossil_repo, config_file, fossil_args=fossil_args)
    
    try:
        repo_details = config['repositories'][norm_path]
        git_repo_url = repo_details['git_repo_url']
        git_clone_path = Path(repo_details['git_clone_path'])
        git_marks_file = Path(repo_details['git_marks_file'])
        fossil_marks_file = Path(repo_details['fossil_marks_file'])
        original_cwd = Path.cwd()
        abs_fossil_repo = original_cwd / fossil_repo
        
        # Get the current branch *before* we open in a temp directory
        # This ensures we know which branch we need to use
        branch_prefix = path_to_branch_prefix(norm_path)
        all_branches_output = run_command(['fossil', 'branch', 'list'], capture_output=True, text=True).stdout
        target_branch = None
        
        # Find branch that matches our prefix
        for line in all_branches_output.splitlines():
            branch_name = line.strip().lstrip('*').strip()
            if branch_name.startswith(f"{branch_prefix}/"):
                target_branch = branch_name
                logger.info(f"Found target branch: {target_branch}")
                break
        
        if not target_branch:
            # Try a more flexible approach - look for branch names that might match
            logger.warning(f"No branch with exact prefix '{branch_prefix}/' found. Looking for alternatives...")
            
            # Get all branches and look for best match
            for line in all_branches_output.splitlines():
                branch_name = line.strip().lstrip('*').strip()
                path_parts = norm_path.split('/')
                if all(part in branch_name.lower().replace('__', '_') for part in path_parts):
                    target_branch = branch_name
                    logger.info(f"Found alternative branch: {target_branch}")
                    break
        
        if not target_branch:
            raise ValueError(f"Could not find any branch related to '{norm_path}'. Available branches: {all_branches_output}")
        
        # More aggressive clean and re-clone approach
        logger.info(f"Recreating Git clone for '{norm_path}'...")
        if git_clone_path.exists():
            shutil.rmtree(git_clone_path)
        git_clone_path.mkdir(exist_ok=True, parents=True)
        run_command(['git', 'clone', git_repo_url, str(git_clone_path)])
        
        # Set Git config to ignore parent directories
        with cd(git_clone_path):
            # Configure Git to only track files in this directory
            run_command(['git', 'config', 'core.worktree', '.'])
            os.makedirs(os.path.join(git_clone_path, '.git', 'info'), exist_ok=True)
            with open(os.path.join(git_clone_path, '.git', 'info', 'exclude'), 'a') as f:
                f.write("\n# Ignore parent directories\n../\n")
        
        # Export from Fossil to Git - CRITICAL: run the export in a controlled environment
        logger.info(f"Exporting Fossil changes to Git...")
        export_cmd = ['fossil', 'export', '--git']
        if Path(fossil_marks_file).exists():
            export_cmd.extend([f'--import-marks={fossil_marks_file}'])
        export_cmd.extend([f'--export-marks={fossil_marks_file}'])
        
        # Build Git fast-import command with marks
        import_cmd = ['git', 'fast-import', '--force']
        if Path(git_marks_file).exists():
            import_cmd.extend([f'--import-marks={git_marks_file}'])
        import_cmd.extend([f'--export-marks={git_marks_file}'])
        
        # CRITICAL FIX: We need to isolate the export to the specific subdirectory
        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Extract just the specific subfolder to this temp directory
            run_command(['fossil', 'open', str(abs_fossil_repo), '--workdir', str(temp_path)])
            with cd(temp_path):
                logger.info(f"Updating to branch: {target_branch}")
                run_command(['fossil', 'update', target_branch])
                
                # Now export from this controlled environment
                with cd(git_clone_path):  # Make sure we're in the git repo when running git fast-import
                    fossil_export = subprocess.Popen(export_cmd, stdout=subprocess.PIPE)
                    git_import = subprocess.Popen(import_cmd, stdin=fossil_export.stdout)
                    fossil_export.stdout.close()
                    git_import.communicate()
                    
                    # Git fast-import may exit with non-zero for warnings too,
                    # so we'll continue with the push regardless
                    if git_import.returncode != 0:
                        logger.warning(f"Git fast-import returned non-zero exit code {git_import.returncode}. Attempting to push anyway...")
                    
                    # Push the changes - moved inside the git directory context
                    logger.info("Pushing changes to Git repository...")
                    run_command(['git', 'checkout', '-f', 'master'], check=False)
                    run_command(['git', 'push', '-f', 'origin', '--all'])
                    run_command(['git', 'push', '-f', 'origin', '--tags'])
        
        logger.info(f"Successfully pushed Fossil changes from '{norm_path}' to Git repository.")
        
        # Automatically fix Git status after pushing
        logger.info(f"Fixing Git status for '{norm_path}' to hide untracked files...")
        fix_git_status(subdir_path, fossil_repo, config_file, fossil_args)
        
    except Exception as e:
        logger.error(f"Error during push to Git: {str(e)}")
        raise

def reset_marks(subdir_path, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_args=None):
    """Reset marks files for a repository to force a clean export/import."""
    norm_path = normalize_path(subdir_path)
    config = setup_repo_operation(norm_path, fossil_repo, config_file, fossil_args=fossil_args)
    try:
        repo_details = config['repositories'][norm_path]
        git_marks_file = Path(repo_details['git_marks_file'])
        fossil_marks_file = Path(repo_details['fossil_marks_file'])
        
        # Delete the marks files if they exist
        for marks_file in [git_marks_file, fossil_marks_file]:
            if marks_file.exists():
                logger.info(f"Removing marks file: {marks_file}")
                marks_file.unlink()
                
        logger.info(f"Marks files for '{norm_path}' have been reset. Next push will do a full export/import.")
        logger.info(f"Note: This may cause history to be rewritten in the Git repository.")
    except Exception as e:
        logger.error(f"Error during marks reset: {str(e)}")
        raise

def list_repos(config_file=CONFIG_FILE):
    """List all imported repositories and their details."""
    config = load_config(config_file)
    repositories = config.get('repositories', {})
    
    if not repositories:
        logger.info("No repositories have been imported.")
        return
    
    logger.info("Imported repositories:")
    for subdir, details in repositories.items():
        logger.info(f"- {subdir}: {details['git_repo_url']}")
        if logger.level == logging.DEBUG:  # More details when in debug mode
            logger.debug(f"  Clone path: {details['git_clone_path']}")
            logger.debug(f"  Git marks: {details['git_marks_file']}")
            logger.debug(f"  Fossil marks: {details['fossil_marks_file']}")

def fix_git_status(subdir_path, fossil_repo=FOSSIL_REPO, config_file=CONFIG_FILE, fossil_args=None):
    """Fix Git status display for subdirectory to hide untracked Git files."""
    norm_path = normalize_path(subdir_path)
    config = setup_repo_operation(norm_path, fossil_repo, config_file, fossil_args=fossil_args)
    
    try:
        repo_details = config['repositories'][norm_path]
        git_clone_path = Path(repo_details['git_clone_path'])
        target_dir = Path(repo_details.get('target_dir', norm_path))
        
        if not git_clone_path.exists() or not target_dir.exists():
            raise ValueError(f"Git clone path or target directory doesn't exist for {norm_path}")
        
        # Get absolute paths for reliable configuration
        git_clone_path_abs = os.path.abspath(git_clone_path)
        target_dir_abs = os.path.abspath(target_dir)
        git_dir_abs = os.path.join(git_clone_path_abs, '.git')
        
        # Create or update the .git file in the target directory
        git_link_path = os.path.join(target_dir_abs, '.git')
        with open(git_link_path, 'w') as f:
            f.write(f"gitdir: {git_dir_abs}")
        
        # Configure basic git settings
        with cd(git_clone_path_abs):
            # Set the core.worktree to the absolute target directory path
            run_command(['git', 'config', 'core.worktree', target_dir_abs])
            run_command(['git', 'config', 'status.showUntrackedFiles', 'no'])
        
        # Try the direct approach - run the fix function inline
        logger.info(f"Using advanced Git index fix for '{norm_path}'...")
        
        # Step 1: Configure Git to prevent showing untracked files
        with cd(target_dir_abs):
            run_command(['git', 'config', 'core.untrackedCache', 'false'], check=False)
            run_command(['git', 'config', 'status.showUntrackedFiles', 'no'], check=False)
            
            # Step 2: Create magical sequence to force git to recognize all files
            # First, add all files to git index
            logger.info("Indexing all files...")
            run_command(['git', 'add', '--force', '.'], check=False)
            
            # Then, reset (but keep the files in the index)
            logger.info("Resetting staging area (keeping files in index)...")
            run_command(['git', 'reset'], check=False)
            
            # Get list of all files in the directory
            logger.info("Registering files with Git index...")
            file_list = subprocess.check_output(['find', '.', '-type', 'f', 
                                              '-not', '-path', './.git*'], 
                                              text=True).splitlines()
            
            # Filter out common exclusions
            file_list = [f for f in file_list if not (
                f.endswith('.swp') or 
                f.endswith('~') or 
                '/.git/' in f or 
                '/__pycache__/' in f
            )]
            
            # Add .gitignore explicitly if it exists
            if os.path.exists('.gitignore') and './.gitignore' not in file_list:
                file_list.append('./.gitignore')
            
            # Process files in batches to avoid command line length limits
            batch_size = 100
            for i in range(0, len(file_list), batch_size):
                batch = file_list[i:i+batch_size]
                try:
                    # Use update-index to directly force Git to recognize these files
                    update_cmd = ['git', 'update-index', '--add', '--'] + batch
                    run_command(update_cmd, check=False)
                except Exception as e:
                    logger.warning(f"Error updating index batch {i//batch_size}: {e}")
        
        # Also fix the sparse checkout settings in the git clone path
        with cd(git_clone_path_abs):
            sparse_checkout_dir = os.path.join(git_dir_abs, 'info')
            os.makedirs(sparse_checkout_dir, exist_ok=True)
            sparse_checkout_file = os.path.join(sparse_checkout_dir, 'sparse-checkout')
            
            # Write a more permissive sparse checkout pattern
            with open(sparse_checkout_file, 'w') as f:
                f.write("/*\n")  # Match everything at the root level
            
            # Enable sparse checkout
            run_command(['git', 'config', 'core.sparseCheckout', 'true'], check=False)
            
            # Force Git to update the working tree with our new sparse-checkout settings
            run_command(['git', 'read-tree', '-mu', 'HEAD'], check=False)
            
        logger.info(f"Fixed Git status display for '{norm_path}'. Run 'git status' to verify.")
    except Exception as e:
        logger.error(f"Error fixing Git status: {str(e)}")
        raise

def main():
    """Parse command-line arguments and execute the appropriate command."""
    # Create a parent parser with common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parent_parser.add_argument('-f', '--fossil-repo', default=FOSSIL_REPO, help=f'Fossil repository file')
    parent_parser.add_argument('-c', '--config', default=CONFIG_FILE, help=f'Configuration file')
    parent_parser.add_argument('-g', '--git-clones-dir', default=GIT_CLONES_DIR, help=f'Git clones directory')
    parent_parser.add_argument('-M', '--marks-dir', default=MARKS_DIR, help=f'Marks directory')  # Changed -m to -M
    parent_parser.add_argument('--fwd-fossil-open', type=str, metavar='ARGS',
                               help='Forward arguments to fossil open command')
    parent_parser.add_argument('--fwd-fossil-init', type=str, metavar='ARGS',
                               help='Forward arguments to fossil init command')
    parent_parser.add_argument('--fwdfossil', type=str, metavar='FOSSIL_ARGS',
                               help='DEPRECATED - Forward arguments to fossil commands')
    
    # Main parser
    parser = argparse.ArgumentParser(description='Fossil Import Tool (fitrepo)')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    # Add common arguments to main parser
    parent_group = parser.add_argument_group('global options')
    for action in parent_parser._actions:
        parent_group._group_actions.append(action)
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')
    
    # Command definitions
    init_parser = subparsers.add_parser('init', help='Initialize repository and config', parents=[parent_parser])
    init_parser.add_argument('--novscode', action='store_true', help='Do not create VSCode settings file')
    
    subparsers.add_parser('list', help='List imported repositories', parents=[parent_parser])
    
    import_parser = subparsers.add_parser('import', help='Import Git repository', parents=[parent_parser])
    import_parser.add_argument('git_repo_url', help='URL of Git repository to import')
    import_parser.add_argument('subdir_name', help='Subdirectory name for import')
    import_parser.add_argument('--novscode', action='store_true', help='Do not update VSCode workspace file')
    
    update_parser = subparsers.add_parser('update', help='Update with Git changes', parents=[parent_parser])
    update_parser.add_argument('subdir_name', help='Subdirectory name to update')
    
    # Add command for git push
    git_push_parser = subparsers.add_parser('push-git', help='Push Fossil changes to Git', parents=[parent_parser])
    git_push_parser.add_argument('subdir_name', help='Subdirectory name to push')
    git_push_parser.add_argument('-m', '--message', help='Custom commit message for Git')
    
    # Add command for resetting marks
    reset_parser = subparsers.add_parser('reset-marks', help='Reset marks files for clean export', parents=[parent_parser])
    reset_parser.add_argument('subdir_name', help='Subdirectory name to reset marks for')
    
    # Add command for fixing git status
    fix_status_parser = subparsers.add_parser('fix-git-status', help='Fix Git status display', parents=[parent_parser])
    fix_status_parser.add_argument('subdir_name', help='Subdirectory name to fix')
    
    # Special handling for fwdfossil argument issue
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if '--fwdfossil' in ' '.join(sys.argv) and '-f' in sys.argv:
            print("ERROR: For the --fwdfossil argument with values starting with '-', use equals sign format:")
            print("Example: --fwdfossil=\"-f\"")
            sys.exit(1)
        raise

    # Set debug level if verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Parse fossil arguments
    fossil_args = shlex.split(args.fwdfossil) if args.fwdfossil else []
    fossil_open_args = shlex.split(args.fwd_fossil_open) if args.fwd_fossil_open else fossil_args
    fossil_init_args = shlex.split(args.fwd_fossil_init) if args.fwd_fossil_init else []
    
    # Ensure directories exist
    ensure_directories(args.git_clones_dir, args.marks_dir)

    # Command dispatch
    commands = {
        'init': lambda: init_fossil_repo(args.fossil_repo, args.config, fossil_open_args, fossil_init_args, args.novscode),
        'list': lambda: list_repos(args.config),
        'import': lambda: import_git_repo(args.git_repo_url, args.subdir_name, args.fossil_repo, 
                                         args.config, args.git_clones_dir, args.marks_dir, fossil_open_args, args.novscode),
        'update': lambda: update_git_repo(args.subdir_name, args.fossil_repo, args.config, fossil_open_args),
        'push-git': lambda: push_to_git(args.subdir_name, args.fossil_repo, args.config, fossil_open_args, args.message),
        'reset-marks': lambda: reset_marks(args.subdir_name, args.fossil_repo, args.config, fossil_open_args),
        'fix-git-status': lambda: fix_git_status(args.subdir_name, args.fossil_repo, args.config, fossil_open_args)
    }
    
    try:
        commands[args.command]()
    except (ValueError, subprocess.CalledProcessError) as e:
        logger.error(f"Command failed: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        exit(1)

if __name__ == '__main__':
    if not check_dependencies():
        logger.error("Missing required dependencies. Please install them before continuing.")
        logger.error("Make sure git, git-filter-repo, and fossil are installed.")
        logger.error("You can install git-filter-repo with: uv pip install git-filter-repo")
        exit(1)
    main()