import os
import shutil
from ultralytics import YOLO

INPUT_DIR = r"D:\Website\database\rupiah-banknotes-dataset-main"
TRAIN_IMAGES_DIR = os.path.join("dataset", "train", "images")
TRAIN_LABELS_DIR = os.path.join("dataset", "train", "labels")

os.makedirs(TRAIN_IMAGES_DIR, exist_ok=True)
os.makedirs(TRAIN_LABELS_DIR, exist_ok=True)

print(f"[INFO] 1. Menggabungkan gambar dari {INPUT_DIR}...")

image_count = 0
for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            src_path = os.path.join(root, file)
            
            parent_folder = os.path.basename(root)
            new_filename = f"{parent_folder}_{file}"
            dst_path = os.path.join(TRAIN_IMAGES_DIR, new_filename)
            
            shutil.copy(src_path, dst_path)
            image_count += 1

print(f"[INFO] Berhasil menyalin dan menata {image_count} gambar ke {TRAIN_IMAGES_DIR}")

print("[INFO] 2. Memulai proses Auto-Labeling YOLO (ini akan memakan waktu beberapa menit)...")
model = YOLO(r"runs\detect\models\rupiah_tracker\weights\best.pt")

model.predict(
    source=TRAIN_IMAGES_DIR,
    save_txt=True,
    save_conf=False,
    project="dataset",
    name="temp_auto_labels",
    exist_ok=True,
    verbose=False
)

print("[INFO] 3. Memindahkan file anotasi .txt ke folder labels...")
temp_labels_dir = os.path.join("dataset", "temp_auto_labels", "labels")

if os.path.exists(temp_labels_dir):
    for txt_file in os.listdir(temp_labels_dir):
        src_txt = os.path.join(temp_labels_dir, txt_file)
        dst_txt = os.path.join(TRAIN_LABELS_DIR, txt_file)
        shutil.move(src_txt, dst_txt)
        
shutil.rmtree(os.path.join("dataset", "temp_auto_labels"), ignore_errors=True)

print(f"\n[INFO] SELESAI! Dataset {image_count} gambar kini sudah 100% dalam format YOLO standar.")
print(f"File siap dilatih. Silakan periksa folder dataset/train/labels lalu jalankan ulang training Anda.")