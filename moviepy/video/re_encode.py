"""Module contains a function to re-encode a video file using ffmpeg."""

import subprocess
from pathlib import Path


def reencode_video(input_file: str | Path, output_file: str | Path):
    """
    Re-encode a video file using ffmpeg.
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
            "ffmpeg",
            "-i",
            str(input_path),
            "-c",
            "copy",  # Copy audio without re-encoding
            str(output_path),
        ]

        # Run the command
        proc = subprocess.run(command, check=True)
        proc.check_returncode()
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg command failed with error {e}")
