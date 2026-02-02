import time
import os
import json
import auth
import upload
import converter
import download
import database
from config_loader import CONF

USERNAME = CONF.get("INSTA_USER")
PASSWORD = CONF.get("INSTA_PASS")
UPLOAD_DIR = "upload"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_upload(auth_token, user_id, client):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print(f"[*] Created directory: '{UPLOAD_DIR}'")
        print(f"[*] Please put your files into the '{UPLOAD_DIR}' folder and try again.")
        input("\nPress Enter to return to menu...")
        return

    thread_id = auth.get_cached_thread(USERNAME)
    if not thread_id:
        print("[*] No target thread found.")
        thread_id = auth.select_target_thread(client)
        if thread_id: auth.update_cache(USERNAME, thread_id=thread_id)
        else: return

    while True:
        ignored = ['.DS_Store', '.gitkeep']
        try:
            files = [f for f in os.listdir(UPLOAD_DIR) 
                     if os.path.isfile(os.path.join(UPLOAD_DIR, f)) 
                     and not f.startswith('.') 
                     and f not in ignored]
        except Exception as e:
            print(f"[-] Error reading directory: {e}")
            return

        print("\n=== UPLOAD MENU ===")
        if not files:
            print(f"[-] No files found in '{UPLOAD_DIR}/'.")
            input("Press Enter to return...")
            return

        for i, f in enumerate(files, 1): 
            fpath = os.path.join(UPLOAD_DIR, f)
            size = os.path.getsize(fpath) / (1024*1024)
            print(f"{i}. {f} ({size:.2f} MB)")
        
        print("E. Back to Main Menu")

        try:
            choice_str = input("\nEnter file numbers (e.g. 1,3) or 'E': ").strip()
            if choice_str.lower() == 'e': break
            
            targets = []
            parts = choice_str.split(',')
            for p in parts:
                if p.strip().isdigit():
                    idx = int(p.strip()) - 1
                    if 0 <= idx < len(files): targets.append(files[idx])

            if not targets:
                print("[-] Invalid")
                continue

            for filename in targets:
                full_path = os.path.join(UPLOAD_DIR, filename)
                
                upload_list = converter.prepare_file(full_path)
                if not upload_list:
                    print(f"[-] Error converting {filename}")
                    continue

                uploaded_media_ids = []
                abort = False
                total_chunks = len(upload_list)

                print(f"[*] Uploading {filename} ({total_chunks} parts)...")

                for idx, (path, is_temp) in enumerate(upload_list, 1):
                    item_id, otid = auth.get_random_message(client, thread_id)
                    
                    if item_id:
                        print(f"    - Part {idx}/{total_chunks}...", end="\r")
                        mid = upload.upload_image_step_1(auth_token, user_id, path)
                        
                        if mid:
                            time.sleep(1.5)
                            upload.attach_doodle_step_2(mid, auth_token, thread_id, item_id, otid)
                            uploaded_media_ids.append(mid)
                        else:
                            print(f"\n[-] Failed to upload part {idx}.")
                            abort = True
                            break
                    else:
                        print("\n[-] Failed to get message target.")
                        abort = True
                        break
                    
                    if is_temp and os.path.exists(path): os.remove(path)
                    time.sleep(1.5)

                if not abort and len(uploaded_media_ids) == total_chunks:
                    was_converted = any(u[1] for u in upload_list)
                    database.save_file_record(filename, uploaded_media_ids, was_converted)
                    print(f"\n[+] Successfully Clouded: {filename}")
                else:
                    print(f"\n[-] Upload incomplete for {filename}")

        except ValueError: print("[-] Invalid")
        except KeyboardInterrupt: break

def menu_retrieve(auth_token):
    while True:
        files = database.list_files()
        print("\n=== RETRIEVE FILES ===")
        if not files: 
            print("[-] Database empty.")
            return

        for i, r in enumerate(files, 1):
            chunk_count = len(json.loads(r['media_ids']))
            print(f"{i}. {r['filename']} ({chunk_count} parts)")
        
        print("E. Back to Main Menu")
        
        try:
            val = input("\nSelect file number or 'E': ").strip()
            if val.lower() == 'e': break

            if val.isdigit():
                idx = int(val) - 1
                if 0 <= idx < len(files):
                    t = files[idx]
                    mids = json.loads(t['media_ids'])
                    download.download_file(mids, t['filename'], t['is_converted'], auth_token)
                else: print("[-] Invalid")
            else: print("[-] Invalid")
        except Exception as e: print(f"[-] Error: {e}")

def menu_delete():
    while True:
        files = database.list_files()
        print("\n=== DELETE FILES ===")
        if not files: 
            print("[-] Database empty.")
            return

        for i, r in enumerate(files, 1):
            print(f"{i}. {r['filename']}")
        print("E. Back to Main Menu")
        
        try:
            val = input("\nDelete # or 'E': ").strip()
            if val.lower() == 'e': break

            if val.isdigit():
                idx = int(val) - 1
                if 0 <= idx < len(files):
                    target = files[idx]
                    confirm = input(f"Delete '{target['filename']}'? (y/n): ")
                    if confirm.lower() == 'y':
                        if database.delete_file_record(target['id']):
                            print("[+] Deleted successfully.")
                        else: print("[-] Delete failed.")
                else: print("[-] Invalid")
            else: print("[-] Invalid")
        except: print("[-] Invalid")

def main():
    clear_screen()
    if not USERNAME or not PASSWORD:
        return print("[-] Error: Credentials missing in config.env")

    print(f"[*] Connecting as {USERNAME}...")
    token, uid, cl = auth.login_smart(USERNAME, PASSWORD)
    if not token: return print("[-] Login failed.")
    
    clear_screen()
    print(f"[+] Logged in as {USERNAME}")

    while True:
        print("\n=== INSTA CLOUD ===")
        print("1. Upload")
        print("2. Retrieve")
        print("3. Delete")
        print("4. Exit")
        
        opt = input("Option: ").strip()
        if opt == "1": menu_upload(token, uid, cl)
        elif opt == "2": menu_retrieve(token)
        elif opt == "3": menu_delete()
        elif opt == "4": 
            print("Bye!")
            break
        else: print("[-] Invalid")

if __name__ == "__main__":
    main()