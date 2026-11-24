import os
from ultralytics import YOLO
import torch

def train_model():
    print(f"[INFO] CUDA tersedia: {torch.cuda.is_available()}")
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"[INFO] Menggunakan device: {device}")

    model = YOLO("yolo11n.pt") 

    data_path = os.path.abspath("dataset/data.yaml")

    results = model.train(
        data=data_path,
        epochs=50,         
        imgsz=640,
        batch=8,           
        patience=15,       
        device=device,
        project="models",
        name="rupiah_tracker",
        exist_ok=True
    )
    
    print("[INFO] Training selesai. Model terbaik disimpan di models/rupiah_tracker/weights/best.pt")

if __name__ == "__main__":
    train_model()