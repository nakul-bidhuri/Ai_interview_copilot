import streamlit.components.v1 as components
import json

def render_walkie_talkie_widget(
    current_question: str,
    candidate_name: str = "Candidate",
    interviewer_persona: str = "Interviewer",
    auto_speak: bool = True
):
    """
    Renders an interactive Walkie-Talkie audio widget using HTML5 Web Speech API.
    Provides:
    1. Realistic Walkie-Talkie radio interface with sound effect chirps.
    2. Text-to-Speech (TTS) for the interviewer question.
    3. Push-to-Talk Speech Recognition (STT) for the student's live answer.
    4. Copies transcribed text directly into candidate answer flow.
    """
    escaped_question = json.dumps(current_question)
    escaped_name = json.dumps(candidate_name)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          background: transparent;
          color: #ffffff;
        }}
        .walkie-container {{
          background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
          border: 2px solid #334155;
          border-radius: 18px;
          padding: 20px;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
          max-width: 100%;
          box-sizing: border-box;
        }}
        .walkie-header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
          border-bottom: 1px solid #334155;
          padding-bottom: 10px;
        }}
        .walkie-channel {{
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          font-weight: 600;
          letter-spacing: 0.5px;
          color: #38bdf8;
          text-transform: uppercase;
        }}
        .channel-dot {{
          width: 10px;
          height: 10px;
          background-color: #10b981;
          border-radius: 50%;
          box-shadow: 0 0 8px #10b981;
          animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
          0% {{ opacity: 0.4; }}
          50% {{ opacity: 1; }}
          100% {{ opacity: 0.4; }}
        }}
        .walkie-screen {{
          background: #090d16;
          border: 1px solid #1e293b;
          border-radius: 12px;
          padding: 14px;
          min-height: 80px;
          margin-bottom: 18px;
          font-size: 14px;
          line-height: 1.5;
          color: #e2e8f0;
          position: relative;
        }}
        .screen-badge {{
          display: inline-block;
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 4px;
          background: #0284c7;
          color: white;
          font-weight: bold;
          margin-bottom: 6px;
        }}
        .live-transcript {{
          color: #38bdf8;
          font-style: italic;
          margin-top: 6px;
          min-height: 20px;
        }}
        .walkie-controls {{
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          align-items: center;
        }}
        .btn {{
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-weight: 600;
          font-size: 14px;
          padding: 10px 18px;
          border-radius: 12px;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
        }}
        .btn-ai-speak {{
          background: linear-gradient(135deg, #2563eb, #1d4ed8);
          color: white;
        }}
        .btn-ai-speak:hover {{
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          transform: translateY(-2px);
        }}
        .btn-push-to-talk {{
          background: linear-gradient(135deg, #ef4444, #dc2626);
          color: white;
          font-size: 15px;
          padding: 12px 24px;
          box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
        }}
        .btn-push-to-talk.recording {{
          background: linear-gradient(135deg, #10b981, #059669);
          box-shadow: 0 0 18px rgba(16, 185, 129, 0.6);
          animation: micPulse 1s infinite;
        }}
        @keyframes micPulse {{
          0% {{ transform: scale(1); }}
          50% {{ transform: scale(1.04); }}
          100% {{ transform: scale(1); }}
        }}
        .btn-copy {{
          background: #334155;
          color: #e2e8f0;
          font-size: 13px;
        }}
        .btn-copy:hover {{
          background: #475569;
        }}
        .instruction-bar {{
          font-size: 12px;
          color: #94a3b8;
          margin-top: 10px;
        }}
      </style>
    </head>
    <body>
      <div class="walkie-container">
        <div class="walkie-header">
          <div class="walkie-channel">
            <div class="channel-dot" id="statusDot"></div>
            <span>WALKIE-TALKIE MODE // CHANNEL 1</span>
          </div>
          <span style="font-size: 12px; color: #94a3b8;">AI Voice: Active</span>
        </div>

        <div class="walkie-screen">
          <div class="screen-badge" id="speakerLabel">🎙️ AI Interviewer</div>
          <div id="statusMessage" style="color: #cbd5e1;">Click "🔊 Hear Question" or press Push-to-Talk to respond.</div>
          <div class="live-transcript" id="liveTranscript"></div>
        </div>

        <div class="walkie-controls">
          <button class="btn btn-ai-speak" id="btnSpeak">
            🔊 Hear Question Out Loud
          </button>
          
          <button class="btn btn-push-to-talk" id="btnMic">
            🎙️ Hold / Tap to Speak (Walkie-Talkie)
          </button>

          <button class="btn btn-copy" id="btnCopy" style="display: none;">
            📋 Copy Spoken Answer
          </button>
        </div>

        <div class="instruction-bar">
          💡 <b>Tip:</b> Click <b>Hear Question</b> to listen. When ready, click <b>Tap to Speak</b>, speak your answer into your mic, and click again to finish. Your transcribed answer will be pasted into the box below!
        </div>
      </div>

      <script>
        const questionText = {escaped_question};
        const candidateName = {escaped_name};
        const autoPlay = {"true" if auto_speak else "false"};

        const btnSpeak = document.getElementById('btnSpeak');
        const btnMic = document.getElementById('btnMic');
        const btnCopy = document.getElementById('btnCopy');
        const liveTranscript = document.getElementById('liveTranscript');
        const statusMessage = document.getElementById('statusMessage');
        const speakerLabel = document.getElementById('speakerLabel');
        const statusDot = document.getElementById('statusDot');

        let isRecording = false;
        let recognition = null;
        let accumulatedTranscript = "";

        // Web Audio Chirp Generator for Walkie-Talkie Radio effect
        function playChirp(freq1, freq2) {{
          try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.setValueAtTime(freq1, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(freq2, ctx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.15, ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.1);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.1);
          }} catch(e) {{}}
        }}

        // Text-to-Speech
        function speakQuestion() {{
          if (!('speechSynthesis' in window)) {{
            alert("Sorry, your browser doesn't support Text-to-Speech.");
            return;
          }}
          window.speechSynthesis.cancel();
          playChirp(800, 1200);

          const utterance = new SpeechSynthesisUtterance(questionText);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;

          const voices = window.speechSynthesis.getVoices();
          const englishVoice = voices.find(v => v.lang.startsWith('en')) || voices[0];
          if (englishVoice) utterance.voice = englishVoice;

          speakerLabel.innerText = "🔊 AI Interviewer Speaking...";
          speakerLabel.style.background = "#2563eb";
          statusDot.style.backgroundColor = "#38bdf8";
          statusDot.style.boxShadow = "0 0 10px #38bdf8";

          utterance.onend = () => {{
            playChirp(1200, 800);
            speakerLabel.innerText = "✅ Over to you!";
            speakerLabel.style.background = "#10b981";
            statusDot.style.backgroundColor = "#10b981";
            statusDot.style.boxShadow = "0 0 8px #10b981";
          }};

          window.speechSynthesis.speak(utterance);
        }}

        // Speech Recognition (Push-to-Talk)
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {{
          recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onstart = () => {{
            isRecording = true;
            btnMic.classList.add('recording');
            btnMic.innerText = "🛑 Stop & Finish Speaking";
            speakerLabel.innerText = "🎙️ You Are Speaking (Live)...";
            speakerLabel.style.background = "#ef4444";
            statusMessage.innerText = "Listening to your answer. Speak clearly...";
            playChirp(700, 1400);
          }};

          recognition.onresult = (event) => {{
            let interim = "";
            let final = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
              if (event.results[i].isFinal) {{
                accumulatedTranscript += " " + event.results[i][0].transcript;
              }} else {{
                interim += event.results[i][0].transcript;
              }}
            }}
            liveTranscript.innerText = (accumulatedTranscript + " " + interim).trim();
            btnCopy.style.display = "inline-flex";

            // Attempt to sync into parent Streamlit text area if accessible
            try {{
              const parentDoc = window.parent.document;
              const textareas = parentDoc.querySelectorAll('textarea');
              if (textareas.length > 0) {{
                const targetArea = textareas[textareas.length - 1];
                targetArea.value = (accumulatedTranscript + " " + interim).trim();
                targetArea.dispatchEvent(new Event('input', {{ bubbles: true }}));
              }}
            }} catch(err) {{}}
          }};

          recognition.onerror = (event) => {{
            console.error("Speech recognition error:", event.error);
            speakerLabel.innerText = "⚠️ Microphone Error";
            statusMessage.innerText = "Error: " + event.error + ". You can also type your answer below.";
            isRecording = false;
            btnMic.classList.remove('recording');
            btnMic.innerText = "🎙️ Hold / Tap to Speak (Walkie-Talkie)";
          }};

          recognition.onend = () => {{
            isRecording = false;
            btnMic.classList.remove('recording');
            btnMic.innerText = "🎙️ Hold / Tap to Speak (Walkie-Talkie)";
            speakerLabel.innerText = "📻 Roger that! Answer captured.";
            speakerLabel.style.background = "#10b981";
            playChirp(1400, 700);
          }};
        }} else {{
          btnMic.innerText = "⚠️ Speech Recognition Not Supported in this browser";
          btnMic.disabled = true;
        }}

        btnSpeak.addEventListener('click', speakQuestion);

        btnMic.addEventListener('click', () => {{
          if (!recognition) return;
          if (!isRecording) {{
            accumulatedTranscript = "";
            liveTranscript.innerText = "";
            try {{
              recognition.start();
            }} catch(e) {{
              console.log(e);
            }}
          }} else {{
            recognition.stop();
          }}
        }});

        btnCopy.addEventListener('click', () => {{
          const text = liveTranscript.innerText;
          if (text) {{
            navigator.clipboard.writeText(text);
            btnCopy.innerText = "✅ Copied to Clipboard!";
            setTimeout(() => {{
              btnCopy.innerText = "📋 Copy Spoken Answer";
            }}, 2000);
          }}
        }});

        if (autoPlay) {{
          setTimeout(speakQuestion, 600);
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=270, scrolling=False)
