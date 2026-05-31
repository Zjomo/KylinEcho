import os
import warnings
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, redirect, url_for

import soundfile as sf
from werkzeug.utils import secure_filename

from modules.utils.paths import UVR_OUTPUT_DIR
from modules.diarize.audio_loader import load_audio
from modules.utils.logger import get_logger
from uvr.models import MDX

# 初始化
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logger = get_logger()
warnings.filterwarnings('ignore')

# 模型配置
model_dir = r'../models/UVR/MDX_Net_Models'
model_name = r'UVR-MDX-NET-Inst_1'
model_config = {"segment": 256, "split": True}
device = 'cpu'
sample_rate = 16000

# 加载模型（一次即可）
model = MDX(
    model_dir=model_dir,
    name=model_name,
    other_metadata=model_config,
    device=device,
    logger=None
)
model.sample_rate = sample_rate


# 工具函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(upload_path)

            # 加载音频
            audio = load_audio(upload_path)

            # 模型处理
            result = model(audio)
            instrumental, vocals = result["instrumental"].T, result["vocals"].T

            # 输出路径
            timestamp = datetime.now().strftime("%m%d%H%M%S")
            output_filename = f"UVR-{timestamp}"
            ext = ".wav"
            
            instrumental_output_path = os.path.join(UVR_OUTPUT_DIR, "instrumental",f"{output_filename}-instrumental{ext}")
            vocals_output_path = os.path.join(UVR_OUTPUT_DIR, "vocals", f"{output_filename}-vocals{ext}")
            
            os.makedirs(os.path.dirname(instrumental_output_path), exist_ok=True)
            os.makedirs(os.path.dirname(vocals_output_path), exist_ok=True)

            sf.write(instrumental_output_path, instrumental, sample_rate, format="WAV")
            sf.write(vocals_output_path, vocals, sample_rate, format="WAV")

            return render_template('index.html',
                                   instrumental_path=url_for('download_file',
                                                             path=f"instrumental/{output_filename}-instrumental{ext}"),
                                   vocals_path=url_for('download_file', path=f"vocals/{output_filename}-vocals{ext}"),
                                   success=True)

        else:
            return render_template('index.html', error="Unsupported file type.")
    return render_template('index.html')


@app.route('/download/<path:path>')
def download_file(path):
    dir_name, file_name = os.path.split(path)
    return send_from_directory(os.path.join(UVR_OUTPUT_DIR, dir_name), file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(port=5012, debug=True)
