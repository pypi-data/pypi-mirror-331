import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snapshot_pkg.snapshot import create_snapshot, parse_snapshot_file
from snapshot_pkg.restore import restore_from_snapshot, selective_restore


class TestSnapshotCreation(unittest.TestCase):
    """Test cases for snapshot creation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'snapshots')
        os.makedirs(self.output_dir)
        
        # Create a simple project structure
        self.project_dir = os.path.join(self.test_dir, 'project')
        os.makedirs(os.path.join(self.project_dir, 'src'))
        os.makedirs(os.path.join(self.project_dir, 'tests'))
        
        # Create some files
        with open(os.path.join(self.project_dir, 'README.md'), 'w') as f:
            f.write('# Test Project\n\nThis is a test project.\n')
        
        with open(os.path.join(self.project_dir, 'src', 'main.py'), 'w') as f:
            f.write('def hello():\n    return "Hello, world!"\n')
        
        with open(os.path.join(self.project_dir, 'tests', 'test_main.py'), 'w') as f:
            f.write('def test_hello():\n    assert hello() == "Hello, world!"\n')
        
        # Create a .gitignore file
        with open(os.path.join(self.project_dir, '.gitignore'), 'w') as f:
            f.write('*.pyc\n__pycache__/\n#spkg secret.txt\n')
        
        # Create a file that should be ignored
        with open(os.path.join(self.project_dir, 'secret.txt'), 'w') as f:
            f.write('This is a secret file that should be ignored.\n')
        
        # Create a binary file
        with open(os.path.join(self.project_dir, 'binary.bin'), 'wb') as f:
            f.write(b'\x00\x01\x02\x03')

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.test_dir)

    # Patch the is_binary_file function to always return True for binary.bin
    @patch('snapshot_pkg.snapshot.is_binary_file')
    def test_create_snapshot(self, mock_is_binary):
        """Test creating a snapshot of a project."""
        # Make the mock return True for binary.bin and False for others
        def side_effect(file_path):
            return os.path.basename(file_path) == 'binary.bin'
        mock_is_binary.side_effect = side_effect
        
        snapshot_file = create_snapshot(self.project_dir, self.output_dir, comment="Test snapshot")
        
        # Check that the snapshot file was created
        self.assertTrue(os.path.exists(snapshot_file))
        
        # Read the snapshot file
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the snapshot contains expected content
        self.assertIn('# Package Snapshot', content)
        self.assertIn('## Comments', content)
        self.assertIn('Test snapshot', content)
        self.assertIn('## Directory Structure', content)
        self.assertIn('## Table of Contents', content)
        self.assertIn('README.md', content)
        self.assertIn('src/main.py', content)
        self.assertIn('tests/test_main.py', content)
        
        # Check that the ignored file is not included
        self.assertNotIn('secret.txt', content)
        
        # Check that binary file is marked accordingly
        self.assertIn('binary.bin', content)
        self.assertIn('Binary file - contents not shown', content)

    # Patch the is_binary_file function for parse_snapshot_file test
    @patch('snapshot_pkg.snapshot.is_binary_file')
    def test_parse_snapshot_file(self, mock_is_binary):
        """Test parsing a snapshot file."""
        # Make the mock return True for binary.bin and False for others
        def side_effect(file_path):
            return os.path.basename(file_path) == 'binary.bin'
        mock_is_binary.side_effect = side_effect
        
        # First create a snapshot
        snapshot_file = create_snapshot(self.project_dir, self.output_dir, comment="Test snapshot")
        
        # Parse the snapshot file
        file_contents, comment = parse_snapshot_file(snapshot_file)
        
        # Check that the comment was extracted correctly
        self.assertEqual(comment, "Test snapshot")
        
        # Check that the file contents were extracted correctly
        self.assertIn('src/main.py', file_contents)
        self.assertIn('README.md', file_contents)
        self.assertIn('tests/test_main.py', file_contents)
        
        # Check specific file content
        self.assertIn('def hello():', file_contents['src/main.py'])
        self.assertIn('# Test Project', file_contents['README.md'])
        
        # Check binary file marker
        self.assertEqual(file_contents['binary.bin'], "[Binary file - contents not shown]")


class TestSnapshotRestoration(unittest.TestCase):
    """Test cases for snapshot restoration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create source and target directories
        self.source_dir = os.path.join(self.test_dir, 'source')
        self.target_dir = os.path.join(self.test_dir, 'target')
        self.output_dir = os.path.join(self.source_dir, 'snapshots')
        
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)
        os.makedirs(self.output_dir)
        
        # Create source project structure
        os.makedirs(os.path.join(self.source_dir, 'src'))
        
        # Create some files in source
        with open(os.path.join(self.source_dir, 'README.md'), 'w') as f:
            f.write('# Source Project\n\nThis is the source project.\n')
        
        with open(os.path.join(self.source_dir, 'src', 'main.py'), 'w') as f:
            f.write('def hello():\n    return "Hello from source!"\n')
        
        # Create a .gitignore file
        with open(os.path.join(self.source_dir, '.gitignore'), 'w') as f:
            f.write('*.pyc\n__pycache__/\n')
        
        # Mock the snapshot file content directly for restoration tests
        # NOTE: Using backticks (```) instead of prime characters (′′′) to match the actual implementation
        snapshot_content = """# Package Snapshot - Generated on 2025-03-02_15-00-00

## Comments
Source snapshot

## Directory Structure
```
📦 source
├─ 📂 src
│  └─ 🐍 main.py
└─ 📝 README.md
```

## Table of Contents
1. [README.md](#readmemd)
2. [src/main.py](#src-mainpy)

## Files

<a id="readmemd"></a>
### README.md
```markdown
# Source Project

This is the source project.
```

<a id="src-mainpy"></a>
### src/main.py
```python
def hello():
    return "Hello from source!"
```
"""
        self.snapshot_file = os.path.join(self.output_dir, 'test_snapshot.md')
        with open(self.snapshot_file, 'w', encoding='utf-8') as f:
            f.write(snapshot_content)

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_restore_from_snapshot(self):
        """Test restoring a project from a snapshot."""
        # Create a different structure in target to ensure it's properly restored
        with open(os.path.join(self.target_dir, 'existing.txt'), 'w') as f:
            f.write('This is an existing file in the target.\n')
        
        # Restore from the snapshot
        restore_from_snapshot(self.snapshot_file, self.target_dir, mode='overwrite', create_backup=False)
        
        # Check that files from the snapshot were restored
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'README.md')))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'src', 'main.py')))
        
        # Check file contents
        with open(os.path.join(self.target_dir, 'README.md'), 'r') as f:
            content = f.read()
            self.assertIn('# Source Project', content)
        
        with open(os.path.join(self.target_dir, 'src', 'main.py'), 'r') as f:
            content = f.read()
            self.assertIn('Hello from source', content)
        
        # Check that existing file still exists (restoration doesn't delete files)
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'existing.txt')))

    def test_selective_restore(self):
        """Test selective restoration from a snapshot."""
        # Create some structure in target
        os.makedirs(os.path.join(self.target_dir, 'src'), exist_ok=True)
        
        # Restore only the README.md file
        selective_restore(
            self.snapshot_file, 
            self.target_dir, 
            patterns=['README.md'], 
            exclude_patterns=None,
            interactive=False,
            mode='overwrite',
            create_backup=False
        )
        
        # Check that only README.md was restored
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'README.md')))
        self.assertFalse(os.path.exists(os.path.join(self.target_dir, 'src', 'main.py')))
        
        # Check file content
        with open(os.path.join(self.target_dir, 'README.md'), 'r') as f:
            content = f.read()
            self.assertIn('# Source Project', content)

    def test_safe_mode_restoration(self):
        """Test restoration with 'safe' mode that doesn't overwrite existing files."""
        # Create a file with different content in target
        os.makedirs(os.path.join(self.target_dir, 'src'), exist_ok=True)
        with open(os.path.join(self.target_dir, 'README.md'), 'w') as f:
            f.write('# Target Project\n\nThis should not be overwritten.\n')
        
        # Restore from snapshot in safe mode
        restore_from_snapshot(self.snapshot_file, self.target_dir, mode='safe', create_backup=False)
        
        # Check that existing file wasn't overwritten
        with open(os.path.join(self.target_dir, 'README.md'), 'r') as f:
            content = f.read()
            self.assertIn('# Target Project', content)
            self.assertNotIn('# Source Project', content)
        
        # But new file was created
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'src', 'main.py')))


class TestCLI(unittest.TestCase):
    """Test cases for the command-line interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create a simple project structure
        self.project_dir = os.path.join(self.test_dir, 'project')
        os.makedirs(os.path.join(self.project_dir, 'src'))
        
        # Create some files
        with open(os.path.join(self.project_dir, 'README.md'), 'w') as f:
            f.write('# Test Project\n')
        
        with open(os.path.join(self.project_dir, 'src', 'main.py'), 'w') as f:
            f.write('def hello():\n    return "Hello, world!"\n')

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.test_dir)

    # Fix: Use the correct module path
    @patch('snapshot_pkg.snapshot.create_snapshot')
    def test_handle_snapshot(self, mock_create_snapshot):
        """Test the snapshot command handler."""
        from snapshot_pkg.__main__ import handle_snapshot
        
        # Mock args
        args = MagicMock()
        args.start_path = self.project_dir
        args.output_folder = 'snapshots'
        args.message = 'Test snapshot'
        args.no_comment_prompt = True
        
        # Mock create_snapshot to return a path
        mock_create_snapshot.return_value = os.path.join(self.project_dir, 'snapshots', 'test_snapshot.md')
        
        # Call the handler
        result = handle_snapshot(args)
        
        # Check that create_snapshot was called with correct args
        mock_create_snapshot.assert_called_once_with(
            self.project_dir, 'snapshots', None, 'Test snapshot'
        )
        
        # Check return code
        self.assertEqual(result, 0)

    # Fix: Patch the correct module path
    @patch('snapshot_pkg.restore.restore_from_snapshot')
    @patch('snapshot_pkg.__main__.get_snapshot_path')
    def test_handle_restore(self, mock_get_snapshot_path, mock_restore):
        """Test the restore command handler."""
        from snapshot_pkg.__main__ import handle_restore
        
        # Mock args
        args = MagicMock()
        args.snapshot_file = 'snapshot.md'
        args.target_dir = self.test_dir
        args.mode = 'overwrite'
        args.no_backup = True
        args.backup_path = None
        args.patterns = None
        args.exclude_patterns = None
        args.interactive = False
        
        # Mock get_snapshot_path to return a path
        mock_get_snapshot_path.return_value = os.path.join(self.test_dir, 'snapshot.md')
        
        # Mock restore_from_snapshot to return a path
        mock_restore.return_value = None
        
        # Call the handler
        result = handle_restore(args)
        
        # Check that restore_from_snapshot was called with correct args
        mock_restore.assert_called_once_with(
            os.path.join(self.test_dir, 'snapshot.md'),
            self.test_dir,
            'overwrite',
            False,
            None
        )
        
        # Check return code
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()