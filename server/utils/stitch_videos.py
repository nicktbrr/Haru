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

        # First concatenate videos without fades
        temp_concat = os.path.join(temp_dir, "temp_concat.mp4")
        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            temp_concat
        ]

        try:
            subprocess.run(concat_cmd, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error concatenating videos: {e.stderr.decode('utf-8')}")
            return False

        # Get duration of concatenated video
        video_info = get_video_info(temp_concat)
        if not video_info:
            return False

        duration = video_info['duration']
        fade_duration = 1.0  # 1 second fade

        # Apply fade in and fade out
        fade_cmd = [
            'ffmpeg', '-y',
            '-i', temp_concat,
            '-vf', f'fade=t=in:st=0:d={fade_duration},fade=t=out:st={duration-fade_duration}:d={fade_duration}',
            '-c:a', 'copy'
        ]

        # If audio file is provided
        if audio_file and os.path.exists(audio_file):
            # First apply fades to video
            temp_faded = os.path.join(temp_dir, "temp_faded.mp4")
            try:
                subprocess.run(fade_cmd + [temp_faded],
                               check=True, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                print(f"Error applying fades: {e.stderr.decode('utf-8')}")
                return False

            # Then add audio
            audio_cmd = [
                'ffmpeg', '-y',
                '-i', temp_faded,
                '-i', audio_file,
                '-filter_complex', f"[1:a]atrim=0:{duration},asetpts=PTS-STARTPTS[a]",
                '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac',
                output_path
            ]

            try:
                subprocess.run(audio_cmd, check=True, stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error adding audio: {e.stderr.decode('utf-8')}")
                return False
        else:
            # Just apply fades without audio
            try:
                subprocess.run(fade_cmd + [output_path],
                               check=True, stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error applying fades: {e.stderr.decode('utf-8')}")
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


def merge_videos_with_audio(video_dir, output_path, audio_file=None, normalize=True):
    """
    Merge all videos in a directory with optional audio and normalization.

    Args:
        video_dir (str): Directory containing video files
        output_path (str): Path where the final video will be saved
        audio_file (str, optional): Path to audio file to add to the video
        normalize (bool): Whether to normalize video resolutions

    Returns:
        bool: True if successful, False otherwise
    """
    video_dir = Path(video_dir).resolve()
    output_path = Path(output_path).resolve()
    audio_file = Path(audio_file).resolve() if audio_file else None

    # Validate input directory
    if not video_dir.exists() or not video_dir.is_dir():
        print(
            f"Error: Video directory '{video_dir}' does not exist or is not a directory")
        return False

    # Get video files from directory
    video_files = get_video_files_from_directory(video_dir)
    if not video_files:
        print(f"Error: No video files found in directory '{video_dir}'")
        return False

    if audio_file and not audio_file.exists():
        print(f"Warning: Audio file '{audio_file}' does not exist")
        audio_file = None

    # Create output directory if it doesn't exist
    output_dir = output_path.parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Perform concatenation with all features
    print("Starting video processing...")
    if concatenate_videos(video_files, output_path, audio_file, normalize):
        print(f"Successfully created merged video: {output_path}")
        return True
    else:
        print("Video processing failed")
        return False


def main():
    # Example usage of the new method
    video_dir = Path('assets/videos')
    output_path = Path('output.mp4')
    audio_file = Path('assets/music/1743286897.723132.mp3')

    merge_videos_with_audio(video_dir, output_path, audio_file, normalize=True)


if __name__ == "__main__":
    main()
