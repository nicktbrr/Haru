#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path


def create_concat_file(video_files, temp_dir):
    """Create a temporary file listing videos to concatenate."""
    concat_file_path = os.path.join(temp_dir, "concat_list.txt")

    with open(concat_file_path, 'w') as f:
        for video_file in video_files:
            # Convert to absolute path and escape single quotes for ffmpeg
            abs_path = os.path.abspath(str(video_file))
            escaped_path = abs_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    return concat_file_path


def get_video_info(video_path):
    """Get duration and other info about the video file."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration,r_frame_rate',
        '-of', 'csv=p=0',
        str(video_path)
    ]

    try:
        output = subprocess.check_output(
            cmd).decode('utf-8').strip().split(',')
        width, height = output[0], output[1]

        # Handle different duration formats
        try:
            duration = float(output[2])
        except ValueError:
            # If duration is not available, try alternative method
            alt_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                str(video_path)
            ]
            duration = float(subprocess.check_output(
                alt_cmd).decode('utf-8').strip())

        return {
            'width': width,
            'height': height,
            'duration': duration
        }
    except (subprocess.CalledProcessError, IndexError):
        print(f"Error: Could not get information for {video_path}")
        return None


def concatenate_videos(video_files, output_path, audio_file=None, normalize_resolution=False):
    """Concatenate videos and optionally add audio."""
    if not video_files:
        print("Error: No video files provided")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a concat file listing all videos
        concat_file = create_concat_file(video_files, temp_dir)

        # Get info of first video to use as reference if normalizing
        if normalize_resolution and len(video_files) > 1:
            video_info = get_video_info(video_files[0])
            if video_info:
                target_width = video_info['width']
                target_height = video_info['height']

                # Create normalized versions of all videos
                normalized_videos = []
                for i, video_file in enumerate(video_files):
                    normalized_path = os.path.join(
                        temp_dir, f"normalized_{i}.mp4")
                    cmd = [
                        'ffmpeg', '-y', '-i', str(video_file),
                        '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2',
                        '-c:v', 'libx264', '-c:a', 'aac',
                        normalized_path
                    ]

                    try:
                        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
                        normalized_videos.append(normalized_path)
                    except subprocess.CalledProcessError as e:
                        print(
                            f"Error normalizing video {video_file}: {e.stderr.decode('utf-8')}")
                        return False

                # Create new concat file with normalized videos
                video_files = normalized_videos
                concat_file = create_concat_file(video_files, temp_dir)

        # Basic concatenation command
        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy'
        ]

        # If audio file is provided
        if audio_file:
            if os.path.exists(audio_file):
                # First, create concatenated video without audio
                temp_output = os.path.join(temp_dir, "temp_concat.mp4")
                temp_cmd = concat_cmd + [temp_output]

                try:
                    subprocess.run(temp_cmd, check=True,
                                   stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    print(
                        f"Error concatenating videos: {e.stderr.decode('utf-8')}")
                    return False

                # Get duration of concatenated video
                video_info = get_video_info(temp_output)
                if not video_info:
                    return False

                # Command to add audio and trim it to match video duration
                audio_cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_output,
                    '-i', audio_file,
                    '-filter_complex', f"[1:a]atrim=0:{video_info['duration']},asetpts=PTS-STARTPTS[a]",
                    '-map', '0:v', '-map', '[a]',
                    '-c:v', 'copy', '-c:a', 'aac',
                    output_path
                ]

                try:
                    subprocess.run(audio_cmd, check=True,
                                   stderr=subprocess.PIPE)
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error adding audio: {e.stderr.decode('utf-8')}")
                    return False
            else:
                print(
                    f"Warning: Audio file '{audio_file}' not found. Continuing without audio.")
                # Continue with concatenation only

        # If no audio or audio file doesn't exist, just concatenate
        final_cmd = concat_cmd + [output_path]
        try:
            subprocess.run(final_cmd, check=True, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error concatenating videos: {e.stderr.decode('utf-8')}")
            return False


def get_video_files_from_directory(directory):
    """Get all video files from a directory."""
    video_extensions = {'.mp4', '.mov', '.avi',
                        '.mkv', '.wmv', '.flv', '.webm'}
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


def main():
    # Hardcoded paths for testing
    video_dir = Path('assets/videos')
    output_path = Path('output.mp4')
    audio_file = Path('assets/music/1743286897.723132.mp3')
    normalize = False  # Set to True if you want to normalize video resolutions

    # Convert to absolute paths
    video_dir = video_dir.resolve()
    output_path = output_path.resolve()
    audio_file = audio_file.resolve() if audio_file else None

    # Validate input directory
    if not video_dir.exists() or not video_dir.is_dir():
        print(
            f"Error: Video directory '{video_dir}' does not exist or is not a directory")
        sys.exit(1)

    # Get video files from directory
    video_files = get_video_files_from_directory(video_dir)
    if not video_files:
        print(f"Error: No video files found in directory '{video_dir}'")
        sys.exit(1)

    if audio_file and not audio_file.exists():
        print(f"Warning: Audio file '{audio_file}' does not exist")

    # Create output directory if it doesn't exist
    output_dir = output_path.parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Perform concatenation
    print("Starting video concatenation...")
    if concatenate_videos(video_files, output_path, audio_file, normalize):
        print(f"Successfully created concatenated video: {output_path}")
    else:
        print("Video concatenation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
