# DoodleCloud ☁️

> **Turn Instagram into your personal, infinite cloud storage.**

DoodleCloud is a Proof-of-Concept (PoC) tool that uses Instagram's internal API to store unlimited files for free. By converting files into "Visual Noise" images and uploading them as DM doodles, we can bypass file type restrictions and use Instagram's servers as a permanent backend.

![DoodleCloud GUI](https://iili.io/fbvVGPS.jpg)

## 🚀 How It Works

1.  **The Loophole:** Instagram allows users to send "doodles" in Direct Messages. These are essentially PNG images hosted on Facebook's CDN.
2.  **Encoding:** DoodleCloud takes any file (MP3, APK, ZIP, etc.) and converts its binary data into pixels, creating a "Visual Noise" PNG.
3.  **Chunking:** Large files are split into 20MB chunks to ensure high reliability and bypass resolution limits.
4.  **Storage:** These images are uploaded to a private DM thread. The file metadata (filenames, chunk IDs) is stored in a **PostgreSQL** database.
5.  **Retrieval:** When you download a file, the tool fetches the images, reads the pixels back into bytes, and stitches them together to restore your original file perfectly.

## 📦 Features

* **Infinite Storage:** No caps, assuming Instagram doesn't patch the API.
* **Any File Type:** Stores `.exe`, `.apk`, `.mp4`, `.zip`, etc.
* **Database Indexed:** Keeps track of your files remotely using PostgreSQL (NeonDB recommended).
* **Encryption:** Basic obfuscation via image conversion.
* **Dual Interface:**
    * **CLI:** Fast, terminal-based management.
    * **GUI:** Modern Web Dashboard.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/depreciating/DoodleCloud.git
    cd DoodleCloud
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a file named `config.env` in the root folder and add your credentials:
    ```env
    # Instagram Credentials
    INSTA_USER=your_username
    INSTA_PASS=your_password

    # PostgreSQL Database (Neon.tech is free & recommended)
    DB_HOST=your-db-host.neon.tech
    DB_NAME=neondb
    DB_USER=your_db_user
    DB_PASS=your_db_password
    DB_PORT=5432
    ```

## 🖥️ Usage

### Option A: Graphical Interface (GUI)
The recommended way to use DoodleCloud.

1.  Run the web server:
    ```bash
    python gui/app.py
    ```
2.  Open your browser to: `http://127.0.0.1:5000`
3.  **First Run:** Click the **Gear Icon** ⚙️ next to your username to select a target DM thread (create a group with yourself or an alt account).
4.  **Upload:** Drag & drop files into the dashboard.
5.  **Download:** Select files and click Download.

### Option B: Command Line (CLI)
For power users or headless servers.

1.  Run the CLI tool:
    ```bash
    python cli.py
    ```
2.  Follow the interactive menu to Upload, Retrieve, or Delete files.
    * *Note: Files to upload must be placed in the `upload/` folder.*
    * *Note: Downloaded files will appear in the `download/` folder.*

## ⚠️ Disclaimer & Warning

This project is for **Educational Purposes Only**.
* Do not use your main Instagram account. Use a burner account.
* I am not responsible for banned accounts or lost data.

## 👨‍💻 Credits

**Created by [Depreciating](https://github.com/depreciating)**

* **Telegram:** [@depreciatin](https://t.me/depreciatin)
* **Discord:** [Server Invite](https://discord.gg/YNHkj9kVFt)
