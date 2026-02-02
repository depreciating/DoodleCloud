import os
import sys
import time
import json
from flask import Flask, render_template, request, jsonify, send_file

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import auth
import database
import converter
import upload
import download
from config_loader import CONF

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(parent_dir, 'upload')
DOWNLOAD_FOLDER = os.path.join(parent_dir, 'download')
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DOWNLOAD_FOLDER): os.makedirs(DOWNLOAD_FOLDER)

USERNAME = CONF.get("INSTA_USER")
PASSWORD = CONF.get("INSTA_PASS")
client = None
auth_token = None
user_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    global client, auth_token, user_id
    
    if not auth_token:
        token, uid, cl = auth.login_smart(USERNAME, PASSWORD)
        if token:
            auth_token = token
            user_id = uid
            client = cl
        else:
            return jsonify({"status": "disconnected"})

    thread_id = auth.get_cached_thread(USERNAME)
    
    return jsonify({
        "status": "connected", 
        "username": USERNAME,
        "thread_selected": bool(thread_id)
    })

@app.route('/api/threads', methods=['GET'])
def get_threads():
    if not client: return jsonify({"error": "Not logged in"}), 401

    try:
        resp = client.private_request("direct_v2/inbox/", params={"limit": "20"})
        threads_raw = resp.get('inbox', {}).get('threads', [])
        
        threads = []
        for t in threads_raw:
            title = t.get('thread_title')
            if not title:
                users = t.get('users', [])
                title = ", ".join([u['username'] for u in users]) or "Unknown Chat"
            
            threads.append({
                "id": t.get('thread_id'),
                "title": title
            })
            
        return jsonify(threads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/threads', methods=['POST'])
def select_thread():
    data = request.json
    thread_id = data.get('thread_id')
    
    if not thread_id: return jsonify({"error": "No ID"}), 400
    
    auth.update_cache(USERNAME, thread_id=thread_id)
    return jsonify({"status": "success"})

@app.route('/api/files', methods=['GET'])
def list_files():
    files = database.list_files()
    for f in files:
        try:
            f['parts'] = len(json.loads(f['media_ids']))
        except:
            f['parts'] = 1
    return jsonify(files)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    thread_id = auth.get_cached_thread(USERNAME)
    if not thread_id:
        return jsonify({"error": "NO_THREAD_SELECTED"}), 400 

    try:
        upload_list = converter.prepare_file(save_path)
    except Exception as e: return jsonify({"error": str(e)}), 500

    if not upload_list: return jsonify({"error": "Conversion failed"}), 500

    uploaded_ids = []
    try:
        for idx, (path, is_temp) in enumerate(upload_list, 1):
            item_id, otid = auth.get_random_message(client, thread_id)
            if not item_id: raise Exception("Could not fetch message target")

            mid = upload.upload_image_step_1(auth_token, user_id, path)
            if not mid: raise Exception(f"Failed to upload part {idx}")

            time.sleep(1)
            upload.attach_doodle_step_2(mid, auth_token, thread_id, item_id, otid)
            uploaded_ids.append(mid)

            if is_temp and os.path.exists(path): os.remove(path)
            time.sleep(1)

        was_converted = any(u[1] for u in upload_list)
        database.save_file_record(filename, uploaded_ids, was_converted)
        if os.path.exists(save_path): os.remove(save_path)

        return jsonify({"status": "success", "filename": filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_route():
    data = request.json
    media_ids = json.loads(data.get('media_ids'))
    filename = data.get('filename')
    is_converted = data.get('is_converted')
    try:
        download.download_file(media_ids, filename, is_converted, auth_token)
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_route():
    data = request.json
    if database.delete_file_record(data.get('id')): return jsonify({"status": "success"})
    else: return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    print(f"[*] Starting Web Interface on http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False, port=5000)