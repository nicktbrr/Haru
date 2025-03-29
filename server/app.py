from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure upload settings
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..")
app.config["MUSIC_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "music")
app.config["VIDEO_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "videos")
app.config["SESSIONS_FILE"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "sessions.json")

# Create necessary folders
os.makedirs(app.config["MUSIC_FOLDER"], exist_ok=True)
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_music():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Check file extension
    allowed_extensions = {".mp3", ".wav"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({"error": "Invalid file type. Only MP3 and WAV files are allowed."}), 400

    if file:
        try:
            # Generate a unique session ID
            session_id = str(time.time())

            unique_filename = f"{session_id}{file_ext}"
            filepath = os.path.join(
                app.config["MUSIC_FOLDER"], unique_filename)
            file.save(filepath)

            return jsonify({
                "message": "File uploaded successfully",
            })
        except Exception as e:
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500


@app.route("/generate", methods=["POST"])
def generate_video():
    try:
        # Get all files in the music directory
        music_files = os.listdir(app.config["MUSIC_FOLDER"])

        if not music_files:
            return jsonify({"error": "No music files found in the assets/music directory"}), 404

        # Get the most recent file based on modification time
        latest_file = max(
            music_files,
            key=lambda x: os.path.getmtime(
                os.path.join(app.config["MUSIC_FOLDER"], x))
        )

        return jsonify({
            "message": "Found latest music file",
            "filename": latest_file,
            "filepath": os.path.join(app.config["MUSIC_FOLDER"], latest_file)
        })

    except Exception as e:
        return jsonify({"error": f"Error finding music file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
