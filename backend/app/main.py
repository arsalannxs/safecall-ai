import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.audio_processor import AudioProcessor
from app.services.ai_detector import DeepfakeDetector
from app.services.intent_scanner import IntentScanner

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core AI Engines
audio_processor = AudioProcessor()
deepfake_detector = DeepfakeDetector(threshold=0.75)
intent_scanner = IntentScanner()

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "engine": "Deepfake + Intent Multi-Modal Engine"
    }

@app.websocket("/ws/stream")
async def audio_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[SERVER] Client connected to Unified Multi-Modal AI Engine.")
    
    try:
        while True:
            message = await websocket.receive()
            
            # Scenario A: Processing raw streaming binary audio chunks
            if "bytes" in message:
                raw_bytes = message["bytes"]
                audio_array = audio_processor.bytes_to_audio_array(raw_bytes)
                mel_spec = audio_processor.extract_mel_spectrogram(audio_array)
                voice_analysis = deepfake_detector.analyze_spectrogram(mel_spec)
                
                response = {
                    "type": "voice_analysis",
                    "bytes_processed": len(raw_bytes),
                    "voice_metrics": voice_analysis
                }
                await websocket.send_text(json.dumps(response))

            # Scenario B: Processing live text transcriptions / JSON payloads
            elif "text" in message:
                payload = json.loads(message["text"])
                transcript_text = payload.get("transcript", "")
                
                intent_analysis = intent_scanner.analyze_text(transcript_text)
                
                # Mock high-risk check when receiving text + previous voice state
                synthetic_score = payload.get("synthetic_score", 0.15)
                combined_risk = round((synthetic_score * 0.5) + (intent_analysis["scam_score"] * 0.5), 4)

                response = {
                    "type": "full_risk_assessment",
                    "transcript_analyzed": transcript_text,
                    "intent_metrics": intent_analysis,
                    "combined_threat_score": combined_risk,
                    "action_required": "ALERT_USER" if combined_risk >= 0.65 else "MONITOR"
                }
                await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("[SERVER] Client disconnected gracefully.")
    except Exception as e:
        print(f"[SERVER ERROR] Stream Error: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)