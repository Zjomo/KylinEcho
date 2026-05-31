import soundfile

from werkzeug.utils import secure_filename
from funasr import AutoModel
from flask import Flask, request, jsonify, send_file,render_template
from flask_cors import CORS
from utils import *

warnings.filterwarnings('ignore')


# 路径设置
root_dict = os.getcwd()
# video_path = os.path.join(root_dict, 'Video', 'firstRun.mp4')
keyframe_output_dir = os.path.join(root_dict, 'Video', 'img')
Keyframe_output_filename = os.path.join(root_dict, 'video', 'img', 'output_%06d.jpg')

# 确保输出目录存在
os.makedirs(keyframe_output_dir, exist_ok=True)
# 预编码器 与 预训练模型
model_url = os.path.join(root_dict, 'models', 'Image2text')
processor = BlipProcessor.from_pretrained(model_url)
model = BlipForConditionalGeneration.from_pretrained(model_url)

summary = ''


app = Flask(__name__)
CORS(app)  # 允许跨域请求



@app.route('/')
def index():
    return render_template('index.html')


# 1、大语言模型API
def text_to_commentary(Question):
    dashscope.api_key = "sk-8ee136df3d1c461bb85c60a31418d43a"
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': Question}]

    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_turbo,
        messages=messages,
        result_format='message')  # 将返回结果格式设置为 message
    
    answer = response.output.choices[0].message.content
    return answer
    
# 2、AI智能视频剪辑
def AI_Video_API(video_path,output_file):
    global summary
    # 路径设置
    root_dict = os.getcwd()
    keyframe_output_dir = os.path.join(root_dict, 'Video', 'img')
    Keyframe_output_filename = os.path.join(root_dict, 'video', 'img', 'output_%06d.jpg')
    os.makedirs(keyframe_output_dir, exist_ok=True)

    # 预编码器 与 预训练模型
    model_url = os.path.join(root_dict, 'models', 'Image2text')
    processor = BlipProcessor.from_pretrained(model_url)
    model = BlipForConditionalGeneration.from_pretrained(model_url)

    # video_path = os.path.join(root_dict, 'Video', 'firstRun.mp4')
    # output_file = os.path.join(root_dict, 'Video', 'output.mp4')

    summary = AI_Video_Clip(video_path,output_file)
    
    return summary


# 2、图片解析函数 
def image_to_text(image_url, text_express=''):
    raw_image = Image.open(image_url).convert('RGB')
    inputs = processor(raw_image, text_express, return_tensors="pt")
    out = model.generate(**inputs)
    conditional_out = processor.decode(out[0], skip_special_tokens=True)
    return conditional_out


# 3、解说词_语音生成
def text_to_audio(text, output_audio_file):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # 设置语速
    engine.setProperty('volume', 1)  # 设置音量

    # 获取可用的语音列表
    voices = engine.getProperty('voices')

    # 设置中文语音（以微软的中文语音为例）
    for voice in voices:
        if "zh-CN" in voice.languages:
            engine.setProperty('voice', voice.id)
            break

    # 将文本转换为语音并保存为文件
    engine.save_to_file(text, output_audio_file)
    engine.runAndWait()


'''
def text_to_audio(text, output_audio_file):
    sambert_hifigan_tts = pipeline(task=Tasks.text_to_speech, model=model_id, cache_dir='/AI/cacheOfmodelscope')
    output = sambert_hifigan_tts(input=text, voice='zhitian_emo')
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(output_audio_file, 'wb') as f:
        f.write(wav)
'''

# 4、语音识别
def audio_to_text(audio_file):
    root_dict = os.getcwd()
    model_dict = os.path.join(root_dict, 'models', 'audio2txt')
    model = AutoModel(model=model_dict, model_revision="v2.0.4")

    speech, sample_rate = soundfile.read(audio_file)
    res = model.generate(input=speech, 
                         cache=None, 
                         is_final=True, 
                         chunk_size=None, 
                         encoder_chunk_look_back=None, 
                         decoder_chunk_look_back=None)
    return res[0]['text']

# 路由配置
@app.route('/api/language-model', methods=['POST'])
def language_model_route():
    data = request.json
    prompt = data.get('prompt', '')
    response = text_to_commentary(prompt)
    return jsonify({"response": response})
    
  
@app.route('/api/video-processing', methods=['POST'])
def video_processing():
    global summary
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file and file.filename.endswith('.mp4'):
        video_path = os.path.join('uploads', file.filename)
        output_file = os.path.join(root_dict, 'Video', 'output.mp4')

        # 保存上传的文件
        file.save(video_path)

        # 调用 AI 视频剪辑函数
        # AI_Video_API(video_path, output_file)
        summary = AI_Video_API(video_path, output_file)

        # 返回处理后的视频文件
        return send_file(output_file, as_attachment=True)
        
    return jsonify({'error': 'File format not supported'}), 400
    
    
@app.route('/api/summary', methods=['POST'])
def get_summary():
    global summary
    return jsonify({"summary": summary})
    
          
@app.route('/api/image-parsing', methods=['POST'])
def image_parsing_route():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    analysis_result = image_to_text(file_path)
    return jsonify({"analysis": analysis_result})


@app.route('/api/speech-synthesis', methods=['POST'])
def speech_synthesis_route():
    data = request.json
    text = data.get('text', '')
    output_audio_file = 'synthesized.wav'
    model_id = os.path.join(os.getcwd(), 'models', 'text2audio')
    text_to_audio(text, output_audio_file)
    
    return send_file(output_audio_file, as_attachment=True, download_name=output_audio_file, mimetype="audio/wav")



@app.route('/api/speech-recognition', methods=['POST'])
def speech_recognition_route():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    transcription = audio_to_text(file_path)
    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='127.0.0.1', port=5006)
