#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path
import json


def create_concat_file(video_files, temp_dir):
    """Create a temporary file listing videos to concatenate."""
    concat_file_path = os.path.join(temp_dir, "concat_list.txt")

    with open(concat_file_path, "w") as f:
        for video_file in video_files:
            # Convert to absolute path and escape single quotes for ffmpeg
            abs_path = os.path.abspath(str(video_file))
            escaped_path = abs_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    return concat_file_path


def get_video_info(video_path):
    """Get duration and other info about the video file."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,duration,r_frame_rate",
        "-of",
        "json",  # Use JSON format for more reliable parsing
        str(video_path),
    ]

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        data = json.loads(output)

        # Extract video stream information
        stream = data["streams"][0]
        width = stream.get("width")
        height = stream.get("height")

        if not width or not height:
            raise ValueError(f"Could not get dimensions for {video_path}")

        # Get duration from format if not in stream
        duration = stream.get("duration")
        if not duration:
            duration_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(video_path),
            ]
            duration_data = json.loads(
                subprocess.check_output(duration_cmd).decode("utf-8")
            )
            duration = duration_data["format"]["duration"]

        return {"width": width, "height": height, "duration": float(duration)}
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
    ) as e:
        print(f"Error getting video info for {video_path}: {str(e)}")
        return None


def concatenate_videos(
    video_files,
    output_path,
    audio_file=None,
    normalize_resolution=False,
    brightness=50,
    contrast=50,
):
    """Concatenate multiple videos into one, optionally adding audio."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create concat file
        concat_file = create_concat_file(video_files, temp_dir)

        # Get dimensions of all videos
        video_info_list = [get_video_info(v) for v in video_files]
        if not all(video_info_list):
            raise ValueError("Could not get video information for all files")

        # Use the dimensions of the first video as the target
        target_width = int(video_info_list[0]["width"])
        target_height = int(video_info_list[0]["height"])

        # Build ffmpeg command
        cmd = ["ffmpeg", "-y"]

        # Add input files
        cmd.extend(["-f", "concat", "-safe", "0", "-i", concat_file])
        if audio_file:
            cmd.extend(["-i", str(audio_file)])

        # Calculate brightness and contrast values
        # Convert from 0-100 range to FFmpeg's expected ranges
        # Brightness: -1.0 to 1.0
        # Contrast: 0.0 to 2.0
        brightness_value = ((brightness - 50) / 50) * 1.0
        contrast_value = 1.0 + (contrast - 50) / 50

        # Build video filters
        filters = []
        if normalize_resolution:
            filters.append(
                f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
            )

        # Add brightness and contrast filters
        filters.append(
            f"eq=brightness={brightness_value}:contrast={contrast_value}"
        )

        # Combine all filters
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # Add output options with better quality settings
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",  # Enable fast start for web playback
            ]
        )

        # Add audio options if audio file is provided
        if audio_file:
            cmd.extend(
                [
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",  # Ensure video and audio lengths match
                ]
            )

        cmd.append(str(output_path))

        # Execute ffmpeg command with error handling
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Successfully created merged video: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            raise

    finally:
        # Clean up temporary files
        if os.path.exists(concat_file):
            os.remove(concat_file)
        os.rmdir(temp_dir)


def get_video_files_from_directory(directory):
    """Get all video files from a directory."""
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"}
    video_files = []

    try:
        for file in os.listdir(directory):
            if os.path.splitext(file)[1].lower() in video_extensions:
                video_files.append(os.path.join(directory, file))

        # Sort files to ensure consistent ordering
        video_files.sort()
        return video_files
    except Exception as e:
        print(f"Error reading directory {directory}: {e}")
        return []


def merge_videos_with_audio(
    video_dir,
    output_path,
    audio_file=None,
    normalize=True,
    brightness=50,
    contrast=50,
):
    """Merge all videos in a directory with optional audio file."""
    try:
        # Get all video files from the directory
        video_files = get_video_files_from_directory(video_dir)
        if not video_files:
            print("No video files found in directory")
            return False

        # Sort video files to ensure correct order
        video_files.sort()

        # Concatenate videos and add audio if provided
        concatenate_videos(
            video_files,
            output_path,
            audio_file=audio_file,
            normalize_resolution=normalize,
            brightness=brightness,
            contrast=contrast,
        )
        return True

    except Exception as e:
        print(f"Error merging videos: {str(e)}")
        return False


def get_most_recent_audio_file(directory):
    """Get the most recent audio file from a directory."""
    audio_extensions = {".mp3", ".wav"}
    audio_files = []

    try:
        for file in os.listdir(directory):
            if os.path.splitext(file)[1].lower() in audio_extensions:
                file_path = os.path.join(directory, file)
                audio_files.append((file_path, os.path.getmtime(file_path)))

        if not audio_files:
            return None

        # Sort by modification time, most recent first
        audio_files.sort(key=lambda x: x[1], reverse=True)
        return audio_files[0][0]
    except Exception as e:
        print(f"Error finding audio file: {e}")
        return None


def main():
    # Get the project root directory (2 levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # Use absolute paths
    video_dir = project_root / "assets" / "videos"
    output_path = project_root / "assets" / "output" / "output.mp4"
    audio_file = project_root / "assets" / "music" / "1743302325.6031349.mp3"

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Video directory: {video_dir}")
    print(f"Output path: {output_path}")
    print(f"Audio file: {audio_file}")

    merge_videos_with_audio(video_dir, output_path, audio_file, normalize=True)


if __name__ == "__main__":
    main()
