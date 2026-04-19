from flask import Flask, render_template, request, send_file, jsonify
import edge_tts
import os
import uuid
import asyncio

app = Flask(__name__)

# Render safe folder
OUTPUT_DIR = "/tmp/tts_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# TTS STABLE ENGINE
# =========================
@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "vi-VN-HoaiMyNeural")
        rate = request.form.get("rate", "0")

        if not text:
            return jsonify({"error": "No text"}), 400

        file_id = str(uuid.uuid4())
        filename = file_id + ".mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # SAFE async wrapper (fix Render crash)
        async def run_tts():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=f"{rate}%"
            )
            await communicate.save(filepath)

        asyncio.run(run_tts())

        return jsonify({
            "audio": f"/audio/{filename}",
            "file": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# AUDIO
# =========================
@app.route("/audio/<filename>")
def audio(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, mimetype="audio/mpeg")


# =========================
# DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, as_attachment=True)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)