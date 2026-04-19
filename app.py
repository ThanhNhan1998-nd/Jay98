from flask import Flask, render_template, request, send_file, jsonify
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)

OUTPUT_DIR = "/tmp/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def tts_generate(text, voice, rate, path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate}%"
    )
    await communicate.save(path)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text", "")
    voice = request.form.get("voice", "vi-VN-HoaiMyNeural")
    rate = request.form.get("rate", "0")

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    asyncio.run(tts_generate(text, voice, rate, filepath))

    return jsonify({
        "audio": f"/audio/{filename}"
    })


@app.route("/audio/<filename>")
def audio(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), mimetype="audio/mpeg")


@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)