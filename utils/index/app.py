from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')      # 主页


@app.route('/face')
def face():
    return redirect("http://127.0.0.1:5001")            # 人脸识别服务

@app.route('/upload')
def upload():
    return redirect("http://127.0.0.1:5001/admin")      # 智能数据上传【人脸信息录入】



@app.route('/voice')
def voice():
    return redirect("http://127.0.0.1:5002")             # 智能交互助手

@app.route('/agent')
def agent():
    return redirect("https://xiaozhi.me/console/agents")  # Ai智能体控制台



@app.route('/robot')
def robot():
    return redirect("http://localhost/chat/wJ6H8nMxZRhE2ZQb") # 智能校史馆员


@app.route('/exhibits')
def exhibits():
    return redirect("http://127.0.0.1:5004")                  # 示例展品展示


if __name__ == '__main__':
    app.run(port=5003, debug=True)
