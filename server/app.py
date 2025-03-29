# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# # Configure upload settings
# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
# app.config["UPLOAD_FOLDER"] = os.path.join(
#     os.path.dirname(os.path.abspath(__file__)), "..")
# app.config["MUSIC_FOLDER"] = os.path.join(
#     app.config["UPLOAD_FOLDER"], "assets", "music")

# # Create music folder if it doesn't exist
# os.makedirs(app.config["MUSIC_FOLDER"], exist_ok=True)


# @app.route("/upload", methods=["POST"])
# def upload_music():
#     if "file" not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     # Check file extension
#     allowed_extensions = {".mp3", ".wav"}
#     file_ext = os.path.splitext(file.filename)[1].lower()

#     if file_ext not in allowed_extensions:
#         return jsonify({"error": "Invalid file type. Only MP3 and WAV files are allowed."}), 400

#     if file:
#         try:
#             # Secure the filename and save the file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config["MUSIC_FOLDER"], filename)
#             file.save(filepath)

#             return jsonify({
#                 "message": "File uploaded successfully",
#                 "filename": filename,
#                 "filepath": filepath
#             })
#         except Exception as e:
#             return jsonify({"error": f"Error saving file: {str(e)}"}), 500


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import uuid
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

# Initialize sessions storage if it doesn't exist
if not os.path.exists(app.config["SESSIONS_FILE"]):
    with open(app.config["SESSIONS_FILE"], "w") as f:
        json.dump({}, f)


def get_sessions():
    """Read the sessions from the file"""
    try:
        with open(app.config["SESSIONS_FILE"], "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_session(session_id, data):
    """Save session data to the file"""
    sessions = get_sessions()
    sessions[session_id] = data
    with open(app.config["SESSIONS_FILE"], "w") as f:
        json.dump(sessions, f)


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
            session_id = str(uuid.uuid4())

            # Secure the filename and save the file
            original_filename = file.filename
            unique_filename = f"{session_id}{file_ext}"
            filepath = os.path.join(
                app.config["MUSIC_FOLDER"], unique_filename)
            file.save(filepath)

            # Store session information
            session_data = {
                "timestamp": time.time(),
                "original_filename": original_filename,
                "file_path": filepath,
                "status": "uploaded",
                "video_path": None
            }
            save_session(session_id, session_data)

            return jsonify({
                "message": "File uploaded successfully",
                "session_id": session_id
            })
        except Exception as e:
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500


@app.route("/generate", methods=["POST"])
def generate_video():
    data = request.json

    if not data or "session_id" not in data:
        return jsonify({"error": "Missing session_id parameter"}), 400

    session_id = data["session_id"]

    # Get the session data
    sessions = get_sessions()
    if session_id not in sessions:
        return jsonify({"error": "Invalid session ID or session expired"}), 404

    session_data = sessions[session_id]

    # Check if music file exists
    if not os.path.exists(session_data["file_path"]):
        return jsonify({"error": "Music file not found. Please upload again."}), 404

    # Check if the status is 'uploaded' and not already processed
    if session_data["status"] != "uploaded":
        return jsonify({"error": "This session has already been processed"}), 400

    try:
        # Here you would integrate with your AI services:
        # 1. Analyze the music with Gemini
        # 2. Generate video with LumaAI
        # For now, we'll simulate this process:

        # Update session status to processing
        session_data["status"] = "processing"
        save_session(session_id, session_data)

        # Simulate processing time (remove in production)
        time.sleep(2)

        # Generate a mock video path (in production, this would be the actual video)
        video_filename = f"video_{session_id}.mp4"
        video_path = os.path.join(app.config["VIDEO_FOLDER"], video_filename)

        # Create an empty file to simulate video creation
        # In production, this would be the actual generated video file
        with open(video_path, "w") as f:
            f.write("Mock video content")

        # Update session with completed status and video path
        session_data["status"] = "completed"
        session_data["video_path"] = video_path
        save_session(session_id, session_data)

        # Generate URLs for the frontend
        video_url = f"http://localhost:5000/video/{video_filename}"
        download_url = f"http://localhost:5000/download/{video_filename}"

        return jsonify({
            "message": "Video generated successfully",
            "description": "A beautiful cherry blossom video generated from your music",
            "video_url": video_url,
            "download_url": download_url
        })

    except Exception as e:
        # Update session status to error
        session_data["status"] = "error"
        session_data["error"] = str(e)
        save_session(session_id, session_data)

        return jsonify({"error": f"Error generating video: {str(e)}"}), 500


@app.route("/video/<filename>")
def serve_video(filename):
    return app.send_static_file(os.path.join(app.config["VIDEO_FOLDER"], filename))


@app.route("/download/<filename>")
def download_video(filename):
    return app.send_static_file(
        os.path.join(app.config["VIDEO_FOLDER"], filename),
        as_attachment=True
    )


@app.route("/status/<session_id>", methods=["GET"])
def check_status(session_id):
    """Additional route to check the status of a processing session"""
    sessions = get_sessions()

    if session_id not in sessions:
        return jsonify({"error": "Invalid session ID"}), 404

    session_data = sessions[session_id]

    return jsonify({
        "status": session_data["status"],
        "timestamp": session_data["timestamp"],
        "filename": session_data["original_filename"]
    })

# Clean up old sessions periodically


def cleanup_old_sessions():
    """Remove sessions and files older than 24 hours"""
    sessions = get_sessions()
    current_time = time.time()
    expired_sessions = []

    for session_id, data in sessions.items():
        # Check if session is older than 24 hours
        if current_time - data["timestamp"] > 86400:  # 24 hours in seconds
            # Remove files if they exist
            if data["file_path"] and os.path.exists(data["file_path"]):
                os.remove(data["file_path"])

            if data["video_path"] and os.path.exists(data["video_path"]):
                os.remove(data["video_path"])

            expired_sessions.append(session_id)

    # Remove expired sessions from dictionary
    for session_id in expired_sessions:
        del sessions[session_id]

    # Save updated sessions
    with open(app.config["SESSIONS_FILE"], "w") as f:
        json.dump(sessions, f)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
