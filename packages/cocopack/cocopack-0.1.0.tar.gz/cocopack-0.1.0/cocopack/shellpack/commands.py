import os, sys
from .cli import get_script_path

def run_shell_function(script_name, function_name, *args):
    """Run a shell function from a script"""
    script_path = get_script_path(script_name)
    cmd = f"source {script_path} && {function_name} {' '.join(args)}"
    return os.system(cmd)

### from shell/ezshell.sh

def show_symlinks():
    """Direct command for show_symlinks"""
    return run_shell_function('ezshell.sh', 'show_symlinks', *sys.argv[1:])

def show_storage():
    """Direct command for show_storage"""
    return run_shell_function('ezshell.sh', 'show_storage', *sys.argv[1:])

def safe_remove():
    """Direct command for safe_remove"""
    return run_shell_function('ezshell.sh', 'safe_remove', *sys.argv[1:])

def rcd():
    """Direct command for rcdf"""
    return run_shell_function('ezshell.sh', 'recursive_cd_subdir', *sys.argv[1:])

def move_with_symlink():
    """Direct command for move_with_symlink"""
    return run_shell_function('ezshell.sh', 'move_with_symlink', *sys.argv[1:])

def split_path():
    """Direct command for split_path"""
    return run_shell_function('ezshell.sh', 'split_path', *sys.argv[1:])

def path_cleanup():
    """Direct command for path_cleanup"""
    return run_shell_function('ezshell.sh', 'path_cleanup', *sys.argv[1:])

def print_python_versions():
    """Direct command for print_python_versions"""
    return run_shell_function('ezshell.sh', 'print_python_versions', *sys.argv[1:])

### from shell/colorcode.sh

def color_wrap():
    """Direct command for color_wrap"""
    return run_shell_function('colorcode.sh', 'color_wrap', *sys.argv[1:])

### from shell/helpers/jekyll.sh

def jekyll_restart():
    """Direct command for jekyll_restart"""
    return run_shell_function('helpers/jekyll.sh', 'jekyll_restart', *sys.argv[1:])

def jekyll_reload():
    """Direct command for jekyll_reload"""
    return run_shell_function('helpers/jekyll.sh', 'jekyll_reload', *sys.argv[1:])

def jekyll_restart_plus():
    """Direct command for jekyll_restart_plus"""
    return run_shell_function('helpers/jekyll.sh', 'jekyll_restart_plus', *sys.argv[1:])

### shell/scripts/clear_git_history.sh

def clear_git_history():
    """Direct command for clear_git_history"""
    if len(sys.argv) < 2:
        print("Usage: clear-git-history <commit_message>")
        sys.exit(1)
    script_path = get_script_path('scripts/clear_git_history.sh')
    return run_shell_function(script_path, *sys.argv[1:]) 