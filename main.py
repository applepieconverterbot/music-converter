from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import time
import subprocess

app = Flask(__name__)

# --- 🎨 MODERN DARK UI (HTML/CSS) ---
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
        :root {
            --bg: #0f0f0f;
            --card: #1c1c1c;
            --accent: #ff0033;
            --text: #ffffff;
            --text-gray: #aaaaaa;
            --input: #252525;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.1) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(50, 50, 255, 0.05) 0%, transparent 20%);
        }

        .container {
            background: rgba(28, 28, 28, 0.8);
            backdrop-filter: blur(20px);
            width: 100%;
            max-width: 500px;
            padding: 40px;
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            animation: floatUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
            position: relative;
        }

        @keyframes floatUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 28px; font-weight: 700; letter-spacing: -1px; }
        .header span { color: var(--accent); }
        .header p { color: var(--text-gray); font-size: 14px; margin-top: 5px; }

        label {
            display: block;
            margin-bottom: 8px;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-gray);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .input-group { position: relative; margin-bottom: 25px; }
        
        .input-group i {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #666;
        }

        input, select {
            width: 100%;
            padding: 16px 16px 16px 45px;
            background: var(--input);
            border: 1px solid #333;
            border-radius: 12px;
            color: white;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.2s;
            outline: none;
        }
        
        select { padding-left: 16px; appearance: none; cursor: pointer; }

        input:focus, select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(255, 0, 51, 0.1);
        }

        button {
            width: 100%;
            padding: 18px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 10px 20px -5px rgba(255, 0, 51, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 25px -5px rgba(255, 0, 51, 0.5);
            filter: brightness(110%);
        }

        /* Loading Overlay */
        #loader {
            display: none;
            position: absolute;
            inset: 0;
            background: rgba(15, 15, 15, 0.95);
            border-radius: 24px;
            z-index: 100;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin { to { transform: rotate(360deg); } }

    </style>
</head>
<body>

    <div class="container">
        <!-- Loader -->
        <div id="loader">
            <div class="spinner"></div>
            <h3 style="font-size: 18px;">Converting Audio</h3>
            <p style="font-size: 13px; color: #666; margin-top: 5px;">This takes about 15-30 seconds...</p>
        </div>

        <div class="header">
            <h1>Sonic<span>Stream</span></h1>
            <p>High-Fidelity Audio Extraction</p>
        </div>

        <form action="/convert" method="post" onsubmit="document.getElementById('loader').style.display='flex'">
            
            <div class="input-group">
                <label>YouTube Link</label>
                <i class="fa-solid fa-link"></i>
                <input type="text" name="url" placeholder="https://music.youtube.com/..." required autocomplete="off">
            </div>

            <div class="input-group">
                <label>Target Format</label>
                <select name="format">
                    <optgroup label="✨ Best Quality (Recommended)">
                        <option value="m4a" selected>M4A (AAC) - Best for Apple/Mobile</option>
                        <option value="mp3">MP3 (320kbps) - Universal</option>
                        <option value="flac">FLAC - Lossless Quality</option>
                        <option value="wav">WAV - Uncompressed</option>
                        <option value="opus">OPUS - High Efficiency</option>
                    </optgroup>

                    <optgroup label="🎧 Audiophile">
                        <option value="alac">ALAC - Apple Lossless</option>
                        <option value="aiff">AIFF - Studio Standard</option>
                        <option value="ape">APE - Monkey's Audio</option>
                        <option value="wv">WV - WavPack</option>
                        <option value="tta">TTA - True Audio</option>
                        <option value="rf64">RF64 - WAV Successor</option>
                    </optgroup>

                    <optgroup label="📞 Telephony & Retro (Low Quality)">
                        <option value="amr">AMR - Speech</option>
                        <option value="gsm">GSM - Mobile 2G</option>
                        <option value="vox">VOX - ADPCM</option>
                        <option value="8svx">8SVX - Amiga 8-bit</option>
                    </optgroup>
                    
                    <optgroup label="💾 Legacy">
                        <option value="wma">WMA - Windows Media</option>
                        <option value="ogg">OGG - Vorbis</option>
                        <option value="mp2">MP2 - MPEG Layer II</option>
                        <option value="mpc">MPC - Musepack</option>
                        <option value="3gp">3GP - Low Data Mobile</option>
                    </optgroup>
                </select>
            </div>

            <button type="submit">DOWNLOAD AUDIO</button>
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
    
    timestamp = int(time.time())
    # We convert to WAV first as an intermediary to allow complex format changes
    temp_wav = f"/tmp/{timestamp}_temp.wav"
    final_output = f"/tmp/{timestamp}.{fmt}"

    # CHECK FOR COOKIES FILE
    # You must upload 'cookies.txt' to your GitHub repo for this to work!
    cookie_args = {}
    if os.path.exists('cookies.txt'):
        cookie_args = {'cookiefile': 'cookies.txt'}

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'/tmp/{timestamp}_temp.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        **cookie_args, # Inject cookies if file exists
        
        # 👇 THE 2026 FIX: Force "Android Music" Client 👇
        # This is the secret weapon to bypass the "Sign in" web error
        'extractor_args': {
            'youtube': {
                'player_client': ['android_music', 'android_creator'],
                'player_skip': ['web', 'ios', 'tv', 'android']
            }
        },
        
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}],
    }

    try:
        # 1. Download Source
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio_converted')
            # Sanitize filename
            clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' -_']).strip()

        # 2. Convert using FFmpeg
        # We start building the command
        ffmpeg_cmd = ['ffmpeg', '-y', '-i', temp_wav]

        # --- FORMAT LOGIC ---
        # High Quality / Standard
        if fmt == 'mp3':
            ffmpeg_cmd.extend(['-b:a', '320k'])
        elif fmt in ['aac', 'm4a']:
            ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', '256k'])
        elif fmt == 'opus':
            ffmpeg_cmd.extend(['-c:a', 'libopus', '-b:a', '192k'])
        elif fmt == 'ogg':
            ffmpeg_cmd.extend(['-c:a', 'libvorbis', '-q:a', '10'])
        elif fmt == 'wma':
            ffmpeg_cmd.extend(['-c:a', 'wmav2', '-b:a', '192k'])
        
        # Telephony / Retro (MUST be low sample rate or FFmpeg crashes)
        elif fmt == 'amr':
            ffmpeg_cmd.extend(['-ar', '8000', '-ac', '1', '-c:a', 'libopencore_amrnb'])
        elif fmt == 'gsm':
            ffmpeg_cmd.extend(['-ar', '8000', '-ac', '1', '-c:a', 'gsm'])
        elif fmt == 'vox':
            ffmpeg_cmd.extend(['-f', 'u8', '-c:a', 'pcm_u8', '-ar', '8000', '-ac', '1'])
        elif fmt == '8svx':
            ffmpeg_cmd.extend(['-c:a', 'pcm_s8', '-f', 'iff'])
        elif fmt == 'rf64':
             ffmpeg_cmd.extend(['-f', 'rf64'])

        # Lossless / Others (Defaults are fine)
        elif fmt in ['flac', 'wav', 'alac', 'aiff', 'ape', 'wv', 'tta', 'mpc', '3gp', 'mp2']: 
            pass 
        
        ffmpeg_cmd.append(final_output)

        # Execute conversion
        subprocess.run(ffmpeg_cmd, check=True)

        # 3. Send to user
        return send_file(final_output, as_attachment=True, download_name=f"{clean_title}.{fmt}")

    except Exception as e:
        error_msg = str(e)
        
        # Friendly Error Page
        return f"""
        <body style="background:#0f0f0f; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; text-align:center;">
            <div style="background:#1c1c1c; padding:40px; border-radius:20px; border:1px solid #333; max-width:500px;">
                <h2 style="color:#ff0033; margin-bottom:15px;">⚠️ Conversion Failed</h2>
                <p style="color:#ccc; margin-bottom:20px;">{error_msg}</p>
                
                {'<div style="background:#332200; color:#ffaa00; padding:15px; border-radius:10px; font-size:13px; margin-bottom:20px;"><strong>TIP:</strong> The server was blocked by YouTube. You must upload a <code>cookies.txt</code> file to your GitHub repository to fix this.</div>' if 'Sign in' in error_msg else ''}
                
                <button onclick="history.back()" style="background:#333; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer;">Go Back</button>
            </div>
        </body>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
