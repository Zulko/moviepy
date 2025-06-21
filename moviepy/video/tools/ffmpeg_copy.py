"""Module contains a function to copy a video file using ffmpeg without re-encoding.
This can be useful for fixing issues with corrupted video files.
"""

import subprocess
from pathlib import Path
from typing import Union

from moviepy.config import FFMPEG_BINARY


def ffmpeg_copy(input_file: Union[str, Path], output_file: Union[str, Path]):
    """
    Re-mix a video file using ffmpeg.
    This may fix issues with corrupted video file.

    Parameters
    ----------
    input_file : str or Path file that will be re-encoded
    output_file: str or Path path to save the re-encoded file

    Returns
    -------
    None
    """
    # Convert input and output files to Path objects
    input_path = Path(input_file).resolve()
    output_path = Path(output_file).resolve()

    # Check if the input file exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

    if output_path.exists():
        raise FileExistsError(f"Output file '{output_file}' already exists.")

    try:
        # Construct the ffmpeg command
        command = [
            FFMPEG_BINARY,
            "-i",
            str(input_path),
            "-c",
            "copy",  # Copy streams without re-encoding
            str(output_path),
        ]

        # Run the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise IOError(f"Error: ffmpeg command failed with error {e}") from e
