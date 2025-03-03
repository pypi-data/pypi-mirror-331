import os
import time
import re
import sys
import fnmatch
from typing import List, Dict, Tuple, Optional
import glob

def list_available_snapshots(snapshot_dir: str = None) -> List[Dict[str, str]]:
    """
    List all available snapshots with their timestamps and comments.
    
    Args:
        snapshot_dir: Directory to search for snapshots (default: ./snapshots)
        
    Returns:
        List of dictionaries containing snapshot information
    """
    # Use default directory if none provided
    if not snapshot_dir:
        snapshot_dir = os.path.join(os.getcwd(), 'snapshots')
    
    # Ensure directory exists
    if not os.path.exists(snapshot_dir):
        print(f"Snapshot directory not found: {snapshot_dir}")
        return []
    
    # Find all snapshot files (markdown only)
    snapshot_files = glob.glob(os.path.join(snapshot_dir, "*.md"))
    if not snapshot_files:
        print(f"No snapshots found in {snapshot_dir}")
        return []
    
    snapshots = []
    
    # Extract information from each snapshot file
    for file_path in sorted(snapshot_files, key=os.path.getmtime, reverse=True):
        snapshot_info = {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'modified': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path))),
            'comment': extract_snapshot_comment(file_path),
            'is_backup': 'pre_restore_backup_' in os.path.basename(file_path)
        }
        snapshots.append(snapshot_info)
    
    return snapshots

def extract_snapshot_comment(snapshot_file_path: str) -> str:
    """
    Extract the comment from a snapshot file.
    
    Args:
        snapshot_file_path: Path to the snapshot file
        
    Returns:
        The comment string, or a default message if no comment is found
    """
    try:
        with open(snapshot_file_path, 'r', encoding='utf-8') as f:
            # Read first 2000 characters which should include the header and comment
            header = f.read(2000)
            
            # Look for the comment section in markdown
            comment_match = re.search(r"## Comments\n(.*?)(?=\n##|\Z)", header, re.DOTALL)
            if comment_match:
                return comment_match.group(1).strip()
    except Exception as e:
        pass
            
    return "(No comment)"

def display_snapshot_list(snapshots: List[Dict[str, str]]) -> None:
    """
    Display formatted list of snapshots with their details.
    
    Args:
        snapshots: List of snapshot information dictionaries
    """
    if not snapshots:
        print("No snapshots available.")
        return
    
    print("\nAvailable snapshots:")
    print("-" * 100)
    print(f"{'#':<3} {'Type':<8} {'Date':<19} {'Filename':<30} {'Comment'}")
    print("-" * 100)
    
    for i, snapshot in enumerate(snapshots, 1):
        # Truncate filename if it's too long
        filename = snapshot['filename']
        if len(filename) > 29:
            filename = filename[:26] + "..."
            
        # Truncate comment if it's too long
        comment = snapshot['comment']
        max_comment_len = 100 - 3 - 8 - 19 - 30 - 1  # Total width minus other columns
        if len(comment) > max_comment_len:
            comment = comment[:max_comment_len-3] + "..."
            
        snapshot_type = "BACKUP" if snapshot['is_backup'] else "SNAPSHOT"
        
        print(f"{i:<3} {snapshot_type:<8} {snapshot['modified']:<19} {filename:<30} {comment}")
    
    print("-" * 100)

def select_snapshot_interactive() -> Optional[str]:
    """
    Show list of available snapshots and let user select one.
    
    Returns:
        Path to the selected snapshot file, or None if cancelled
    """
    # Get snapshot list
    snapshots = list_available_snapshots()
    
    if not snapshots:
        return None
    
    # Display snapshots
    display_snapshot_list(snapshots)
    
    # Let user select
    while True:
        try:
            choice = input("\nEnter number to select a snapshot (or 'q' to quit): ").strip()
            
            if choice.lower() in ('q', 'quit', 'exit'):
                print("Selection cancelled.")
                return None
                
            idx = int(choice) - 1
            if 0 <= idx < len(snapshots):
                selected = snapshots[idx]['path']
                print(f"Selected: {selected}")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(snapshots)}.")
        except ValueError:
            print("Please enter a valid number.")
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled.")
            return None

def get_snapshot_path(arg_value) -> Optional[str]:
    """
    Convert a snapshot argument (path or index) to a valid snapshot path.
    
    Args:
        arg_value: Either a path to a snapshot file or an index (as string)
        
    Returns:
        Path to the selected snapshot file, or None if not found
    """
    if arg_value is None:
        return None
        
    # Try to interpret as an index
    try:
        idx = int(arg_value) - 1
        snapshots = list_available_snapshots()
        if 0 <= idx < len(snapshots):
            return snapshots[idx]['path']
        else:
            print(f"Error: Snapshot index {arg_value} is out of range (1-{len(snapshots)}).")
            return None
    except ValueError:
        # Not an integer, interpret as a path
        if os.path.isfile(arg_value):
            return arg_value
        else:
            print(f"Error: Snapshot file '{arg_value}' not found.")
            return None

def handle_restore(args):
    """Handle the restore command with enhanced snapshot selection."""
    import os
    from .restore import restore_from_snapshot, selective_restore
    
    # Convert snapshot arg to a path if it's a number
    if args.snapshot_file:
        args.snapshot_file = get_snapshot_path(args.snapshot_file)
        if not args.snapshot_file:
            return 1
    
    # If no snapshot file is specified, prompt for selection
    if args.snapshot_file is None:
        selected_snapshot = select_snapshot_interactive()
        if not selected_snapshot:
            return 1
        args.snapshot_file = selected_snapshot
    
    # Make target directory absolute
    target_dir = os.path.abspath(args.target_dir)
    
    # Create backup?
    create_backup = not args.no_backup
    
    # Check if selective restore is being used
    if args.patterns or args.exclude_patterns or args.interactive:
        try:
            backup_file = selective_restore(
                args.snapshot_file,
                target_dir,
                args.patterns,
                args.exclude_patterns,
                args.interactive,
                args.mode,
                create_backup,
                args.backup_path
            )
            return 0
        except Exception as e:
            print(f"Error during selective restoration: {e}")
            return 1
    else:
        # Use the standard restore
        try:
            backup_file = restore_from_snapshot(
                args.snapshot_file, 
                target_dir,
                args.mode,
                create_backup,
                args.backup_path
            )
            return 0
        except Exception as e:
            print(f"Error during restoration: {e}")
            return 1

def handle_snapshot(args):
    """Handle the snapshot command."""
    from .snapshot import create_snapshot
    
    start_path = os.path.abspath(args.start_path)
    output_folder = args.output_folder or 'snapshots'
    
    # Handle comment message
    comment = args.message
    if not comment and not args.no_comment_prompt:
        try:
            user_input = input("Would you like to add a comment for this snapshot? (y/n): ")
            if user_input.lower() in ('y', 'yes'):
                comment = input("Enter comment: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nComment prompt cancelled.")
            comment = None
    
    if not os.path.isdir(start_path):
        print(f"Error: {start_path} is not a valid directory.")
        return 1
    
    print(f"Creating markdown snapshot from {start_path}...")
    
    output_file = create_snapshot(start_path, output_folder, None, comment)
    print(f"Done! Snapshot saved to: {output_file}")
    
    return 0

# Main entry point function updates for the CLI
def main():
    """
    Main entry point for the snapshot_pkg utility.
    Provides a unified interface for both snapshot and restore functionality.
    """
    import argparse
    import sys
    from .snapshot import create_snapshot
    
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Create and restore snapshots of code packages or directories.",
        prog="snapshot-pkg"
    )
    
    # Add global options
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help="List all available snapshots and exit"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create the parser for the "snapshot" command
    snapshot_parser = subparsers.add_parser("snapshot", help="Create a snapshot of a directory")
    snapshot_parser.add_argument(
        'start_path',
        metavar='PATH',
        type=str,
        nargs='?',
        default='.',
        help="The directory to snapshot (default: current directory)."
    )
    snapshot_parser.add_argument(
        '-o', '--output-folder',
        type=str,
        help="The folder in which to store the output file (default: [start_path]/snapshots)."
    )
    snapshot_parser.add_argument(
        '-m', '--message',
        type=str,
        help="Add a comment message to the snapshot describing its purpose."
    )
    snapshot_parser.add_argument(
        '--no-comment-prompt',
        action='store_true',
        help="Don't prompt for a comment message if one isn't provided."
    )
    
    # Create the parser for the "restore" command with enhanced options
    restore_parser = subparsers.add_parser("restore", help="Restore from a snapshot")
    
    restore_parser.add_argument(
        'snapshot_file',
        type=str,
        nargs='?',
        help="Path to the snapshot file to restore from, or snapshot number from the list."
    )
    restore_parser.add_argument(
        'target_dir',
        type=str,
        nargs='?',
        default='.',
        help="Directory to restore to (default: current directory)."
    )
    restore_parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['safe', 'overwrite', 'force'],
        default='overwrite',
        help=("Restoration mode: 'safe' skips existing files, 'overwrite' replaces "
              "existing files (default), 'force' replaces all files.")
    )
    restore_parser.add_argument(
        '--no-backup',
        action='store_true',
        help="Skip creating a backup before restoration."
    )
    restore_parser.add_argument(
        '-b', '--backup-path',
        type=str,
        help="Custom path for the backup file."
    )
    # Add selective restoration options
    restore_parser.add_argument(
        '-p', '--pattern',
        action='append',
        dest='patterns',
        help="Include only files matching this glob pattern (can be used multiple times)"
    )
    restore_parser.add_argument(
        '-e', '--exclude',
        action='append',
        dest='exclude_patterns',
        help="Exclude files matching this glob pattern (can be used multiple times)"
    )
    restore_parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help="Interactively select files to restore"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle the list command or option first
    if args.list:
        snapshots = list_available_snapshots()
        display_snapshot_list(snapshots)
        return 0
    
    # Show help if no command is specified
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the specified command
    if args.command == "snapshot":
        return handle_snapshot(args)
    elif args.command == "restore":
        return handle_restore(args)