let currentFiles = [];
let selectedFiles = new Set();

document.addEventListener("DOMContentLoaded", () => {
    checkStatus();
    loadFiles();
});

const fileInput = document.getElementById('fileInput');

// 1. Status Check
async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const badge = document.getElementById('statusIndicator');
        
        if (data.status === 'connected') {
            badge.className = 'badge badge-online';
            badge.innerHTML = `<i class="fas fa-user-circle"></i> ${data.username}`;
            
            // Auto-prompt if no thread is selected
            if (data.thread_selected === false) {
                setTimeout(openThreadDialog, 500);
            }
        } else {
            badge.innerHTML = "Disconnected";
        }
    } catch (e) { console.error(e); }
}

// 2. Thread Selection Logic
async function openThreadDialog() {
    const dialog = document.getElementById('threadDialog');
    const list = document.getElementById('threadList');
    dialog.showModal();
    
    list.innerHTML = '<div style="text-align:center; color:#aaa;"><i class="fas fa-circle-notch fa-spin"></i> Loading chats...</div>';

    try {
        const res = await fetch('/api/threads');
        const threads = await res.json();
        
        list.innerHTML = '';
        if (threads.length === 0) {
            list.innerHTML = '<div style="padding:10px;">No chats found.</div>';
            return;
        }

        threads.forEach(t => {
            const div = document.createElement('div');
            div.className = 'thread-item';
            div.innerHTML = `<i class="fas fa-comments" style="color:#aaa; margin-right:10px;"></i> ${t.title}`;
            div.onclick = () => selectThread(t.id, t.title);
            list.appendChild(div);
        });

    } catch (e) {
        list.innerHTML = '<div style="color:var(--danger);">Failed to load chats.</div>';
    }
}

async function selectThread(id, title) {
    try {
        const res = await fetch('/api/threads', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({thread_id: id})
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            document.getElementById('threadDialog').close();
            alert(`Selected: ${title}`);
        }
    } catch (e) { alert("Selection failed"); }
}

// 3. Load Files
async function loadFiles() {
    const grid = document.getElementById('fileGrid');
    
    try {
        const res = await fetch('/api/files');
        currentFiles = await res.json();
        selectedFiles.clear();
        updateToolbar();

        grid.innerHTML = '';
        if (currentFiles.length === 0) {
            grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:#444;margin-top:20px;">No files found.</div>';
            return;
        }

        currentFiles.forEach(file => {
            const date = new Date(file.created_at * 1000).toLocaleDateString();
            const ext = file.filename.split('.').pop().toLowerCase();
            let icon = 'fas fa-file';
            
            if (['jpg','png','gif'].includes(ext)) icon = 'fas fa-file-image';
            else if (['mp3','wav'].includes(ext)) icon = 'fas fa-file-audio';
            else if (['mp4','mov'].includes(ext)) icon = 'fas fa-file-video';
            else if (['zip','rar'].includes(ext)) icon = 'fas fa-file-archive';
            else if (['pdf','txt'].includes(ext)) icon = 'fas fa-file-alt';
            else if (['apk'].includes(ext)) icon = 'fab fa-android';

            const card = document.createElement('div');
            card.className = 'file-card';
            card.onclick = () => toggleSelect(file.id, card);
            card.innerHTML = `
                <div class="parts-tag">${file.parts} Parts</div>
                <div class="file-icon"><i class="${icon}"></i></div>
                <div class="file-name">${file.filename}</div>
                <div class="file-meta">${date}</div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        grid.innerHTML = '<div style="color:var(--danger);text-align:center;">Failed to load files</div>';
    }
}

// 4. Selection Logic
function toggleSelect(id, cardElement) {
    if (selectedFiles.has(id)) {
        selectedFiles.delete(id);
        cardElement.classList.remove('selected');
    } else {
        selectedFiles.add(id);
        cardElement.classList.add('selected');
    }
    updateToolbar();
}

function updateToolbar() {
    const count = selectedFiles.size;
    document.getElementById('selectionCount').innerText = `${count} selected`;
    document.getElementById('btnDelete').style.display = count > 0 ? 'inline-flex' : 'none';
    document.getElementById('btnDownload').style.display = count > 0 ? 'inline-flex' : 'none';
}

// 5. Batch Upload Logic
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleBatchUpload(e.target.files);
});

async function handleBatchUpload(files) {
    if (files.length > 5) {
        alert("You can only upload up to 5 files at a time!");
        fileInput.value = ""; // Reset input
        return;
    }
    
    const dialog = document.getElementById('uploadDialog');
    const txt = document.getElementById('uploadText');
    dialog.showModal();
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        txt.innerText = `Processing ${i + 1}/${files.length}: ${file.name}...`;
        
        try {
            await processSingleUpload(file);
        } catch (e) {
            console.error(e);
            alert(`Failed to upload ${file.name}: ${e}`);
        }
    }
    
    dialog.close();
    fileInput.value = ""; // Reset input
    loadFiles();
}

async function processSingleUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    const data = await res.json();
    
    if (data.status !== 'success') {
        if (data.error === "NO_THREAD_SELECTED") {
            throw "No chat thread selected (Check settings)";
        } else {
            throw data.error;
        }
    }
}

// 6. Batch Download Logic
async function downloadSelected() {
    if (selectedFiles.size > 5) {
        alert("You can only download up to 5 files at a time!");
        return;
    }
    
    const btn = document.getElementById('btnDownload');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Processing...`;
    
    const ids = Array.from(selectedFiles);
    
    for (const id of ids) {
        // Find the full file object
        // Note: Check type consistency (string vs int)
        const targetFile = currentFiles.find(f => String(f.id) === String(id));
        if (!targetFile) continue;

        try {
            const res = await fetch('/api/download', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(targetFile)
            });
            const data = await res.json();
            
            if (data.status !== 'success') {
                console.error(`Error downloading ${targetFile.filename}: ${data.error}`);
            }
        } catch (e) {
            console.error(`Network error on ${targetFile.filename}`);
        }
    }
    
    alert("Batch download complete! Check your 'download/' folder.");
    selectedFiles.clear();
    updateToolbar();
    
    // Restore button text
    btn.innerHTML = originalText;
    
    // Refresh grid to clear selection visually
    loadFiles();
}

// 7. Delete Logic (Already supports batch, just cleanup)
async function deleteSelected() {
    if (!confirm(`Delete ${selectedFiles.size} file(s)?`)) return;

    const btn = document.getElementById('btnDelete');
    btn.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Deleting...`;

    for (let id of selectedFiles) {
        await fetch('/api/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id})
        });
    }
    
    loadFiles();
}