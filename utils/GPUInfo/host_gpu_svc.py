from flask import Flask, jsonify
import pynvml, json, time, serial, threading

pynvml.nvmlInit()
app = Flask(__name__)

def gpu_json():
    """取当前 GPU 状态"""
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    return {
        "gpu": 0,
        "driver": pynvml.nvmlSystemGetDriverVersion(),
        "memory": {"total": info.total, "used": info.used, "free": info.free},
        "utilization": {"gpu": util.gpu, "memory": util.memory},
        "ts": int(time.time())
    }

@app.route("/gpu")
def gpu():
    return jsonify(gpu_json())

# ---------- VMware Tools 虚拟串口部分 ----------
def serial_forward():
    """
    把 Flask 改成 ‘串口服务器’：
    虚拟机每发来一个 ‘GET /gpu\n’，我们就回一段 JSON+‘\n’ 结束。
    VMware Tools 默认会把宿主机的 COM3 映射到客机的 /dev/ttyS1
    """
    ser = serial.Serial("COM4", 115200, timeout=1)
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line == "GET /gpu":
            ser.write((json.dumps(gpu_json()) + "\n").encode())

if __name__ == "__main__":
    # 后台线程跑串口
    threading.Thread(target=serial_forward, daemon=True).start()
    # 前台线程跑 HTTP（可选，给其它物理机用）
    app.run(host="0.0.0.0", port=5510)