from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.detector import ObjectDetector
import cv2
import os

app = FastAPI(title="Rupiah CV System API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2] 

MODEL_PATH = ROOT_DIR / "runs" / "detect" / "models" / "rupiah_tracker" / "weights" / "best.pt"

if not MODEL_PATH.exists():
    print(f"[FATAL ERROR] Model tidak ditemukan di: {MODEL_PATH}")
    sys.exit(1) 
detector = ObjectDetector(MODEL_PATH)
camera = None
is_running = False

def get_video_stream():
    global camera, is_running
    
    print("[INFO] Mencoba membuka kamera...")
    camera = cv2.VideoCapture(1) 
    
    if not camera.isOpened():
        print("[ERROR] Kamera tidak terdeteksi atau akses ditolak!")
        return

    is_running = True
    print("[INFO] Kamera berhasil dibuka dan streaming dimulai.")
    
    while is_running:
        success, frame = camera.read()
        
        if not success or frame is None:
            print("[ERROR] Mendapatkan frame kosong dari kamera.")
            continue 
            
        try:
            processed_frame, _ = detector.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')
        except Exception as e:
            print(f"[ERROR] Kesalahan inferensi model: {e}")
            break

@app.get("/api/camera/stream")
def video_stream():
    return StreamingResponse(get_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/api/camera/stop")
def stop_camera():
    global is_running, camera
    is_running = False
    if camera:
        camera.release()
    return {"status": "Kamera dihentikan"}

@app.post("/api/count/reset")
def reset_counting():
    detector.counter.reset_session()
    return {"status": "Sesi direset"}

@app.get("/api/count-summary")
def get_summary():
    return {"summary": detector.counter.get_summary()}