from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
from werkzeug.utils import secure_filename
import os
import time
import pathlib
import subprocess
import queue

from modules.whisper.data_classes import Segment
from modules.diarize.audio_loader import load_audio
from transcriber import SpeakerDiarizationTranscriber
import datetime

UPLOAD_FOLDER = '.\\uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'mp4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Whisper 模型路径
MODEL_PATH = r'./models/Whisper/faster-whisper/models--Systran--faster-whisper-large-v2/snapshots/f0fe81560cb8b68660e564f55dd99207059c092e'

# 初始化转录器
processor = SpeakerDiarizationTranscriber(model_path=MODEL_PATH)

# ========= 实时日志队列 =========
log_queue = queue.Queue()

def log(message):
    print(message)
    log_message = datetime.datetime.now().strftime("[%H:%M:%S]") + message
    log_queue.put(log_message)

@app.route("/logs")
def stream_logs():
    def event_stream():
        while True:
            msg = log_queue.get()
            yield f"data: {msg}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

# =================================

def burn_subtitles_to_video(video_path, srt_path, output_path):
    video_path_fixed = pathlib.Path(video_path).resolve().as_posix()
    srt_path_fixed = pathlib.Path(srt_path).resolve().as_posix()
    output_path_fixed = pathlib.Path(output_path).resolve().as_posix()

    log("🎬 开始烧录字幕到视频...")
    cmd = [
        "ffmpeg",
        "-i", video_path_fixed,
        "-vf", r"subtitles='%s'" % (srt_path_fixed[0] + '\\' + srt_path_fixed[1:]),
        output_path_fixed
    ]

    log("🔥 FFmpeg 命令： " + " ".join(cmd))
    subprocess.run(cmd, check=True)
    log(f"✅ 字幕已烧录完成：{output_path_fixed}")

def extract_audio_from_video(video_path, output_path, sample_rate=16000):
    log("🎧 正在从视频提取音频...")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-ac", "1", "-ar", str(sample_rate),
        "-vn", "-f", "wav", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    log(f"✅ 音频已提取至：{output_path}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def write_srt_file(segments, srt_path):
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    log("📝 正在写入 SRT 字幕文件...")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            speaker = seg['speaker']
            text = seg['text']
            f.write(f"{i}\n{start} --> {end}\n{speaker}: {text}\n\n")
    log(f"✅ 字幕文件已写入：{srt_path}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("audio_file")
        use_diarization = request.form.get("use_diarization") == "on"

        if not file or file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            log(f"📁 文件已上传：{filename}")

            # 如果是视频则提取音频
            file_ext = filename.rsplit('.', 1)[-1].lower()
            if file_ext == "mp4":
                wav_filename = os.path.splitext(filename)[0] + "_extracted.wav"
                wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)
                extract_audio_from_video(filepath, wav_filepath)
                audio_path = wav_filepath
            else:
                audio_path = filepath

            # 转录处理
            try:
                log("🧠 开始转录" + ("（含说话人识别）" if use_diarization else "（不含说话人识别）"))
                if use_diarization:
                    segments = processor.run(audio_path)
                else:
                    segments = processor.run_without_diarization(audio_path)
                log("✅ 转录完成")
            except Exception as e:
                log(f"❌ 转录失败：{str(e)}")
                raise

            results = [
                {
                    "speaker": seg.text.split("|")[0] if "|" in seg.text else "（字幕）",
                    "start": round(seg.start, 1),
                    "end": round(seg.end, 1),
                    "text": "|".join(seg.text.split("|")[1:]) if "|" in seg.text else seg.text
                }
                for seg in segments
            ]

            # 写入字幕
            srt_filename = os.path.splitext(filename)[0] + ".srt"
            srt_path = os.path.join(app.config['UPLOAD_FOLDER'], srt_filename)
            write_srt_file(results, srt_path)

            # 视频字幕烧录
            if file_ext == "mp4":
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.splitext(filename)[0]
                output_video_filename = f"{base_name}_subtitled_{timestamp}.mp4"
                output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], output_video_filename)

                try:
                    burn_subtitles_to_video(filepath, srt_path, output_video_path)
                    video_ready = True
                except Exception as e:
                    log(f"⚠️ 字幕烧录失败：{str(e)}")
                    video_ready = False
            else:
                video_ready = False

            return render_template("index.html", results=results, filename=filename,
                                   srt_file=srt_filename,
                                   video_file=output_video_filename if video_ready else None)

    return render_template("index.html", results=None)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5011, debug=True, threaded=True)
