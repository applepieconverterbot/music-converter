from flask import Flask, request, render_template_string, redirect
import requests
import random

app = Flask(__name__)

# --- 🎨 RED DARK UI (Pixel Perfect) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonicStream | Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0f0f0f; --card: #1c1c1c; --accent: #ff0033; --text: #ffffff; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Outfit', sans-serif; background-color: var(--bg); color: var(--text); 
            height: 100vh; display: flex; justify-content: center; align-items: center; 
            background-image: radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.1) 0%, transparent 20%); 
        }
        .container { 
            background: rgba(28, 28, 28, 0.8); backdrop-filter: blur(20px); width: 100%; max-width: 500px; 
            padding: 40px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); text-align: center; 
        }
        .header h1 { margin-bottom: 20px; font-size: 28px; }
        .header span { color: var(--accent); }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Fixed Inputs */
        input, select { 
            width: 100%; height: 50px; padding: 0 16px; background: #252525; 
            border: 1px solid #333; border-radius: 12px; color: white; font-size: 15px; 
            outline: none; transition: 0.2s; appearance: none;
        }
        select {
            background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
            background-repeat: no-repeat;
            background-position: right 15px center;
            background-size: 10px;
        }
        input:focus, select:focus { border-color: var(--accent); }
        
        button { 
            width: 100%; padding: 18px; background: var(--accent); color: white; 
            border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 16px;
        }
        button:hover { filter: brightness(110%); }
        
        #loader { display: none; position: absolute; inset: 0; background: rgba(15, 15, 15, 0.95); z-index: 100; flex-direction: column; justify-content: center; align-items: center; border-radius: 24px; }
        .spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 15px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div id="loader"><div class="spinner"></div><h3>Connecting...</h3></div>
        <div class="header"><h1>Sonic<span>Stream</span></h1></div>
        <form action="/convert" method="post" onsubmit="document.getElementById('loader').style.display='flex'">
            <div class="input-group">
                <label>YouTube Link</label>
                <input type="text" name="url" placeholder="Paste link..." required autocomplete="off">
            </div>
            <div class="input-group">
                <label>Format</label>
                <select name="format">
                    <optgroup label="Best Quality">
                        <option value="mp3">MP3 (Universal)</option>
                        <option value="best">Best Audio (Original)</option>
                        <option value="flac">FLAC (Lossless)</option>
                    </optgroup>
                    <optgroup label="Other">
                        <option value="wav">WAV</option>
                        <option value="ogg">OGG</option>
                        <option value="opus">OPUS</option>
                    </optgroup>
                </select>
            </div>
            <button type="submit">DOWNLOAD</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    fmt = request.form.get('format')
    
    # 🚀 SERVER ROTATION LIST (Fixes the "Failed to resolve" error)
    # If wuk.sh is down, it tries cobalt.tools, then others.
    api_servers = [
        "https://api.cobalt.tools/api/json",      # Primary
        "https://cobalt.pog.com.hr/api/json",     # Backup 1
        "https://api.wuk.sh/api/json",            # Backup 2 (The one that failed)
        "https://cobalt.club/api/json"            # Backup 3
    ]
    random.shuffle(api_servers) # Randomize to load balance

    # Headers to look like a real browser
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/"
    }

    # Format Logic
    audio_format = fmt
    if fmt == 'best': audio_format = None

    payload = {
        "url": url,
        "isAudioOnly": True,
        "aFormat": audio_format,
        "isNoTTWatermark": True
    }

    last_error = ""

    # Try every server in the list
    for api_url in api_servers:
        try:
            print(f"Attempting server: {api_url}")
            response = requests.post(api_url, json=payload, headers=headers, timeout=25)
            
            try:
                data = response.json()
            except:
                continue # Bad JSON, skip server

            if response.status_code == 200 and 'url' in data:
                return redirect(data['url']) # Success!
            
            elif 'text' in data:
                last_error = data['text']
                # If invalid link, stop trying (it's the user's fault, not server)
                if "invalid" in last_error.lower(): break 
            
        except Exception as e:
            # Server is dead, loop to next one
            last_error = f"Connection failed to {api_url}"
            continue

    return f"""
    <body style="background:#0f0f0f; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
        <h2 style="color:#ff0033;">API Error</h2>
        <p>All download servers are currently busy.</p>
        <p style="color:#888; font-size:12px;">Last error: {last_error}</p>
        <button onclick="history.back()" style="padding:10px 20px; background:#333; color:white; border:none; cursor:pointer;">Go Back</button>
    </body>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
