import eventlet

eventlet.monkey_patch()

import requests
from flask import Flask, render_template, request
import hashlib
import hmac
import base64
import json
import time
import threading
import logging
import pyaudio
from websocket import create_connection
import websocket
from urllib.parse import quote
import re

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading, time, json, logging, hashlib, hmac, base64
import pyaudio, requests, websocket
from websocket import create_connection
from urllib.parse import quote
from flask_socketio import SocketIO, emit
from threading import Lock
import psutil
import platform

try:
    import pynvml
    pynvml.nvmlInit()
except:
    pynvml = None


# 初始化 SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

client_instance = None


def translate_with_zhipu(text,
                         api_key=r"7eaba50915a641379732f5c0f50cbe11.QlJ9StdNwa1OZZkb",
                         model='glm-4-flash',
                         # model='glm-3-turbo',
                         target_lang='en',
                         source_lang='cn'):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,  # 可选其他模型如 glm-3-turbo
        "messages": [
            # {"role": "system", "content": "你是一个翻译助手，把%s翻译成%s，不需要解释说明"%(source_lang,target_lang)},
            {"role": "system", "content": f"你是一个翻译助手，把{source_lang}翻译成{target_lang}，不需要解释说明"},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("[翻译接口出错]", e)
        return "(翻译失败)"


class Client():
    def __init__(self, app_id, api_key, lang='cn', targetLang='en'):
        self.app_id = app_id
        self.api_key = api_key
        self.lang = lang
        self.targetLang = targetLang
        self.last_result_data = []
        self.running = True

        ts = str(int(time.time()))
        md5 = hashlib.md5()
        md5.update((app_id + ts).encode('utf-8'))
        baseString = md5.hexdigest().encode('utf-8')

        signa = hmac.new(api_key.encode('utf-8'), baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa).decode('utf-8')

        url = (
            f"ws://rtasr.xfyun.cn/v1/ws?appid={app_id}"
            f"&ts={ts}&signa={quote(signa)}"
            f"&lang={lang}&targetLang={targetLang}&roleType=2&transStrategy=1&transType=normal"
        )

        self.ws = create_connection(url)
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send_from_stream(self):
        print("🔊 Start capturing system audio from VB-Audio device...")

        chunk_size = 128
        sample_rate = 16000
        channels = 1
        format = pyaudio.paInt16

        pa = pyaudio.PyAudio()

        vb_device_index = None
        for i in range(pa.get_device_count()):
            dev = pa.get_device_info_by_index(i)
            if "VB-Audio" in dev['name'] or "VoiceMeeter" in dev['name']:
                vb_device_index = i
                print(f"✅ Found VB-Audio device: {dev['name']} (Index: {i})")
                break

        if vb_device_index is None:
            print("❌ VB-Audio device not found.")
            return

        stream = pa.open(format=format,
                         channels=channels,
                         rate=sample_rate,
                         input=True,
                         input_device_index=vb_device_index,
                         frames_per_buffer=chunk_size)

        try:
            while self.running and self.ws.connected:
                data = stream.read(chunk_size, exception_on_overflow=False)
                try:
                    self.ws.send(data)
                except websocket.WebSocketConnectionClosedException:
                    print("⚠️ WebSocket 已关闭，停止发送音频数据。")
                    break
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("🎤 Stopped capturing audio.")
        finally:
            try:
                if self.ws.connected:
                    self.ws.send('{"end":  true}'.encode('utf-8'))
            except websocket.WebSocketConnectionClosedException:
                print("⚠️ 无法发送结束指令，WebSocket 已关闭。")
            stream.stop_stream()
            stream.close()
            pa.terminate()

    def recv(self):
        print("Waiting for recognition results...\n")
        try:
            global last_result_data
            last_result_data = []
            while self.ws.connected:
                result = self.ws.recv()
                if not result:
                    break
                result_dict = json.loads(result)

                if result_dict["action"] == "started":
                    print("[Handshake successful]")

                elif result_dict["action"] == "result":
                    data = json.loads(result_dict["data"])
                    self.last_result_data.append(data)
                    self.print_subtitles(data)
                    last_result_data.append(data)

                elif result_dict["action"] == "error":
                    print("[Error] " + result_dict.get("message", "Unknown error"))
                    self.ws.close()
        except websocket.WebSocketConnectionClosedException:
            print("WebSocket closed.")

    def print_subtitles(self, data):
        global orig_text, translated
        if 'biz' not in data.keys():
            cn = data.get("cn", {})
            st = cn.get("st", {})
            rt_blocks = st.get("rt", [])
            tl_blocks = data.get("tl", {}).get("st", {}).get("rt", [])

            for i, rt in enumerate(rt_blocks):
                bg = int(st.get("bg", 0)) / 1000
                ed = int(st.get("ed", 0)) / 1000

                ws = rt.get("ws", [])
                rl = None

                if ws and ws[0].get("cw"):
                    rl = ws[0]["cw"][0].get("rl", "未知")

                orig_text = "".join(w["cw"][0]["w"] for w in ws)
                orig_text = re.sub(r'^\W+', '', orig_text) # 去除开头可能存在的 标点

                translated = translate_with_zhipu(orig_text, source_lang=self.lang, target_lang=self.targetLang)

        else:
            translated_tmp.append(translated)
            rl = data.get('rl')
            bg = data.get('bg') / 1000
            ed = data.get('ed') / 1000
            if (bg > 0) and (ed > 0) and (translated_tmp[-1] != translated_tmp[-2]):
                print(f"\n⏱ {bg:.2f}s - {ed:.2f}s | 🤵 Speaker {rl}")
                print(f"🗣 原文: {orig_text}")
                print(f"🌐 翻译: {translated}")

                # 传输至前端
                socketio.emit('subtitle', {'original': orig_text,
                                           'translated': translated,
                                           'start_time': f"{bg:.2f}",
                                           'end_time': f"{ed:.2f}",
                                           'speaker': rl
                                           })

    def close(self):
        print("🛑 关闭字幕引擎")
        self.running = False  # <<< 停止发送线程
        if self.ws and self.ws.connected:
            self.ws.close()


@app.route('/')
def index():
    return render_template('index.html')


# 加锁
client_instance = None
client_lock = Lock()


@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    # 加锁
    global client_instance
    with client_lock:
        # 若有 "旧实例" 存在，先关闭
        if client_instance:
            print("⚠️ 已有识别会话，关闭旧实例...")
            client_instance.close()
            client_instance = None

        app_id = "28c1c3c6"
        api_key = "9cd6592d3e6f93994d922f6c6feb7f79"
        lang = request.form.get('lang', 'en')
        targetLang = request.form.get('targetLang', 'cn')
        client = Client(app_id, api_key, lang=lang, targetLang=targetLang)
        threading.Thread(target=client.send_from_stream).start()

    return "Recognition started"


@app.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    global client_instance
    with client_lock:
        if client_instance:
            print("🛑 停止识别会话...")
            client_instance.close()
            client_instance = None
            return "Recognition stopped"
        return "No active recognition"


@app.route('/system_stats')
def system_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    mem_used = memory.used / (1024 ** 3)
    mem_total = memory.total / (1024 ** 3)
    mem_percent = memory.percent

    gpu_info = []
    if pynvml:
        try:
            count = pynvml.nvmlDeviceGetCount()
            for i in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                name_raw = pynvml.nvmlDeviceGetName(handle)
                name = name_raw.decode() if isinstance(name_raw, bytes) else str(name_raw)

                gpu_info.append({
                    'name': name,
                    'memory_used': round(mem.used / (1024 ** 2), 2),
                    'memory_total': round(mem.total / (1024 ** 2), 2),
                    'memory_percent': round(mem.used / mem.total * 100, 1),
                    'gpu_util': util.gpu
                })
        except Exception as e:
            gpu_info = [{'error': str(e)}]

    return {
        'cpu_percent': cpu_percent,
        'memory_used': round(mem_used, 2),
        'memory_total': round(mem_total, 2),
        'memory_percent': mem_percent,
        'gpu': gpu_info,
        'platform': platform.system()
    }



if __name__ == '__main__':
    # 防止出现翻译词重复的情况
    global translated_tmp
    translated_tmp = [0]
    socketio.run(app, host='127.0.0.1', port=5010, debug=True)
