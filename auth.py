from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import json
import base64
import random
import os

CACHE_FILE = "thread_cache.json"

def generate_igt_token(client):
    try:
        payload = {"ds_user_id": client.user_id, "sessionid": client.sessionid}
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        return f"Bearer IGT:2:{encoded}"
    except: return None

def load_cache_data():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f: return json.load(f)
        except: pass
    return {}

def save_cache_data(data):
    with open(CACHE_FILE, "w") as f: json.dump(data, f, indent=4)

def update_cache(username, client=None, thread_id=None):
    data = load_cache_data()
    if username not in data: data[username] = {}
    
    if client:
        data[username]["settings"] = client.get_settings()
        data[username]["user_id"] = str(client.user_id)
        
    if thread_id: 
        data[username]["thread_id"] = thread_id
        
    save_cache_data(data)

def get_cached_thread(username):
    return load_cache_data().get(username, {}).get("thread_id")

def login_smart(username, password):
    cl = Client()
    cl.set_device({"app_version": "409.0.0.48.170", "android_version": 28, "model": "G011A"})

    data = load_cache_data()
    user_data = data.get(username, {})
    cached_settings = user_data.get("settings")
    
    session_valid = False

    if cached_settings:
        try:
            cl.set_settings(cached_settings)
            
            cl.login(username, password)
            
            try:
                cl.get_timeline_feed()
                session_valid = True
            except LoginRequired:
                print("[!] Session expired. Refreshing...")
                
                old_uuids = cl.get_settings().get("uuids")
                cl.set_settings({})
                if old_uuids:
                    cl.set_uuids(old_uuids)

                cl.login(username, password)
                session_valid = True
        except Exception as e:
            print(f"[-] Session restore failed: {e}")

    if not session_valid:
        try:
            print(f"[*] Performing fresh login for {username}...")
            cl.login(username, password)
        except Exception as e:
            print(f"[-] Login Fatal Error: {e}")
            return None, None, None

    update_cache(username, client=cl)
    
    return generate_igt_token(cl), str(cl.user_id), cl

def select_target_thread(client):
    try:
        resp = client.private_request("direct_v2/inbox/", params={"limit": "20"})
        threads = resp.get('inbox', {}).get('threads', [])
        
        print("\n=== SELECT THREAD ===")
        for i, t in enumerate(threads, 1):
            title = t.get('thread_title') or "Unknown"
            print(f"{i}. {title}")
            
        choice = int(input("\nSelect: ").strip()) - 1
        return str(threads[choice].get('thread_id'))
    except: return None

def get_random_message(client, thread_id):
    try:
        resp = client.private_request(f"direct_v2/threads/{thread_id}/", params={"limit": "20"})
        items = resp.get('thread', {}).get('items', [])
        
        valid = [i for i in items if i.get('item_type') not in ['video_call_event', 'action_log']]
        if not valid: valid = items
        
        if not valid: return None, None
            
        sel = random.choice(valid)
        return str(sel.get('item_id')), str(sel.get('client_context') or sel.get('item_id'))
    except: return None, None