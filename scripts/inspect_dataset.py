import os
import glob
from collections import Counter

def audit_dataset(dataset_path):
    print(f"--- Memulai Audit Dataset di {dataset_path} ---")
    if not os.path.exists(dataset_path):
        print("[ERROR] Direktori dataset tidak ditemukan!")
        return

    images = glob.glob(os.path.join(dataset_path, '**', '*.jpg'), recursive=True) + \
             glob.glob(os.path.join(dataset_path, '**', '*.jpeg'), recursive=True) + \
             glob.glob(os.path.join(dataset_path, '**', '*.png'), recursive=True)
    
    print(f"[INFO] Total gambar ditemukan: {len(images)}")

    missing_annotations = 0
    class_distribution = Counter()
    
    for img_path in images:
        txt_path = os.path.splitext(img_path)[0]
        txt_path = txt_path.replace(f"{os.sep}images{os.sep}", f"{os.sep}labels{os.sep}") + '.txt'
        
        # Fallback jika ternyata dalam 1 folder yang sama
        if not os.path.exists(txt_path):
            txt_path = os.path.splitext(img_path)[0] + '.txt'

        if not os.path.exists(txt_path):
            missing_annotations += 1
        else:
            with open(txt_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5: 
                        class_distribution[int(parts[0])] += 1

    print(f"[INFO] Gambar tanpa anotasi: {missing_annotations}")
    
    if missing_annotations == len(images) and len(images) > 0:
        print("[WARNING] Dataset ini hanya berisi gambar dan tidak memiliki file anotasi bounding box (.txt)!")
    
    print("\n--- Distribusi Kelas Berdasarkan Anotasi (Jika Ada) ---")
    for cls_id, count in sorted(class_distribution.items()):
        print(f"Kelas ID {cls_id}: {count} bounding boxes")
        if count < 100:
            print(f"  -> [WARNING] Kelas {cls_id} memiliki sampel terlalu sedikit.")

if __name__ == "__main__":
    audit_dataset("dataset")