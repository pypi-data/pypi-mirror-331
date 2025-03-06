#  filesize-cli - Calculate file and directory sizes from the command line
#
#  Copyright (C) 2024-2025 Kolja Nolte <kolja.nolte@gmail.com>
#  https://www.kolja-nolte.com
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files to deal with the Software
#  without restriction, including without limitation the rights to use, copy,
#  modify, merge, publish, distribute, sublicense, and/or sell copies of the
#  Software, and to permit persons to whom the Software is furnished to do so.
#
#  THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
#
#  Author: Kolja Nolte
#  E-Mail: kolja.nolte@gmail.com
#  Website: https://www.kolja-nolte.com

# Import the os module for file and directory operations
import os

# Import pytest for testing framework functionality
import pytest

# Import the get_path_size function from the main module
from filesize_cli.main import get_path_size


# Define a fixture to create a temporary test file for use in tests
@pytest.fixture
def tmp_file(tmp_path):
	"""Create a temporary file"""

	# Create a file path using the pytest-provided temporary directory
	file = tmp_path / "test_file.txt"

	# Open the file in write mode and add test content
	with open(file, "w") as f:
		f.write("Test content")

	# Yield the file path to the test, making it available as a parameter
	yield file


# Define a fixture to create a temporary directory for testing
@pytest.fixture
def tmp_dir(tmp_path):
	"""Create a temporary directory"""

	# Create a directory path within the pytest-provided temporary directory
	directory = tmp_path / "test_dir"

	# Create the actual directory on the filesystem
	directory.mkdir()

	# Yield the directory path to the test
	yield directory


# Test function to verify file size calculation
def test_file_size(tmp_file):
	"""Test getting size of a file"""

	# Get the expected file size using os.path.getsize
	expected_size = os.path.getsize(tmp_file)

	# Assert that our function returns the same size as the os.path.getsize function
	assert get_path_size(tmp_file) == expected_size

	# Verify the returned value is an integer
	assert isinstance(get_path_size(tmp_file), int)


# Test function to verify directory size calculation
def test_directory_size(tmp_dir, tmp_file):
	"""Test getting size of a directory"""

	# Create a first file inside the test directory
	file_in_dir = tmp_dir / "file.txt"

	# Write content to the first file
	with open(file_in_dir, "w") as f:
		f.write("Content")

	# Create a second file inside the test directory
	file2 = tmp_dir / "file2.txt"

	# Write content to the second file
	with open(file2, "w") as f:
		f.write("More content")

	# Calculate the expected total size by adding the sizes of both files
	expected_size = os.path.getsize(file_in_dir) + os.path.getsize(file2)

	# Get the directory size using our function
	dir_size = get_path_size(tmp_dir)

	# Verify the calculated size matches our expected size
	assert dir_size == expected_size

	# Verify the returned size is an integer
	assert isinstance(dir_size, int)


# Test function to verify error handling for non-existent paths
def test_non_existent_path(caplog):
	"""Test handling of non-existent file/directory"""

	# Use pytest.raises to catch the SystemExit exception that should be raised
	with pytest.raises(SystemExit) as exit_info:
		get_path_size("non_existent_path")

	# Verify that the function exited with an error
	assert exit_info.type == SystemExit

	# Verify that the appropriate error message was logged
	assert "Invalid path: non_existent_path" in caplog.text


# Test function to verify handling of nested directory structures
def test_directory_with_subdirectories(tmp_dir):
	"""Test directory with nested subdirectories and files"""

	# Create a subdirectory within the test directory
	sub_dir = tmp_dir / "subdir"

	# Make the subdirectory
	sub_dir.mkdir()

	# Create a file in the subdirectory
	file1 = sub_dir / "file1.txt"

	# Write content to the file in the subdirectory
	with open(file1, "w") as f:
		f.write("Subdir file")

	# Create a file in the root test directory
	file2 = tmp_dir / "file2.txt"

	# Write content to the file in the root directory
	with open(file2, "w") as f:
		f.write("Root file")

	# Calculate the expected size by adding both file sizes
	expected_size = os.path.getsize(file1) + os.path.getsize(file2)

	# Verify our function returns the correct total size
	assert get_path_size(tmp_dir) == expected_size


# Test function to verify symbolic link handling
def test_symlink(tmp_path):
	"""Test handling of symbolic links"""

	# Create a target file for the symlink
	file = tmp_path / "target.txt"

	# Write content to the target file
	with open(file, "w") as f:
		f.write("Target content")

	# Create a path for the symbolic link
	symlink = tmp_path / "symlink"

	# Create a symbolic link pointing to the target file
	os.symlink(file, symlink)

	# Get the size of the symlink (should return the target file size)
	size = get_path_size(symlink)

	# Verify the result is an integer
	assert isinstance(size, int)

	# Verify the size is greater than zero
	assert size > 0


# Test function to verify empty directory handling
def test_empty_directory(tmp_dir):
	"""Test empty directory"""

	# Verify that an empty directory returns a size of 0
	assert get_path_size(tmp_dir) == 0


# Test function to verify zero-byte file handling
def test_zero_byte_file(tmp_path):
	"""Test file with zero bytes"""

	# Create a path for a zero-byte file
	file = tmp_path / "zero_byte.txt"

	# Create the file without writing any content
	open(file, "a").close()

	# Verify that a zero-byte file returns a size of 0
	assert get_path_size(file) == 0
