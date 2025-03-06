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

# Import the os module to interact with the operating system (file paths, sizes, etc.)
import os

# Import the sys module for system-level operations (like exiting the program)
import sys

# Import logging module to handle informational and error messages
import logging

# Import argument parsing classes to handle command-line arguments
from argparse import ArgumentParser, ArgumentTypeError

# Import Enum class to create enumeration of file size units
from enum import Enum
from pathlib import Path

# Import typing classes for type hints
from typing import List, Tuple

# Configure the basic logging settings for the application
# Sets warning level as default, formats messages, and directs output to console
logging.basicConfig(
	level=logging.WARNING,
	format="%(levelname)s: %(message)s",
	handlers=[logging.StreamHandler()]
)


# Define an enumeration class for different file size units
class FileSizeUnit(Enum):
	# Define constants for bytes unit
	BYTES = 'B'

	# Define constants for kilobytes unit
	KILOBYTES = 'KB'

	# Define constants for megabytes unit
	MEGABYTES = 'MB'

	# Define constants for gigabytes unit
	GIGABYTES = 'GB'

	# Define constants for terabytes unit
	TERABYTES = 'TB'

	# Define a class method to convert string input to a FileSizeUnit enum value
	@classmethod
	def from_string(cls, value: str) -> 'FileSizeUnit':
		# Convert input string to uppercase for case-insensitive comparison
		value_upper = value.upper()

		# Iterate through all enum members to find matching value
		for unit in cls:
			# Check if the enum value matches the provided string
			if unit.value == value_upper:
				# Return the matching enum member
				return unit

		# Raise an error if no matching unit is found
		raise ValueError(f"Invalid unit: {value}")


# Define a function to validate that an argument is a positive integer
def positive_int(value: str) -> int:
	# Convert the string value to an integer
	ivalue = int(value)

	# Check if the integer is positive
	if ivalue <= 0:
		# Raise an error if the value is not positive
		raise ArgumentTypeError(f"Must be a positive integer, got {value}")

	# Return the validated integer
	return ivalue


# Define a function to calculate the total size of a file or directory
def get_path_size(path: str | Path) -> float:
	# Check if the path is a file
	if os.path.isfile(path):
		# Try to get the size of the file
		try:
			# Return the file size in bytes
			return os.path.getsize(path)

		# Handle potential errors when accessing the file
		except (FileNotFoundError, PermissionError, OSError) as e:
			# Log the error with details
			logging.error(f"Access error: {path} - {e}")

			# Exit the program with an error code
			sys.exit(1)

	# Check if the path is a directory
	if os.path.isdir(path):
		# Initialize total size counter
		total = 0

		# Try to walk through the directory tree
		try:
			# Recursively walk through all directories and files
			for root, _, files in os.walk(path, followlinks=False):
				# Process each file in the current directory
				for file in files:
					# Construct the full file path
					file_path = os.path.join(root, file)

					# Try to get the file size
					try:
						# Check if the path is actually a file (not a symlink or special file)
						if os.path.isfile(file_path):
							# Add the file size to the total
							# noinspection PyUnresolvedReferences
							total += os.path.getsize(file_path)

						# Handle non-file items
						else:
							# Log a warning for non-file items
							logging.warning(f"Skipped non-file: {file_path}")

					# Handle errors when accessing individual files
					except OSError as e:
						# Log a warning and continue processing other files
						logging.warning(f"Skipped {file_path} - {e}")

		# Handle errors when accessing the directory
		except OSError as e:
			# Log the error with details
			logging.error(f"Directory access error: {path} - {e}")

			# Exit the program with an error code
			sys.exit(1)

		# Return the total size of the directory
		return total

	# Handle invalid paths (neither file nor directory)
	logging.error(f"Invalid path: {path}")

	# Exit the program with an error code
	sys.exit(1)


# Define a function to automatically select the most appropriate unit based on size
def auto_select_unit(size_bytes: float, rate: int) -> FileSizeUnit:
	# Define thresholds for each unit with their corresponding exponents
	thresholds: List[Tuple[FileSizeUnit, int]] = [
		(FileSizeUnit.TERABYTES, 4),
		(FileSizeUnit.GIGABYTES, 3),
		(FileSizeUnit.MEGABYTES, 2),
		(FileSizeUnit.KILOBYTES, 1),
		(FileSizeUnit.BYTES, 0)
	]

	# Check each threshold from largest to smallest
	for unit, exponent in thresholds:
		# If the size is greater than or equal to the threshold, use this unit
		if size_bytes >= (rate ** exponent):
			# Return the selected unit
			return unit

	# Default to bytes for very small sizes
	return FileSizeUnit.BYTES


# Define a function to format the size with appropriate units
def format_size(size_bytes: float, unit: FileSizeUnit, rate: int, quiet: bool = False) -> str:
	# Define exponents for each unit to calculate the divisor
	exponents = {
		FileSizeUnit.BYTES:     0,
		FileSizeUnit.KILOBYTES: 1,
		FileSizeUnit.MEGABYTES: 2,
		FileSizeUnit.GIGABYTES: 3,
		FileSizeUnit.TERABYTES: 4
	}

	# Calculate the divisor based on the selected unit and rate
	divisor = rate ** exponents[unit]

	# Calculate the size in the selected unit
	value = size_bytes / divisor

	# If quiet mode is enabled, omit the unit from the output
	if quiet:
		# Format bytes as integers (no decimal places)
		if unit == FileSizeUnit.BYTES:
			return f"{int(value)}"
		# Format other units with two decimal places
		return f"{value:.2f}"

	# When not in quiet mode, include the unit in the output
	# Format bytes as integers (no decimal places)
	if unit == FileSizeUnit.BYTES:
		# Return formatted byte size as an integer
		return f"{int(value)} {unit.value}"

	# Format other units with two decimal places
	return f"{value:.2f} {unit.value}"


# Define the main function of the program
def main() -> None:
	# Create an argument parser with a description
	parser = ArgumentParser(description="Calculate file/directory sizes")

	# Add argument for target paths (one or more required)
	parser.add_argument(
		'paths',
		nargs='+',
		help="Target paths to analyze"
	)

	# Add optional argument for unit selection
	parser.add_argument(
		'-u',
		'--unit', type=FileSizeUnit.from_string,
		default=FileSizeUnit.MEGABYTES,
		help="Size unit (B, KB, MB, GB, TB)"
	)

	# Add optional argument for conversion rate between units
	parser.add_argument(
		'-r',
		'--rate',
		type=positive_int,
		default=1000,
		help="Conversion rate between units"
	)

	# Add optional flag for verbose output
	parser.add_argument(
		'-v',
		'--verbose',
		action='store_true',
		help="Enable verbose logging"
	)

	# Add optional flag for quiet output (size only)
	parser.add_argument(
		'-q',
		'--quiet',
		action='store_true',
		help="Only display the filesize"
	)

	# Parse the command line arguments
	args = parser.parse_args()

	# If verbose mode is enabled, increase logging level
	if args.verbose:
		# Set logging level to INFO to show more detailed messages
		logging.getLogger().setLevel(logging.INFO)

	# Check if unit was explicitly specified in command line args
	unit_specified = any(arg in sys.argv for arg in ['-u', '--unit'])

	# Try to calculate and display the size
	try:
		# Calculate the total size of all specified paths
		total = sum(get_path_size(p) for p in args.paths)

		# Determine which unit to use for display
		if unit_specified:
			# Use the explicitly specified unit
			unit = args.unit
		else:
			# Automatically select the most appropriate unit
			unit = auto_select_unit(total, args.rate)

			# Log the total size in the selected unit
			logging.info(f"Total size: {format_size(total, unit, args.rate)}")

		# Print the formatted size
		print(format_size(total, unit, args.rate, args.quiet))

	# Handle any unexpected errors
	except Exception as e:
		# Log the error with details
		logging.error(f"Unexpected error: {e}")

		# Exit the program with an error code
		sys.exit(1)


# Check if this file is being run directly (not imported)
if __name__ == '__main__':
	# Execute the main function
	main()
