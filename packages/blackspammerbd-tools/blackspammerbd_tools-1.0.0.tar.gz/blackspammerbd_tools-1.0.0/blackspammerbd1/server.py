#!/usr/bin/env python3
"""
Flask Server for blackspammerbd1 package.
SERVER_PORT: 41141
"""

from flask import Flask, request, jsonify
import os, base64

app = Flask(__name__)

@app.route('/connect', methods=['POST'])
def handle_connect():
    data = request.get_json()
    code = data.get("connection_code")
    if code and len(code) == 8:
        return jsonify({"message": "Connected successfully", "code": code}), 200
    else:
        return jsonify({"error": "Invalid connection code"}), 400

@app.route('/list', methods=['GET'])
def handle_list():
    files = os.listdir('.')  # বর্তমান ডিরেক্টরির সব ফাইল/ফোল্ডার
    return jsonify({"files": files}), 200

@app.route('/download/<item>', methods=['GET'])
def handle_download(item):
    if os.path.exists(item):
        with open(item, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode("utf-8")
        return jsonify({"data": encoded}), 200
    else:
        return jsonify({"error": "Item not found"}), 404

@app.route('/upload', methods=['POST'])
def handle_upload():
    data = request.get_json()
    item = data.get("item")
    file_data = data.get("data")
    if item and file_data:
        try:
            decoded = base64.b64decode(file_data)
            with open(item, "wb") as f:
                f.write(decoded)
            return jsonify({"message": f"Uploaded {item} successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid request"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=41141)
