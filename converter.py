import numpy as np
from PIL import Image
import math
import os
import shutil
import random

CHUNK_SIZE = 20 * 1024 * 1024
MIN_DIMENSION = 100

def bytes_to_png(binary_data, output_path):
    try:
        file_len = len(binary_data)
        len_bytes = file_len.to_bytes(4, byteorder='big')
        payload = len_bytes + binary_data

        payload_len = len(payload)
        pixels_needed = math.ceil(payload_len / 3)

        min_pixels = MIN_DIMENSION * MIN_DIMENSION
        if pixels_needed < min_pixels:
            pixels_needed = min_pixels

        width = math.ceil(math.sqrt(pixels_needed))
        height = math.ceil(pixels_needed / width)
        
        total_bytes_needed = width * height * 3
        padding_len = total_bytes_needed - payload_len
        
        payload += b'\x00' * padding_len

        byte_array = np.frombuffer(payload, dtype=np.uint8)
        image_array = byte_array.reshape((height, width, 3))
        
        img = Image.fromarray(image_array, 'RGB')
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"[-] Conversion Error: {e}")
        return False

def prepare_file(filepath):
    if not os.path.exists(filepath): return []
    
    file_size = os.path.getsize(filepath)
    
    if file_size < CHUNK_SIZE and filepath.lower().endswith('.png'):
        pass 

    if file_size < CHUNK_SIZE:
        out_path = filepath + ".png"
        with open(filepath, 'rb') as f:
            if bytes_to_png(f.read(), out_path):
                return [(out_path, True)]
        return []

    print(f"[*] File is {file_size/(1024*1024):.2f} MB. Splitting into 20MB chunks...")
    chunks = []
    part_num = 1
    
    with open(filepath, 'rb') as f:
        while True:
            chunk_data = f.read(CHUNK_SIZE)
            if not chunk_data: break
            
            chunk_name = f"{filepath}.part{part_num}.png"
            if bytes_to_png(chunk_data, chunk_name):
                chunks.append((chunk_name, True))
            else:
                for c, _ in chunks: 
                    if os.path.exists(c): os.remove(c)
                return []
            part_num += 1
            
    return chunks