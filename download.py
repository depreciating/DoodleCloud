import requests
import proxy
import numpy as np
from PIL import Image
from io import BytesIO
import os

FALLBACK_URL = "https://i.instagram.com/api/v1/direct_v2/media_fallback/?entity_id={}&entity_type=59"
DOWNLOAD_DIR = "download"

def deconvert_chunk(image_data):
    try:
        img = Image.open(BytesIO(image_data)).convert('RGB')
        flat_bytes = np.array(img).tobytes()
        file_size = int.from_bytes(flat_bytes[:4], byteorder='big')
        
        if file_size <= 0 or file_size > len(flat_bytes): return None
        return flat_bytes[4 : 4 + file_size]
    except: return None

def download_file(media_ids, filename, is_converted, auth_token):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    save_path = os.path.join(DOWNLOAD_DIR, filename)

    headers = {
        "User-Agent": proxy.get_device_headers()['User-Agent'],
        "Authorization": auth_token
    }
    
    with open(save_path, "wb") as f_out:
        
        total = len(media_ids)
        print(f"[*] Downloading {total} chunk(s) to '{DOWNLOAD_DIR}/'...")

        for i, mid in enumerate(media_ids, 1):
            url = FALLBACK_URL.format(mid)
            try:
                print(f"    - Chunk {i}/{total}...", end="\r")
                resp = requests.get(url, headers=headers, allow_redirects=True)
                
                if resp.status_code != 200:
                    print(f"\n[-] Failed to download chunk {i}. Aborting.")
                    return

                if is_converted:
                    data = deconvert_chunk(resp.content)
                    if data is None:
                        print(f"\n[-] Failed to deconvert chunk {i}.")
                        return
                    f_out.write(data)
                else:
                    f_out.write(resp.content)
                    
            except Exception as e:
                print(f"\n[-] Network error on chunk {i}: {e}")
                return

    print(f"\n[+] Download Complete: {save_path}")