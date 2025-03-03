import base64
import datetime
import json
import threading
import time

import requests

response_map = []


def on_ready():
    print('ready')


def on_response(response):
    global response_map
    response_map.append(response)


def on_completed():
    print('completed')


# 实现一个简单的网络服务
from flask import Flask, request, jsonify

app = Flask(__name__)


def callback_task(progress_callback_url, task_id):
    # 模拟任务执行的进程
    global response_map
    status = "RUNNING"
    # 每次取一个
    while response_map:
        response = response_map.pop(0)
        if status == "RUNNING":
            data = {
                "taskId": task_id,
                "status": status,
                "recognition_results": response['asr_results'],
            }
            requests.post(progress_callback_url, json=data)
            # wait 5s
            time.sleep(5)

    status = "FINISHED"
    data = {
        "taskId": task_id,
        "status": status,
        "recognition_results": [],
    }
    requests.post(progress_callback_url, json=data)


# receive a post request with file
@app.route('/predict', methods=['POST'])
def asr():
    # get file from request
    file = request.files.get('file')
    language = request.form.get('language')
    task_id = request.form.get('taskId')
    progress_callback_url = request.form.get('progressCallbackUrl')

    token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzI3NjUxMTMwNjYsImlhdCI6MTczMjc2NTExM30.tboPQVyJoKuPAbZVIOPJxI9wbr5TD5Mtck-8P59Fs2I'
    call_token = 'eyJhbGciOiJIUzI1NiJ9.eyJ0ZW5hbnRfaWQiOjEsInVzZXJfaWQiOjYsInRva2VuX2NyZWF0ZWRfYXQiOjE3MzMxOTY5Mzg0NTUsImlhdCI6MTczMzE5NjkzOH0.xPt2491jDWZQYCS3TpTSko3ln6xTApqg12m_T-P4FDk'
    region = 'China'

    try:
        file_content = file.read()
        audio_base64 = base64.b64encode(file_content)
        audio_base64 = audio_base64.decode('utf-8')
    except FileNotFoundError:
        raise ValueError('File not found. Please check the path and try again.')

    # 发送音频数据
    message = {
        "enableWords": True,
        "lang": language,
        "fileBase64": audio_base64,
        "finalResult": False,
    }

    message = json.dumps(message)

    try:
        session = requests.Session()
        full_url = 'http://172.26.1.45:8202/ai/cpp/api/v1/asr/stream'
        # full_url = 'http://localhost:8202/ai/cpp/api/v1/asr/stream'
        headers = {
            'token': token,
            'call_token': call_token,
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }
        with session.post(
            full_url,
            data=message,
            headers=headers,
            stream=True,
            timeout=600,
        ) as response:

            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    chunk_json = chunk_str.split(":", 1)[1]
                    resp = json.loads(chunk_json)
                    if 'success' in resp and bool(resp['success']):
                        on_ready()
                        continue

                    if 'end' in resp and bool(resp['end']):
                        on_completed()
                        break

                    on_response(resp)
                    continue

    except Exception as e:
        print(e)
        print(datetime.datetime.now())

    threading.Thread(
        target=callback_task, args=(progress_callback_url, task_id)
    ).start()

    return jsonify(
        {
            'status': 'OK',
            'message': 'ASR request received',
        }
    )


@app.route('/cancel', methods=['POST'])
def cancel():
    task_id = request.args.get('taskId')
    return jsonify(
        {
            'status': 'OK',
            'message': 'ASR request cancelled',
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678, debug=True)
