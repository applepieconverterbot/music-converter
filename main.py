from flask import Flask, request, render_template_string, redirect
import requests
import os

app = Flask(__name__)

# --- 🎨 MODERN DARK UI ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonicStream | Cloud</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #0f0f0f; --card: #1c1c1c; --accent: #00e5ff; --text: #ffffff; --input: #252525; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', sans-serif; background-color: var(--bg); color: var(--text);
            height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden;
            background-image: radial-gradient(circle at 10% 20%, rgba(0, 229, 255, 0.1) 0%, transparent 20%);
        }
        .container {
            background: rgba(28, 28, 28, 0.8); backdrop-filter: blur(20px); width: 100%; max-width: 500px;
            padding: 40px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 5px; }
        .header span { color: var(--accent); }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
        input, select {
            width: 100%; padding: 14px; background: var(--input); border: 1px solid #333;
            border-radius: 12px; color: white; font-size: 15px; outline: none; transition: 0.2s;
        }
        input:focus, select:focus { border-color: var(--accent); }
        button {
            width: 100%; padding: 16px; background: var(--accent); color: #000; border: none;
            border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 10px;
        }
        button:hover { filter: brightness(110%); transform: translateY(-2px); }
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
            <p style="color:#888; font-size:14px; margin-bottom:30px;">Cloud API Mode</p>
        </div>

        <form action="/convert" method="post" onsubmit="document.getElementById('loader').style.display='flex'">
            
            <div class="input-group">
                <label>YouTube Link</label>
                <input type="text" name="url" placeholder="https://..." required autocomplete="off">
            </div>

            <div class="input-group">
                <label>Format</label>
                <select name="format">
                    <option value="mp3">MP3 (Universal)</option>
                    <option value="best">Best Audio (Original Source)</option>
                    <option value="flac">FLAC (Lossless)</option>
                    <option value="wav">WAV (Uncompressed)</option>
                    <option value="ogg">OGG (Vorbis)</option>
                    <option value="opus">OPUS (High Efficiency)</option>
                </select>
            </div>

            <button type="submit">GET DOWNLOAD LINK</button>
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
    
    # 🚀 USING PUBLIC COBALT API (Wuk.sh instance)
    # This solves the IP Ban and the Crash issues.
    api_url = "https://co.wuk.sh/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Handle "best" format logic
    audio_format = fmt if fmt != 'best' else None

    payload = {
        "url": url,
        "isAudioOnly": True,
        "aFormat": audio_format,
        "isNoTTWatermark": True
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and 'url' in data:
            # Redirect user to the file download directly
            return redirect(data['url'])
        
        elif 'text' in data:
            raise Exception(data['text'])
        else:
            raise Exception("Remote API Error")

    except Exception as e:
        return f"""
        <body style="background:#0f0f0f; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
            <h2 style="color:#ff0033;">API Error</h2>
            <p>{str(e)}</p>
            <p style="color:#888;">The remote server could not handle this link.</p>
            <button onclick="history.back()" style="padding:10px 20px;">Go Back</button>
        </body>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
