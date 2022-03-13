"""Script to remove duplicate files."""

from pathlib import Path
import argparse
from argparse import RawTextHelpFormatter
from typing import List

ARG_DESC = """
Remove duplicate files ending with suffix, including the extension. For exmaple, if these two files are detected:
Asad Rivzi, Bushwacka! - Dual - Bushwacka! Remix 1.mp3
Asad Rivzi, Bushwacka! - Dual - Bushwacka! Remix.mp3
and specified argument is " 1.mp3" then this script will remove
Asad Rivzi, Bushwacka! - Dual - Bushwacka! Remix 1.mp3

add -o flag to remove the other file instead
"""


def retrieve_files(
    current_path: Path, suffix: str, recursive: bool = False
) -> List[Path]:
    """Retrieve all files matching the suffix."""
    found_files = list(current_path.glob(suffix))

    subdirectories = [i for i in current_path.iterdir() if i.is_dir()]
    if recursive:
        for subdirectory in subdirectories:
            found_files.extend(retrieve_files(subdirectory, suffix, recursive))

    # Remove directories
    found_files = [i for i in found_files if not i.is_dir()]
    return found_files


def get_files_without_extension(files: Path) -> List[str]:
    """Return a list of filenames that don't include the file extension."""
    files_without_extension = []
    for file_path in files:
        file_path_str = file_path.absolute().as_posix()
        index_of_file_ext_start = file_path_str.rfind(".")
        files_without_extension.append(file_path_str[:index_of_file_ext_start])

    return files_without_extension


# Initialize parser
parser = argparse.ArgumentParser(
    description=ARG_DESC, formatter_class=RawTextHelpFormatter
)

# Add positional args
parser.add_argument(
    "path", help="path where the script should look for files", type=str
)
parser.add_argument(
    "suffix",
    help='suffix of the filename which will be removed, including extension e.g. " 1.mp3"',
    type=str,
)

# Add optional args
# action="store_true" means that it doesn't take any arguments itself, turning it into a boolean
parser.add_argument(
    "-o",
    "--opposite",
    help="remove the other file instead of the one with the suffix",
    action="store_true",
)
parser.add_argument(
    "-r",
    "--recursive",
    help="include files from subdirectories too",
    action="store_true",
)
args = parser.parse_args()

# Access current folder
current_path = Path(args.path)

suffixed_files = retrieve_files(current_path, args.suffix, args.recursive)
all_files = retrieve_files(current_path, "*", args.recursive)
all_files_without_extension = get_files_without_extension(all_files)

suffix_without_stars = args.suffix.replace("*", "")
# Remove suffix and check if a duplicate file exists
for suffixed_file in suffixed_files:
    filename_with_suffix = suffixed_file.absolute().as_posix()
    print(f"Checking if this file has a similarly named file{filename_with_suffix}")
    filename_without_suffix = filename_with_suffix[: -(len(suffix_without_stars))]
    if filename_without_suffix in all_files_without_extension:
        file_to_remove = suffixed_file
        if args.opposite:
            other_file_index = all_files_without_extension.index(
                filename_without_suffix
            )
            file_to_remove = all_files[other_file_index]

            # Don't remove if the file matches itself
            if file_to_remove.absolute().as_posix() == suffixed_file.absolute().as_posix():
                continue

        print(f"Removed file {file_to_remove}")
        file_to_remove.unlink()
