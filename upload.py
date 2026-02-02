import requests
import json
import random
import time
import os
import proxy

RUPLOAD_URL_TEMPLATE = "https://rupload.facebook.com/messenger_image/{}"
GRAPHQL_URL = "https://i.instagram.com/graphql_www"

def upload_image_step_1(auth_token, user_id, image_path):
    if not os.path.exists(image_path): return None
    file_size = os.path.getsize(image_path)
    
    random_upload_id = f"5482841449760_0_-{random.randint(100000000, 999999999)}"
    
    device_headers = proxy.get_device_headers()
    headers = {
        "accept-language": "en-US",
        "authorization": auth_token,
        "ig-intended-user-id": str(user_id),
        "ig-u-ds-user-id": str(user_id),
        "offset": "0",
        "priority": "u=6, i",
        "x-entity-length": str(file_size),
        "x-entity-name": random_upload_id,
        "x-entity-type": "image/png",
        "x-fb-client-ip": "True",
        "x-fb-friendly-name": "undefined:media-upload",
        "x-fb-server-cluster": "True",
        "desired_upload_handler": "doodle_image",
        "image_type": "FILE_ATTACHMENT",
        **device_headers
    }
    
    try:
        with open(image_path, "rb") as img_file:
            response = requests.post(RUPLOAD_URL_TEMPLATE.format(random_upload_id), headers=headers, data=img_file)
            
        if response.status_code == 200:
            return response.json().get("media_id")
    except: pass
    return None

def attach_doodle_step_2(media_id, auth_token, target_thread_id, target_item_id, target_otid):
    device_headers = proxy.get_device_headers()
    
    variables_data = {
        "data": {
            "target_offline_threading_id": target_otid,
            "target_message_item_id": target_item_id,
            "emoji_dropped": None,
            "offline_threading_id": str(random.randint(10**18, 10**19 - 1)),
            "dropped_item_id": str(random.randint(10**18, 10**19 - 1)),
            "action_source": "doodle_drawing",
            "dropped_item_type_id": str(media_id),
            "dropped_item_type": "DOODLE",
            "dropped_item_status": "CREATED",
            "relative_position": {
                "target_message_bubble_layout": {"y_float": 86.0,"width_float": 170.0,"x_float": 56.0,"height_float": 306.0},
                "dropped_item_layout": {"z_index_str": str(int(time.time()*1000)),"y_float": 158.0,"width_float": 100.0,"height_float": 100.0,"scale": 1,"rotation": 0,"x_float": 238.0},
                "target_message_row_width_float": 853.33,
            },
            "ig_thread_igid": target_thread_id
        }
    }
    
    headers = {
        "accept-language": "en-US",
        "authorization": auth_token,
        "content-type": "application/x-www-form-urlencoded",
        **device_headers
    }
    
    try:
        payload = {
            "method": "post", "pretty": "false", "format": "json", "server_timestamps": "true", "locale": "user",
            "fb_api_req_friendly_name": "IGDirectSetDragAndDropItemMutation",
            "client_doc_id": "277994660615315500918604995788", 
            "variables": json.dumps(variables_data)
        }
        requests.post(GRAPHQL_URL, headers=headers, data=payload)
    except: pass