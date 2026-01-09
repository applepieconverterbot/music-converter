from flask import Flask, request, render_template_string, redirect
import requests
import os

app = Flask(__name__)

# --- 🎨 FIXED RED UI ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonicStream | Pro Converter</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #0f0f0f; --card: #1c1c1c; --accent: #ff0033; --text: #ffffff; }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: 'Outfit', sans-serif; 
            background-color: var(--bg); 
            color: var(--text); 
            height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            background-image: radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.1) 0%, transparent 20%); 
        }
        
        .container { 
            background: rgba(28, 28, 28, 0.8); 
            backdrop-filter: blur(20px); 
            width: 100%; 
            max-width: 500px; 
            padding: 40px; 
            border-radius: 24px; 
            border: 1px solid rgba(255,255,255,0.05); 
            text-align: center; 
        }
        
        .header h1 { margin-bottom: 20px; font-size: 28px; }
        .header span { color: var(--accent); }
        
        .input-group { margin-bottom: 20px; text-align: left; width: 100%; }
        
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-size: 12px; 
            font-weight: 700; 
            color: #aaa; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
        }
        
        /* 👇 THE FIX: Force identical sizing for Input and Select 👇 */
        input, select { 
            width: 100%; 
            display: block;
            height: 50px; /* Exact height for both */
            padding: 0 16px; 
            background: #252525; 
            border: 1px solid #333; 
            border-radius: 12px; 
            color: white; 
            font-size: 15px; 
            font-family: inherit;
            outline: none; 
            transition: 0.2s; 
            appearance: none; /* Removes default OS styling issues */
        }
        
        /* Add custom arrow for Select because we removed default appearance */
        select {
            background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
            background-repeat: no-repeat;
            background-position: right 15px center;
            background-size: 10px;
        }

        input:focus, select:focus { border-color: var(--accent); }
        
        button { 
            width: 100%; 
            padding: 18px; 
            background: var(--accent); 
            color: white; 
            border: none; 
            border-radius: 12px; 
            font-weight: 700; 
            font-size: 16px;
            cursor: pointer; 
        }
        button:hover { filter: brightness(110%); }
        
        #loader { display: none; position: absolute; inset: 0; background: rgba(15, 15, 15, 0.95); z-index: 100; flex-direction: column; justify-content: center; align-items: center; border-radius: 24px; }
        .spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 15px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div id="loader"><div class="spinner"></div><h3>Connecting to Cloud...</h3></div>
        <div class="header">
            <h1>Sonic<span>Stream</span></h1>
        </div>
        <form action="/convert" method="post" onsubmit="document.getElementById('loader').style.display='flex'">
            <div class="input-group">
                <label>YouTube Link</label>
                <input type="text" name="url" placeholder="Paste YouTube Link..." required autocomplete="off">
            </div>
            <div class="input-group">
                <label>Target Format</label>
                <select name="format">
                    <optgroup label="Best Quality">
                        <option value="mp3">MP3 (Universal)</option>
                        <option value="best">Best Audio (Source Quality)</option>
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
    
    # 🚀 API LIST (Failover System)
    # If one server is down, it tries the next one automatically.
    api_servers = [
        "https://api.cobalt.tools/api/json",      # Official
        "https://cobalt.pog.com.hr/api/json",     # Backup 1
        "https://api.wuk.sh/api/json",            # Backup 2
        "https://cobalt.club/api/json"            # Backup 3
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "SonicStream-Client/1.0"
    }

    # Format Logic
    audio_format = fmt
    if fmt == 'best':
        audio_format = None

    payload = {
        "url": url,
        "isAudioOnly": True,
        "aFormat": audio_format,
        "isNoTTWatermark": True
    }

    last_error = ""

    # Loop through servers until one works
    for api_url in api_servers:
        try:
            print(f"Trying server: {api_url}...")
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            data = response.json()

            if response.status_code == 200 and 'url' in data:
                return redirect(data['url'])
            
            elif 'text' in data:
                last_error = data['text']
                if "invalid" in last_error.lower(): break 
            
        except Exception as e:
            last_error = f"Connection failed to {api_url}"
            continue

    return f"""
    <body style="background:#0f0f0f; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
        <h2 style="color:#ff0033;">API Error</h2>
        <p>All remote servers are currently busy.</p>
        <p style="color:#888; font-size:12px;">Last error: {last_error}</p>
        <button onclick="history.back()" style="padding:10px 20px; background:#333; color:white; border:none; cursor:pointer;">Go Back</button>
    </body>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
