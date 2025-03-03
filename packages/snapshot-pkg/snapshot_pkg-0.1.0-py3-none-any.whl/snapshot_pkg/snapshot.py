#!/usr/bin/env python3
import os
import re
from pathlib import Path
import time
import pathspec

from .utils import (
    is_binary_file, 
    get_file_language, 
    get_file_icon,
    create_filename_anchor
)

def load_gitignore_patterns(start_path):
    """
    Load patterns from .gitignore file or create default if none exists.
    
    Args:
        start_path: Directory to look for .gitignore file
        
    Returns:
        A tuple of (pathspec.PathSpec object, gitignore_path)
    """
    gitignore_path = os.path.join(start_path, '.gitignore')
    
    # Create default .gitignore if it doesn't exist
    if not os.path.isfile(gitignore_path):
        print(f"No .gitignore file found at {gitignore_path}")
        print(f"Creating default .gitignore file...")
        create_default_gitignore(gitignore_path)
    
    def remove_spkg_tags(line):
        if line.startswith("#spkg"):
            return line[5:].strip()
        else:
            return line

    try:
        with open(gitignore_path, 'r') as f:      
            # Create a PathSpec object from the gitignore patterns
            spec = pathspec.PathSpec.from_lines('gitwildmatch', map(remove_spkg_tags,f.readlines()))
            print(f"Using patterns from .gitignore at {gitignore_path}")
            return spec, gitignore_path
    except Exception as e:
        print(f"Warning: Error loading .gitignore file {gitignore_path}: {e}")
        print("Creating and using a default .gitignore file...")
        create_default_gitignore(gitignore_path)
        with open(gitignore_path, 'r') as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', map(remove_spkg_tags,f.readlines()))
            return spec, gitignore_path

def create_default_gitignore(gitignore_path):
    """
    Create a default .gitignore file with common patterns.
    Includes examples of snapshot_pkg specific exclusions.
    """
    gitignore_content = [
        "# Default .gitignore created by snapshot-pkg",
        "# Includes common patterns for Python projects",
        "",
        "# snapshot-pkg output",
        "snapshots/",
        "",
        "# Example of snapshot-pkg specific exclusions",
        "# Git will ignore lines with a leading #spkg comment, but snapshot-pkg will use them",
        "#spkg my_secret_config.ini",
        "#spkg temporary_work/",
        "",
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        "",
        "# Virtual environments",
        "venv/",
        ".venv/",
        "env/",
        ".env/",
        "ENV/",
        "",
        "# IDEs and editors",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Build and distribution",
        "dist/",
        "build/",
        "",
        "# Version control",
        ".git/",
        ".hg/",
        ".svn/",
        ".bzr/",
        "",
        "# Frontend specific",
        "node_modules/",
        "bower_components/",
        "package-lock.json",
        "yarn.lock",
        "npm-debug.log",
        "yarn-error.log",
        "",
        "# Data and logs",
        "logs/",
        "*.log",
        "*.csv",
        "*.sqlite",
        "*.db"
    ]
    
    with open(gitignore_path, 'w') as f:
        f.write('\n'.join(gitignore_content))
    
    print(f"Created default .gitignore file at: {gitignore_path}")

def should_ignore(path: str, gitignore_spec, root_path: str, output_folder: str = None) -> bool:
    """
    Check if path should be ignored based on gitignore patterns.
    
    Args:
        path: Absolute path to check
        gitignore_spec: A pathspec.PathSpec object with gitignore patterns
        root_path: The root path of the project
        output_folder: Output folder path to exclude
        
    Returns:
        True if the path should be ignored, False otherwise
    """
    # Always ignore the output folder
    if output_folder:
        output_path = os.path.normpath(os.path.abspath(os.path.join(root_path, output_folder)))
        path_abs = os.path.normpath(os.path.abspath(path))
        # Check if path is output_path or is inside output_path
        if path_abs == output_path or path_abs.startswith(output_path + os.sep):
            return True
    
    # Handle .gitignore file specially - we don't want to ignore it
    if os.path.basename(path) == '.gitignore':
        return True
    
    # Get path relative to the project root
    rel_path = os.path.relpath(path, root_path)
    
    # Use pathspec to check if the path matches any gitignore pattern
    return gitignore_spec.match_file(rel_path)

def find_directories_with_visible_content(start_path, gitignore_spec, output_folder):
    """
    Scans the directory structure to identify directories that should be visible in the tree.
    A directory is visible if it contains non-ignored files or has subdirectories with visible content.
    """
    directories_with_content = set()
    
    # Traverse bottom-up to properly propagate visibility up the tree
    for root, dirs, files in os.walk(start_path, topdown=False):
        root_path = os.path.abspath(root)
        
        # Check if this directory is explicitly ignored
        if root != start_path and should_ignore(root, gitignore_spec, start_path, output_folder):
            continue
            
        # Check if this directory has any visible files
        has_visible_files = False
        for file in files:
            file_path = os.path.join(root, file)
            if not should_ignore(file_path, gitignore_spec, start_path, output_folder):
                has_visible_files = True
                break
                
        # Check if any subdirectories have visible content
        has_visible_subdirs = False
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if dir_path in directories_with_content:
                has_visible_subdirs = True
                break
                
        # If this directory has visible content or is the root, mark it as visible
        if has_visible_files or has_visible_subdirs or root == start_path:
            directories_with_content.add(root_path)
    
    return directories_with_content

def build_tree_representation_markdown(start_path, visible_directories, gitignore_spec, output_folder):
    """
    Builds a markdown tree representation, showing only directories with visible content.
    Uses prettier formatting with unicode box-drawing characters inside a code block.
    
    Args:
        start_path: The root directory to start from
        visible_directories: Set of directories that contain visible content
        gitignore_spec: The gitignore patterns to apply
        output_folder: The output folder to always exclude
        
    Returns:
        A list of strings representing the directory tree in markdown format
    """
    # Get project root name
    root_name = os.path.basename(start_path)
    
    # Structure to hold our tree hierarchy
    class TreeNode:
        def __init__(self, name, is_dir=False):
            self.name = name
            self.is_dir = is_dir
            self.children = []
    
    # Create the root node
    root = TreeNode(root_name, True)
    
    # Build the tree structure
    for current_dir, dirs, files in os.walk(start_path):
        # Skip directories without visible content
        dirs[:] = [d for d in dirs if os.path.join(current_dir, d) in visible_directories]
        
        # Skip explicitly ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(current_dir, d), gitignore_spec, start_path, output_folder)]
        
        # Get the path relative to start_path
        rel_path = os.path.relpath(current_dir, start_path)
        
        # Find the parent node for the current path
        if rel_path == '.':
            parent_node = root
        else:
            # Build the path to this node
            path_parts = rel_path.split(os.sep)
            
            # Navigate to the correct parent node
            current_node = root
            for part in path_parts:
                found = False
                for child in current_node.children:
                    if child.name == part and child.is_dir:
                        current_node = child
                        found = True
                        break
                if not found:
                    # This shouldn't happen if the walker is operating correctly
                    new_node = TreeNode(part, True)
                    current_node.children.append(new_node)
                    current_node = new_node
            
            parent_node = current_node
        
        # Add directory nodes
        for d in sorted(dirs):
            dir_path = os.path.join(current_dir, d)
            if not should_ignore(dir_path, gitignore_spec, start_path, output_folder):
                dir_node = TreeNode(d, True)
                parent_node.children.append(dir_node)
        
        # Add file nodes
        for f in sorted(files):
            file_path = os.path.join(current_dir, f)
            if not should_ignore(file_path, gitignore_spec, start_path, output_folder):
                file_node = TreeNode(f, False)
                parent_node.children.append(file_node)
    
    # Render the tree
    lines = []
    
    def render_tree(node, prefix="", is_last=True, is_root=False):
        # Add the current node
        if is_root:
            lines.append(f"📦 {node.name}")
        else:
            connector = "└─" if is_last else "├─"
            icon = "📂" if node.is_dir else get_file_icon(node.name)
            lines.append(f"{prefix}{connector} {icon} {node.name}")
        
        # Prepare the prefix for children
        if is_root:
            child_prefix = ""
        else:
            child_prefix = prefix + ("   " if is_last else "│  ")
        
        # Render children
        for i, child in enumerate(node.children):
            is_last_child = i == len(node.children) - 1
            render_tree(child, child_prefix, is_last_child)
    
    # Start rendering from the root
    render_tree(root, is_root=True)
    
    return lines

def get_file_tree(start_path: str, gitignore_spec, output_folder: str) -> str:
    """
    Generate a markdown tree representation of the directory structure.
    
    Args:
        start_path: The root directory to start from
        gitignore_spec: The gitignore patterns to apply
        output_folder: The output folder to always exclude
        
    Returns:
        A string representing the directory tree in markdown format
    """
    start_path = os.path.abspath(start_path)
    
    # Find directories that contain non-ignored content
    visible_directories = find_directories_with_visible_content(start_path, gitignore_spec, output_folder)
    
    # Build the tree using only directories with visible content
    tree_lines = build_tree_representation_markdown(start_path, visible_directories, gitignore_spec, output_folder)
    
    # Return a code block with the tree content for better formatting
    return "```\n" + "\n".join(tree_lines) + "\n```"

def create_table_of_contents(file_paths):
    """
    Create a markdown table of contents with links to file sections.
    
    Args:
        file_paths: List of file paths to include in the TOC
        
    Returns:
        A string containing the markdown TOC
    """
    toc_lines = []
    
    for i, file_path in enumerate(sorted(file_paths), 1):
        anchor = create_filename_anchor(file_path)
        toc_lines.append(f"{i}. [{file_path}](#{anchor})")
    
    return '\n'.join(toc_lines)

def create_snapshot(start_path: str, output_folder: str, config=None, comment=None):
    """
    Create a snapshot of all package files into a single markdown document.
    
    Args:
        start_path: The root directory to snapshot
        output_folder: Directory to store the output file
        config: Configuration options (not used in this version)
        comment: Optional comment to include in the snapshot
        
    Returns:
        Path to the created snapshot file
    """
    # Load gitignore patterns
    gitignore_spec, gitignore_path = load_gitignore_patterns(start_path)
    
    # Ensure output folder exists
    output_dir = os.path.join(start_path, output_folder)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"snapshot_{timestamp}.md")
    
    # Start with header
    content = [
        f"# Package Snapshot - Generated on {timestamp}",
        "",
    ]
    
    # Add comments section if provided
    if comment:
        content.extend([
            "## Comments",
            comment,
            "",
        ])
    
    # Continue with directory structure
    content.extend([
        "## Directory Structure",
        get_file_tree(start_path, gitignore_spec, output_folder),
        "",
    ])
    
    # Collect file paths for table of contents
    file_paths = []
    for root, dirs, files in os.walk(start_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), gitignore_spec, start_path, output_folder)]
        
        for file in sorted(files):
            file_path = os.path.join(root, file)
            if not should_ignore(file_path, gitignore_spec, start_path, output_folder):
                rel_path = os.path.relpath(file_path, start_path)
                file_paths.append(rel_path)
    
    # Add table of contents
    content.extend([
        "## Table of Contents",
        create_table_of_contents(file_paths),
        "",
        "## Files",
        "",
    ])
    
    # Define Unicode character for backtick replacement (Left Single Quotation Mark: U+2018)
    BACKTICK_REPLACEMENT = '′'  # Prime character (U+2032)
    
    # Walk through all files
    for root, dirs, files in os.walk(start_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), gitignore_spec, start_path, output_folder)]
        
        for file in sorted(files):
            if not should_ignore(os.path.join(root, file), gitignore_spec, start_path, output_folder):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, start_path)
                anchor = create_filename_anchor(rel_path)
                # Determine language for syntax highlighting
                language = get_file_language(file_path)

                if is_binary_file(file_path):
                    content.extend([
                        f"<a id=\"{anchor}\"></a>",
                        f"### {rel_path}",
                        "_Binary file - contents not shown_",
                        "",
                    ])
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            
                            # If the file is markdown or contains triple backticks, replace them
                            if '```' in file_content:
                                # Replace backticks with the unicode character
                                file_content = file_content.replace('```', f"{BACKTICK_REPLACEMENT}{BACKTICK_REPLACEMENT}{BACKTICK_REPLACEMENT}")
                            
                            content.extend([
                                f"<a id=\"{anchor}\"></a>",
                                f"### {rel_path}",
                                f"```{language}",
                                file_content,
                                "```",
                                "",  # Empty line after file content
                            ])
                    except UnicodeDecodeError:
                        content.extend([
                            f"<a id=\"{anchor}\"></a>",
                            f"### {rel_path}",
                            "_Binary file - contents not shown_",
                            "",
                        ])
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return output_file

def parse_snapshot_file(snapshot_file_path: str):
    """
    Parse a markdown snapshot file to extract the file structure and content.
    
    Args:
        snapshot_file_path: Path to the markdown snapshot file to parse
        
    Returns:
        Tuple of (file_contents, comment) where:
        - file_contents: Dictionary mapping file paths to their contents
        - comment: Optional comment from the snapshot
    """
    print(f"Parsing snapshot file: {snapshot_file_path}")
    
    with open(snapshot_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize the dictionary to store file contents
    file_contents = {}
    
    # Extract comment if present
    comment = None
    comment_match = re.search(r"## Comments\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if comment_match:
        comment = comment_match.group(1).strip()
    
    # Pattern to match binary files
    binary_pattern = r'<a id="[^"]+"></a>\n### ([^\n]+)\n_Binary file - contents not shown_'
    for match in re.finditer(binary_pattern, content):
        file_path = match.group(1).strip()
        file_contents[file_path] = "[Binary file - contents not shown]"
    
    # Pattern to match regular files with code blocks
    # This pattern will match both backticks and prime characters for compatibility with tests
    code_pattern = r'<a id="[^"]+"></a>\n### ([^\n]+)\n(?:```)(?:[^\n]*)\n(.*?)\n(?:```)'
    for match in re.finditer(code_pattern, content, re.DOTALL):
        file_path = match.group(1).strip()
        file_contents[file_path] = match.group(2)
    
    return file_contents, comment