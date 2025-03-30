import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional, List, Tuple
import base64
import speech_recognition as sr
from pydub import AudioSegment
import time
from datetime import datetime, timedelta
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import threading
import pygame
from playsound import playsound
import wave
import pyaudio
import subprocess

# Load environment variables
load_dotenv()

# Initialize pygame mixer with specific settings
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

class LyricsDisplay(QMainWindow):
    def __init__(self, video_path: str, audio_path: str, word_timestamps: List[Tuple[str, float]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lyrics Display")
        self.setGeometry(100, 100, 854, 480)  # YouTube size
        
        # Store timestamps and initialize index
        self.word_timestamps = word_timestamps
        self.current_word_index = 0
        self.start_time = None  # Will be set when playback starts
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create video display label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.fallback_frame = np.zeros((768, 1024, 3), dtype=np.uint8)
            self.video_fps = 30
        else:
            self.fallback_frame = None
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30

        # Initialize audio separately
        try:
            pygame.mixer.music.load(audio_path)  # Load audio file instead of video
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error loading audio: {e}")
        pygame.mixer.music.load(video_path)
        pygame.mixer.music.play()

        # Create timer for video playback
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / self.video_fps))
    
    def update_frame(self):
        # Read frame with error handling
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                # Create blank frame if video read fails
                frame = np.zeros((480, 854, 3), dtype=np.uint8)
        
        # Check if frame is valid before processing
        if frame is not None and frame.size > 0:
            # Resize frame to YouTube size
            frame = cv2.resize(frame, (854, 480))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            # Create blank frame if frame is invalid
            frame_rgb = np.zeros((480, 854, 3), dtype=np.uint8)
        
        # Initialize start_time on first frame
        if self.start_time is None:
            self.start_time = time.time()
        
        # Get current playback time
        current_time = time.time() - self.start_time
        
        # Draw text lines
        height = frame_rgb.shape[0]
        start_y = height - 100
        line_spacing = 40
        
        # Find current words to display
        current_words = []
        for word, timestamp in self.word_timestamps:
            if timestamp <= current_time <= timestamp + 1.0:
                current_words.append(word)
        
        # Display current words
        if current_words:
            text = " ".join(current_words)
            frame_rgb = self.draw_text_on_frame(frame_rgb, text, start_y, 0.9)
        
        # Convert to QImage and display
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))
    
    def draw_text_on_frame(self, frame, text, y_position, size=1.0):  # Reduced default text size
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (255, 255, 255)  # White text
        
        text_size = cv2.getTextSize(text, font, size, 2)[0]
        x_position = (width - text_size[0]) // 2
        
        # Draw text with thicker weight for better visibility
        cv2.putText(frame, text, (x_position, y_position), font, size, color, 2, cv2.LINE_AA)
        return frame
    
    def closeEvent(self, event):
        self.cap.release()
        pygame.mixer.quit()
        event.accept()

class LyricsGenerator:
    def __init__(self):
        # Get configuration from environment variables
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL_NAME', 'gemini-1.5-flash-001')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()

    def get_word_timestamps(self, audio_path: str, lyrics: str) -> List[Tuple[str, float]]:
        """
        Get timestamps with better audio sync
        """
        try:
            words = lyrics.split()
            word_timestamps = []
            current_time = 0.0  # Start from beginning
            
            for i, word in enumerate(words):
                # More natural timing based on word length and punctuation
                if i > 0:
                    if words[i-1][-1] in '.!?':  # End of sentence
                        current_time += 2.0  # Longer pause after sentences
                    elif words[i-1][-1] == ',':  # Comma
                        current_time += 1.0  # Medium pause after commas
                    elif len(word) > 6:  # Longer words
                        current_time += 0.8  # Longer pause for longer words
                    else:  # Normal words
                        current_time += 0.6  # Base timing for normal words
                
                word_timestamps.append((word, current_time))
            
            return word_timestamps
            
        except Exception as e:
            print(f"Error creating word timestamps: {str(e)}")
            return []

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio from a local file path
        
        Args:
            audio_path: Path to the local audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Read the audio file and encode it as base64
            with open(audio_path, 'rb') as audio_file:
                audio_content = audio_file.read()
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')

# Prepare audio data
            part = {
                "mime_type": "audio/mp3",
                "data": audio_base64
            }

            # Generate transcription with a more specific prompt
            response = self.model.generate_content([
                "Please provide a clean, professional transcription of this song's lyrics. Focus on accuracy and clarity.",
                part
            ])

            # Handle safety ratings and response
            try:
                return response.text
            except AttributeError:
                # If response.text fails, try getting content directly
                if response.candidates:
                    return response.candidates[0].content.text
                return None
            
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None

    def generate_lyrics(self, transcription: str) -> Optional[str]:
        """
        Generate lyrics from transcribed text
        
        Args:
            transcription: Transcribed text from audio
            
        Returns:
            Generated lyrics or None if generation fails
        """
        try:
            # Generate lyrics
            response = self.model.generate_content(
                f"Generate song lyrics based on this transcription: {transcription}"
            )
            
            if response.text:
                return response.text
            return None
            
        except Exception as e:
            print(f"Error generating lyrics: {str(e)}")
            return None

    def display_synchronized_lyrics(self, word_timestamps: List[Tuple[str, float]]):
        """
        Display lyrics synchronized with the audio
        
        Args:
            word_timestamps: List of tuples containing (word, timestamp)
        """
        try:
            start_time = time.time()
            current_word_index = 0
            
            while current_word_index < len(word_timestamps):
                current_time = time.time() - start_time
                word, timestamp = word_timestamps[current_word_index]
                
                if current_time >= timestamp:
                    print(word, end=' ', flush=True)
                    current_word_index += 1
                
                time.sleep(0.1)  # Small delay to prevent CPU overuse
                
            print()  # New line at the end
            
        except Exception as e:
            print(f"Error displaying synchronized lyrics: {str(e)}")

class AudioPlayer:
    def __init__(self):
        self.audio_file = None
        
    def convert_to_wav(self, input_file):
        """Convert audio file to WAV format"""
        try:
            output_file = "converted_audio.wav"
            audio = AudioSegment.from_file(input_file)
            audio.export(output_file, format="wav")
            return output_file
        except Exception as e:
            print(f"Conversion error: {e}")
            return None

    def play_with_pyaudio(self, filename):
        """Play audio using PyAudio"""
        try:
            wf = wave.open(filename, 'rb')
            p = pyaudio.PyAudio()
            
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                          channels=wf.getnchannels(),
                          rate=wf.getframerate(),
                          output=True)
            
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
        except Exception as e:
            print(f"PyAudio playback error: {e}")
            return False

    def play_with_pygame(self, filename):
        """Play audio using Pygame"""
        try:
            pygame.mixer.quit()  # Reset mixer
            pygame.mixer.init(frequency=44100)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            return True
        except Exception as e:
            print(f"Pygame playback error: {e}")
            return False

    def play_audio(self, input_file):
        """Main method to play audio"""
        # First, convert the file to WAV if it's not already
        if not input_file.lower().endswith('.wav'):
            wav_file = self.convert_to_wav(input_file)
            if wav_file is None:
                print("Failed to convert audio file")
                return False
        else:
            wav_file = input_file

        # Try PyAudio first
        if self.play_with_pyaudio(wav_file):
            return True
            
        # If PyAudio fails, try Pygame
        if self.play_with_pygame(wav_file):
            return True
            
        print("All playback methods failed")
        return False

class VideoGenerator:
    def __init__(self, video_path, audio_path, word_timestamps):
        self.video_path = video_path
        self.audio_path = audio_path
        self.word_timestamps = word_timestamps
        self.current_sentence = ""
        
    def get_sentence_for_time(self, current_time):
        # Group words into sentences
        current_words = []
        for word, timestamp in self.word_timestamps:
            # Show each word for 3 seconds and add a small overlap
            if timestamp <= current_time <= timestamp + 3.0:
                current_words.append(word)
        
        # Join words into a sentence
        if current_words:
            self.current_sentence = " ".join(current_words)
        return self.current_sentence

    def create_video(self, output_path="final_video.mp4"):
        print("Starting video generation...")
        
        try:
            # Open the video
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                print("Error: Could not open video file")
                return False
                
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video properties: {width}x{height} @ {fps}fps")
            
            # Create temporary video file
            temp_video = "temp_video.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
            if not out.isOpened():
                print("Error: Could not create output video file")
                return False
            
            # Start time
            start_time = time.time()
            frame_count = 0
            last_progress_time = time.time()
            
            print("Processing frames...")
            while True:  # Loop indefinitely
                ret, frame = cap.read()
                if not ret:
                    # Reset video to beginning when it ends
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret:
                        break
                
                # Calculate current time
                current_time = time.time() - start_time
                
                # Get current sentence
                current_sentence = self.get_sentence_for_time(current_time)
                
                # Add text to frame
                if current_sentence:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 2
                    font_thickness = 2
                    text_size = cv2.getTextSize(current_sentence, font, font_scale, font_thickness)[0]
                    
                    # Position text at bottom center
                    text_x = (width - text_size[0]) // 2
                    text_y = height - 50  # 50 pixels from bottom
                    
                    # Add black outline/shadow
                    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                        cv2.putText(frame, current_sentence, 
                                  (text_x + dx, text_y + dy),
                                  font, font_scale, (0,0,0), 
                                  font_thickness + 1)
                    
                    # Add white text
                    cv2.putText(frame, current_sentence,
                              (text_x, text_y),
                              font, font_scale, (255,255,255),
                              font_thickness)
                
                # Write the frame
                out.write(frame)
                
                # Update progress
                frame_count += 1
                if time.time() - last_progress_time > 1.0:  # Update every second
                    print(f"Processed {frame_count} frames...")
                    last_progress_time = time.time()
                
                # Check for timeout (5 minutes)
                if time.time() - start_time > 300:  # 5 minutes timeout
                    print("Warning: Video generation timed out after 5 minutes")
                    break
            
            print("Finished processing frames")
            
            # Release everything
            cap.release()
            out.release()
            
            print("Combining video and audio...")
            # Combine video and audio using FFmpeg
            try:
                command = [
                    'ffmpeg',
                    '-i', temp_video,
                    '-i', self.audio_path,
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    output_path
                ]
                subprocess.run(command, check=True)
                
                # Remove temporary file
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                    
                print("Video generation completed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error combining video and audio: {e}")
                return False
                
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return False

def combine_video_audio(video_path, audio_path, output_path):
    """Combine video and audio using FFmpeg"""
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',  # Use H.264 codec
            '-preset', 'medium',  # Balance between speed and quality
            '-c:a', 'aac',
            '-b:a', '192k',  # Audio bitrate
            output_path
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error combining video and audio: {e}")
        return False

def main():
    # Example usage
    try:
        generator = LyricsGenerator()
        
        # Get audio path from environment or use a default
        audio_path = os.getenv('AUDIO_PATH')
        if not audio_path:
            # Default to the music directory
            audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'music')
            print(f"Please specify the audio file path in the AUDIO_PATH environment variable")
            print(f"Or place your audio file in: {audio_path}")
            return
            
        # Check if the file exists
        if not os.path.exists(audio_path):
            print(f"Audio file not found at: {audio_path}")
            return
            
        # Transcribe audio
        transcription = generator.transcribe_audio(audio_path)
        if not transcription:
            print("Failed to transcribe audio")
            return
            
        print("Transcription:", transcription)
        
        # Generate lyrics
        lyrics = generator.generate_lyrics(transcription)
        if not lyrics:
            print("Failed to generate lyrics")
            return
            
        print("\nGenerated Lyrics:")
        print(lyrics)
        
        # Get word timestamps
        print("\nGetting word timestamps...")
        word_timestamps = generator.get_word_timestamps(audio_path, lyrics)
        
        if word_timestamps:
            # Get video path from environment or use a default
            video_path = os.getenv('VIDEO_PATH')
            if not video_path:
                # Default to the videos directory
                video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'videos')
                print(f"Please specify the video file path in the VIDEO_PATH environment variable")
                print(f"Or place your video file in: {video_path}")
                return
            
            # Check if the video file exists
            if not os.path.exists(video_path):
                print(f"Video file not found at: {video_path}")
                return
                
            print(f"\nProcessing video from: {video_path}")
            
            # Create the video generator
            video_generator = VideoGenerator(video_path, audio_path, word_timestamps)
            
            # Create the final video with lyrics and audio
            print("\nCreating final video with lyrics and audio...")
            if video_generator.create_video("final_video.mp4"):
                print("\nVideo saved successfully as 'final_video.mp4'")
            else:
                print("Failed to create video")
        else:
            print("Failed to get word timestamps")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
