#!/usr/bin/env python3
import os
import re
import time
import fnmatch
from typing import Optional, Dict, Tuple, List, Set
from .snapshot import create_snapshot, parse_snapshot_file

def is_backup_snapshot(snapshot_file_path: str) -> bool:
    """
    Determine if a snapshot file is already a backup file.
    
    Args:
        snapshot_file_path: Path to the snapshot file
        
    Returns:
        True if the file appears to be a backup snapshot, False otherwise
    """
    # Check the filename pattern
    filename = os.path.basename(snapshot_file_path)
    if filename.startswith("pre_restore_backup_"):
        return True
        
    # Check file content for automatic backup comment
    try:
        with open(snapshot_file_path, 'r', encoding='utf-8') as f:
            # Read first 2000 characters which should include the header and comment
            header = f.read(2000)
            
            # Look for the automatic backup comment
            if "## Comments" in header and "Automatic backup created before restoration" in header:
                return True
    except:
        # If we can't read the file, assume it's not a backup
        pass
            
    return False

def create_backup_snapshot(target_dir: str, backup_path: str = None, comment: str = None) -> str:
    """
    Create a backup snapshot of the current state before restoration.
    
    Args:
        target_dir: Directory to snapshot
        backup_path: Custom path for the backup file
        comment: Optional comment to include in the backup
        
    Returns:
        Path to the created backup file
    """
    print(f"Creating backup snapshot of current state...")
    
    # Use the create_snapshot function
    backup_dir = os.path.dirname(backup_path) if backup_path else os.path.join(target_dir, 'snapshots')
    
    # Generate a backup with a special prefix
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create the backup
    if backup_path:
        # If a specific backup path is provided, ensure its directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        auto_comment = "Automatic backup created before restoration" if comment is None else comment
        output_file = create_snapshot(target_dir, os.path.dirname(backup_path), None, auto_comment)
        # Rename to the specified file if needed
        if output_file != backup_path:
            os.rename(output_file, backup_path)
            output_file = backup_path
    else:
        # Default: create in snapshots directory with pre_restore prefix
        backup_dir = os.path.join(target_dir, 'snapshots')
        auto_comment = "Automatic backup created before restoration" if comment is None else comment
        output_file = create_snapshot(target_dir, 'snapshots', None, auto_comment)
        
        # Rename the file to indicate it's a pre-restore backup
        new_filename = os.path.join(backup_dir, f"pre_restore_backup_{timestamp}.md")
        os.rename(output_file, new_filename)
        output_file = new_filename
    
    print(f"Backup created at: {output_file}")
    return output_file

def restore_from_snapshot(snapshot_file_path: str, target_dir: str, 
                        mode: str = 'overwrite', create_backup: bool = True,
                        backup_path: str = None) -> Optional[str]:
    """
    Restore a project structure from a snapshot file.
    
    Args:
        snapshot_file_path: Path to the snapshot file
        target_dir: Directory to restore to
        mode: Restoration mode:
              - 'safe': skips existing files
              - 'overwrite': replaces existing files (default)
              - 'force': replaces all files
        create_backup: Whether to create a backup before restoring
        backup_path: Custom path for the backup file
        
    Returns:
        Path to the backup file if created, None otherwise
    """
    backup_file = None
    
    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Check if we're restoring from a backup file
    is_backup = is_backup_snapshot(snapshot_file_path)
    
    # Create backup if requested and we're not already restoring from a backup
    if create_backup and not is_backup:
        backup_file = create_backup_snapshot(target_dir, backup_path)
    elif create_backup and is_backup:
        print("Notice: Skipping backup creation since you're restoring from a backup file.")
    
    # Parse the snapshot file
    file_contents, comment = parse_snapshot_file(snapshot_file_path)
    
    # Display comment if present
    if comment:
        print("\nSnapshot comment:")
        print(f"----------------")
        print(comment)
        print()
    
    # Restore files
    files_restored = 0
    files_skipped = 0
    
    print(f"Restoring files to {target_dir}...")
    
    for file_path, content in file_contents.items():
        # Skip binary file markers
        if content == "[Binary file - contents not shown]":
            print(f"Skipping binary file: {file_path}")
            files_skipped += 1
            continue
            
        full_path = os.path.join(target_dir, file_path)
        dir_path = os.path.dirname(full_path)
        
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        file_exists = os.path.exists(full_path)
        
        if file_exists and mode == 'safe':
            print(f"Skipping existing file: {file_path}")
            files_skipped += 1
            continue
            
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if file_exists:
            print(f"Overwritten: {file_path}")
        else:
            print(f"Created: {file_path}")
        
        files_restored += 1
    
    print(f"\nRestoration complete!")
    print(f"Files restored: {files_restored}")
    print(f"Files skipped: {files_skipped}")
    
    if backup_file:
        print(f"\nNote: A backup was created at {backup_file}")
        print(f"To undo this restoration, run: snapshot-pkg restore {backup_file} {target_dir}")
    
    return backup_file

def selective_restore(snapshot_file_path: str, target_dir: str,
                     patterns: List[str] = None, exclude_patterns: List[str] = None,
                     interactive: bool = False, mode: str = 'overwrite',
                     create_backup: bool = True, backup_path: str = None) -> Optional[str]:
    """
    Selectively restore files from a snapshot based on patterns or interactive selection.
    
    Args:
        snapshot_file_path: Path to the snapshot file
        target_dir: Directory to restore to
        patterns: List of glob patterns to include (e.g. ['*.py', 'docs/*.md'])
        exclude_patterns: List of glob patterns to exclude
        interactive: Whether to prompt the user for each file
        mode: Restoration mode ('safe', 'overwrite', or 'force')
        create_backup: Whether to create a backup before restoring
        backup_path: Custom path for the backup file
        
    Returns:
        Path to the backup file if created, None otherwise
    """
    backup_file = None
    
    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Check if we're restoring from a backup file
    is_backup = is_backup_snapshot(snapshot_file_path)
    
    # Create backup if requested and we're not already restoring from a backup
    if create_backup and not is_backup:
        backup_file = create_backup_snapshot(target_dir, backup_path)
    elif create_backup and is_backup:
        print("Notice: Skipping backup creation since you're restoring from a backup file.")
    
    # Parse the snapshot file
    file_contents, comment = parse_snapshot_file(snapshot_file_path)
    
    # Display comment if present
    if comment:
        print("\nSnapshot comment:")
        print(f"----------------")
        print(comment)
        print()
    
    # Filter files based on patterns
    selected_files = {}
    if patterns:
        # Include only files that match at least one pattern
        for file_path, content in file_contents.items():
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns):
                if exclude_patterns and any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns):
                    # Skip if it matches an exclude pattern
                    continue
                selected_files[file_path] = content
    else:
        # Start with all files
        selected_files = dict(file_contents)
        # Remove excluded files
        if exclude_patterns:
            for file_path in list(selected_files.keys()):
                if any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns):
                    del selected_files[file_path]
    
    # Interactive selection
    if interactive:
        print("Selecting files to restore:")
        print("--------------------------")
        
        # Sort files to display directories together
        file_list = sorted(selected_files.keys())
        final_selection = {}
        
        # Group files by directory for better organization
        dirs = {}
        for file_path in file_list:
            dir_path = os.path.dirname(file_path)
            if dir_path not in dirs:
                dirs[dir_path] = []
            dirs[dir_path].append(file_path)
        
        # Process by directory
        for dir_path, files in sorted(dirs.items()):
            print(f"\nDirectory: {dir_path or '.'}")
            
            # Ask if user wants to restore all files in this directory
            if len(files) > 1:
                response = input(f"  Restore all {len(files)} files in this directory? (y/n/q to quit): ").lower()
                if response == 'q':
                    print("Restoration cancelled.")
                    return backup_file
                
                if response in ('y', 'yes'):
                    for file_path in files:
                        final_selection[file_path] = selected_files[file_path]
                    continue
            
            # Ask for each file
            for file_path in files:
                file_name = os.path.basename(file_path)
                file_exists = os.path.exists(os.path.join(target_dir, file_path))
                status = " (exists)" if file_exists else " (new)"
                
                # Skip binary files
                if selected_files[file_path] == "[Binary file - contents not shown]":
                    print(f"  Skipping binary file: {file_name}")
                    continue
                
                response = input(f"  Restore {file_name}{status}? (y/n/q to quit): ").lower()
                if response == 'q':
                    print("Restoration cancelled.")
                    return backup_file
                
                if response in ('y', 'yes'):
                    final_selection[file_path] = selected_files[file_path]
        
        # Update selection
        selected_files = final_selection
    
    # Proceed with restoration of selected files
    files_restored = 0
    files_skipped = 0
    
    print(f"\nRestoring {len(selected_files)} files to {target_dir}...")
    
    for file_path, content in selected_files.items():
        # Skip binary file markers
        if content == "[Binary file - contents not shown]":
            print(f"Skipping binary file: {file_path}")
            files_skipped += 1
            continue
            
        full_path = os.path.join(target_dir, file_path)
        dir_path = os.path.dirname(full_path)
        
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        file_exists = os.path.exists(full_path)
        
        if file_exists and mode == 'safe':
            print(f"Skipping existing file: {file_path}")
            files_skipped += 1
            continue
            
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if file_exists:
            print(f"Overwritten: {file_path}")
        else:
            print(f"Created: {file_path}")
        
        files_restored += 1
    
    print(f"\nRestoration complete!")
    print(f"Files restored: {files_restored}")
    print(f"Files skipped: {files_skipped}")
    
    if backup_file:
        print(f"\nNote: A backup was created at {backup_file}")
        print(f"To undo this restoration, run: snapshot-pkg restore {backup_file} {target_dir}")
    
    return backup_file