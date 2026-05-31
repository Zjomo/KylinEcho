from flask import Flask, render_template, request, jsonify, send_file
from flask import redirect, url_for
from werkzeug.utils import secure_filename
import os
import uuid
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

from backend.main import SubtitleExtractor
from backend.tools.ocr import OcrRecogniser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SUBTITLE_FOLDER'] = 'static/subtitles'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SUBTITLE_FOLDER'], exist_ok=True)

video_cache = {
    'video_path': None,
    'video_width': None,
    'video_height': None
}

ocr_engine = OcrRecogniser()  # 实时识别使用


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files.get('video')
    if not file:
        return "No file uploaded", 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return redirect(url_for('play_video', filename=filename))


@app.route('/play')
def play_video():
    filename = request.args.get('filename')
    if not filename:
        return "No video specified", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "Video not found", 404

    cap = cv2.VideoCapture(filepath)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Failed to read video", 400

    height, width = frame.shape[:2]

    x = int(width * 0.05)  # 离左边的横向距离
    y = int(height * 0.78)  # 离上面的纵向距离
    w = int(width * 0.90)  # 窗口宽
    h = int(height * 0.20)  # 窗口高

    video_cache['video_path'] = filepath
    video_cache['video_width'] = width
    video_cache['video_height'] = height

    return render_template('index.html',
                           video_url=f"/{filepath}",
                           width=width,
                           height=height,
                           default_box={'x': x, 'y': y, 'w': w, 'h': h})


@app.route('/extract', methods=['POST'])
def extract_subtitles():
    try:
        data = request.get_json()
        x, y, w, h = map(int, (data['x'], data['y'], data['w'], data['h']))
        video_path = video_cache.get('video_path')

        if not video_path or not os.path.exists(video_path):
            return jsonify({'status': 'error', 'msg': 'No video uploaded'}), 400

        subtitle_area = (y, y + h, x, x + w)
        extractor = SubtitleExtractor(video_path, subtitle_area)
        extractor.run()

        # 查找生成的文件
        base_name = os.path.splitext(video_path)[0]
        srt_path = base_name + '.srt'
        txt_path = base_name + '.txt'
        output_path = txt_path if os.path.exists(txt_path) else srt_path

        if not os.path.exists(output_path):
            return jsonify({'status': 'error', 'msg': '字幕提取失败'}), 500

        filename = os.path.basename(output_path)
        final_path = os.path.join(app.config['SUBTITLE_FOLDER'], filename)
        os.rename(output_path, final_path)  # 移动到公开下载目录

        return jsonify({
            'status': 'success',
            'msg': '字幕提取成功！',
            'download_url': f'/download/{filename}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['SUBTITLE_FOLDER'], filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404


@app.route('/preview', methods=['POST'])
def preview_text():
    try:
        # 1. 从 files 拿到二进制文件
        file = request.files.get('image')
        if file is None:
            return jsonify({'text': '', 'error': 'No image uploaded'}), 400

        # 2. 直接用 PIL 打开
        image = Image.open(file.stream).convert('RGB')
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 3. OCR 识别
        dt_boxes, rec_res = ocr_engine.predict(image_np)
        text = " ".join([t[0] for t in rec_res])

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'text': '', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
