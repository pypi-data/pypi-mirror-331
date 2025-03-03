#!/usr/bin/env python3
"""
Utility functions for snapshot_pkg.
"""

import os
import re


def is_binary_file(file_path):
    """
    Determine if a file is binary by checking its content.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file appears to be binary, False otherwise
    """
    try:
        # Try to open the file in text mode
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first chunk of the file (4KB is usually enough to determine)
            chunk = f.read(4096)
            
            # Check for common binary file signatures
            # This approach looks for null bytes and other control characters
            # that are uncommon in text files
            binary_chars = [
                char for char in chunk 
                if ord(char) < 9 or (ord(char) > 13 and ord(char) < 32)
            ]
            
            # If we found binary characters, it's likely a binary file
            # Use a threshold to avoid false positives with some text files
            if len(binary_chars) > 0:
                return True
                
            return False
    except UnicodeDecodeError:
        # If we can't decode it as UTF-8, it's a binary file
        return True
    except Exception:
        # For any other error, assume it's binary to be safe
        return True


def get_file_language(file_path):
    """
    Determine the language for syntax highlighting based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A string representing the language for markdown code blocks
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Map common extensions to languages
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.xml': 'xml',
        '.json': 'json',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.java': 'java',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.pl': 'perl',
        '.swift': 'swift',
        '.rs': 'rust',
        '.r': 'r',
        '.lua': 'lua',
        '.sql': 'sql',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.txt': 'text',
        '.gitignore': 'gitignore',
    }
    
    return language_map.get(ext, '')  # Empty string if no match found


def get_file_icon(filename):
    """
    Returns an appropriate emoji icon for a file based on its extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        String emoji representing the file type
    """
    ext = os.path.splitext(filename)[1].lower()
    
    # Map common extensions to icons
    icon_map = {
        '.py': '🐍',     # Python
        '.js': '📜',     # JavaScript
        '.ts': '📜',     # TypeScript
        '.html': '🌐',   # HTML
        '.css': '🎨',    # CSS
        '.json': '📋',   # JSON
        '.md': '📝',     # Markdown
        '.txt': '📄',    # Text
        '.xml': '📋',    # XML
        '.csv': '📊',    # CSV
        '.xlsx': '📊',   # Excel
        '.pdf': '📑',    # PDF
        '.png': '🖼️',    # PNG image
        '.jpg': '🖼️',    # JPEG image
        '.jpeg': '🖼️',   # JPEG image
        '.gif': '🖼️',    # GIF image
        '.svg': '🖼️',    # SVG image
        '.mp3': '🎵',    # Audio
        '.mp4': '🎬',    # Video
        '.zip': '📦',    # ZIP archive
        '.tar': '📦',    # TAR archive
        '.gz': '📦',     # GZIP archive
        '.gitignore': '🔧', # Git
        '.sh': '⚙️',      # Shell
        '.bash': '⚙️',    # Bash
        '.sql': '💾',    # SQL
        '.cpp': '⚙️',    # C++
        '.c': '⚙️',      # C
        '.h': '⚙️',      # Header
        '.java': '☕',   # Java
        '.rb': '💎',     # Ruby
        '.php': '🐘',    # PHP
        '.go': '🔹',     # Go
        '.rs': '🦀',     # Rust
        '.dart': '🎯',   # Dart
        '.swift': '🔶',  # Swift
        '.kt': '🔷',     # Kotlin
        '.in': '📄',     # .in files
        '.toml': '📄',   # TOML files
    }
    
    return icon_map.get(ext, '📄')  # Default file icon


def create_filename_anchor(file_path):
    """
    Create a GitHub-compatible anchor for a file path.
    
    Args:
        file_path: The file path to create an anchor for
        
    Returns:
        A string suitable for use as an HTML anchor
    """
    # Convert to lowercase, replace / with -, and remove special characters
    anchor = file_path.lower().replace('/', '-').replace('\\', '-')
    # Remove unwanted characters
    anchor = re.sub(r'[^a-z0-9\-_]', '', anchor)
    return anchor