<div align="center">

# RupiahCV — Real-Time Banknote Detection & Nominal Counter

**Production-Ready Computer Vision & Decoupled Web Application for Automated Indonesian Rupiah (IDR) Recognition**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-10b981?style=flat-square)]()
[![Model](https://img.shields.io/badge/Model-YOLOv11n-0284c7?style=flat-square)]()
[![mAP@0.5](https://img.shields.io/badge/mAP%400.5-97.0%25-16a34a?style=flat-square)]()
[![Latency](https://img.shields.io/badge/Inference-6.9%20ms%2Fframe-f59e0b?style=flat-square)]()
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-009688?style=flat-square)]()
[![Frontend](https://img.shields.io/badge/Frontend-Vue%203%20%7C%20Tailwind%20CSS%20v4-42b883?style=flat-square)]()

[Overview](#1-executive-overview) •
[Architecture](#2-system-architecture) •
[Model Benchmarks](#4-model-performance--evaluation-benchmarks) •
[Installation](#6-getting-started) •
[API Reference](#7-api-reference)

</div>

---

## 1. Executive Overview

**RupiahCV** is a real-time computer vision system engineered to detect, classify, and automatically sum Indonesian Rupiah (IDR) paper banknotes from live webcam streams. Built on a decoupled client-server architecture combining **Ultralytics YOLOv11n**, **FastAPI**, and **Vue 3**, the platform offloads deep learning inference to a GPU-accelerated Python backend while delivering a low-latency MJPEG video feed and reactive financial summary to modern Chromium-based browsers.

### Key Capabilities
* **7-Class Banknote Recognition:** Accurately classifies all circulating IDR paper denominations (`Rp1.000` to `Rp100.000`) across both **2016 and 2022 emission series**.
* **Sub-10ms Real-Time Inference:** Achieves **6.9 ms/frame** inference latency on consumer-grade GPU hardware (NVIDIA GeForce GTX 1650 4GB), enabling smooth real-time video overlays.
* **Stateless Frame-Level Summation:** Computes total currency value dynamically per frame ($\text{Total} = \sum (n_k \times v_k)$) with confidence and IoU filtering to eliminate duplicate bounding boxes and prevent cumulative double-counting.
* **Decoupled Enterprise Architecture:** Separates AI/video processing (FastAPI + OpenCV) from presentation logic (Vue 3 Composition API + Tailwind CSS v4) for independent scalability and maintainability.

---

## 2. System Architecture

The application implements a decoupled pipeline where OpenCV captures raw frames from the local camera, YOLOv11n performs single-pass object detection, and FastAPI streams annotated frames via `multipart/x-mixed-replace` (MJPEG) alongside a RESTful telemetry endpoint.

```text
┌─────────────────────┐      Raw Frames       ┌───────────────────────────────────────────┐
│   Webcam / Camera   │ ────────────────────► │        Backend Engine (FastAPI)           │
└─────────────────────┘                       │                                           │
                                              │  1. OpenCV (cv2) Frame Capture            │
                                              │  2. YOLOv11n Inference (conf=0.65, iou=0.4)│
                                              │  3. Stateless Nominal Summation Engine    │
                                              └─────────────────────┬─────────────────────┘
                                                                    │
                                           MJPEG Video Stream       │  REST API (JSON Telemetry)
                                        (/api/camera/stream)        │  (Polled @ 1,000 ms)
                                                                    ▼
                                              ┌───────────────────────────────────────────┐
                                              │      Frontend Client (Vue 3 + Vite)       │
                                              │                                           │
                                              │  • Live Annotated Bounding Box Viewport   │
                                              │  • Real-Time Total & Denomination List    │
                                              │  • Camera Lifecycle Controls (Start/Stop) │
                                              └───────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Specification / Role |
| :--- | :--- | :--- |
| **AI & Computer Vision** | Ultralytics YOLOv11n, OpenCV (`cv2`) | Real-time single-stage object detection & video I/O |
| **Compute Runtime** | PyTorch, NVIDIA CUDA 12.1 | Hardware-accelerated inference (NVIDIA GTX 1650 4GB VRAM) |
| **Backend Service** | Python 3.11, FastAPI, Uvicorn | Asynchronous REST API & MJPEG video streaming server |
| **Frontend Client** | Vue 3 (Composition API), Tailwind CSS v4 | Reactive dashboard UI & live telemetry polling |
| **Data & Annotation** | Roboflow, LabelImg | Dataset formatting, manual bounding-box refinement & pseudo-labeling |

---

## 4. Model Performance & Evaluation Benchmarks

### 4.1 Training Protocol & Hyperparameters
The model was trained on a curated dataset of **1,397 images** (split **80% Train** / **20% Validation** = 279 validation samples), combining studio-lit reference images (`rupiah-banknotes-dataset`) with local webcam calibration captures and 50+ negative background samples.

| Parameter | Configured Value | Description |
| :--- | :--- | :--- |
| **Architecture** | `yolo11n.pt` (Nano) | Lightweight architecture optimized for 4GB VRAM |
| **Input Resolution** | `640 × 640` (`imgsz=640`) | Standardized square input tensor |
| **Epochs / Batch Size** | `50` epochs / `batch=8` | Completed in ~32 minutes (`0.544` hours) |
| **Early Stopping** | `patience=15` | Halts training if validation metrics plateau |
| **Optimizer** | `AdamW` (`auto`) | Adaptive learning rate optimization (`lr0=0.01`) |
| **Inference Thresholds** | `conf=0.65`, `iou=0.4` | Filters low-confidence predictions & overlapping boxes |

### 4.2 Validation Metrics by Class
The trained weights (`models/rupiah_tracker/weights/best.pt`) achieved an overall **mAP@0.5 of 0.970** and peak **F1-Score of 0.95** (at confidence `0.499`).

| Class ID | Class Label | Denomination | Precision-Recall (`mAP@0.5`) |
| :---: | :--- | :--- | :---: |
| `0` | `idr_1000` | Rp1.000 | **0.994** |
| `1` | `idr_2000` | Rp2.000 | **0.990** |
| `2` | `idr_5000` | Rp5.000 | **0.982** |
| `3` | `idr_10000` | Rp10.000 | **0.959** |
| `4` | `idr_20000` | Rp20.000 | **0.966** |
| `5` | `idr_50000` | Rp50.000 | **0.955** |
| `6` | `idr_100000` | Rp100.000 | **0.942** |
| **All** | **All Classes** | **Overall Average** | **0.970** |

### 4.3 Quality Assurance & Risk Mitigation
* **Webcam White-Balance Domain Shift:** Mitigated color distortion between grey `Rp2.000` and blue `Rp50.000` notes under indoor lighting by injecting 30–50 locally captured webcam calibration samples into the training set.
* **Background False Positives:** Reduced erroneous detections on rectangular desk objects by adding 50+ negative background samples and enforcing a strict inference confidence threshold (`conf=0.65`).

---

## 5. Repository Structure

```text
RupiahDetection/
├── backend/
│   ├── app/
│   │   └── main.py                 # FastAPI application, MJPEG stream & inference logic
│   ├── models/
│   │   └── rupiah_tracker/
│   │       ├── weights/
│   │       │   └── best.pt         # Production-ready YOLOv11n trained weights
│   │       ├── args.yaml           # Training hyperparameter configuration
│   │       ├── BoxF1_curve.png     # F1-Confidence evaluation curve
│   │       ├── BoxPR_curve.png     # Precision-Recall evaluation curve
│   │       └── confusion_matrix.png# Validation confusion matrix
│   ├── data.yaml                   # Dataset class definitions
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── public/                     # Static assets
│   ├── src/                        # Vue 3 components & dashboard views
│   ├── index.html                  # Application entry point
│   ├── package.json                # Node.js dependencies & scripts
│   └── vite.config.js              # Vite bundler configuration
├── .gitignore                      # Git exclusion rules (datasets, venv, node_modules)
└── README.md                       # Project documentation
```

---

## 6. Getting Started

### Prerequisites
* **Python:** `3.11+`
* **Node.js:** `18.0+` (with `npm` or `pnpm`)
* **Hardware:** Standard USB/integrated webcam (NVIDIA GPU with CUDA 12.1+ recommended for sub-10ms inference; CPU fallback supported)
* **Browser:** Chromium-based browser (Google Chrome or Microsoft Edge) for native `multipart/x-mixed-replace` MJPEG rendering

### 6.1 Backend Setup
1. Clone the repository and navigate to the backend directory:
   ```bash
   git clone [https://github.com/AdnNyx/RupiahDetection.git](https://github.com/AdnNyx/RupiahDetection.git)
   cd RupiahDetection/backend
   ```
2. Create and activate an isolated Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be active at `http://127.0.0.1:8000`.

### 6.2 Frontend Setup
1. Open a new terminal window and navigate to the `frontend` directory:
   ```bash
   cd RupiahDetection/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Launch the development server:
   ```bash
   npm run dev
   ```
4. Open **`http://127.0.0.1:5173`** in Google Chrome or Microsoft Edge, then click **Mulai Kamera** to begin real-time detection.

---

## 7. API Reference

| Method | Endpoint | Content-Type | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/camera/stream` | `multipart/x-mixed-replace` | Initializes webcam capture and streams real-time MJPEG frames annotated with bounding boxes, class labels, and confidence scores. |
| `POST` / `GET` | `/api/camera/stop` | `application/json` | Releases the active OpenCV camera capture handle and halts frame inference. |
| `GET` | `/api/summary` | `application/json` | Returns current frame detection counts per denomination and calculated total IDR value. |

---

## 8. Known Limitations & Future Roadmap

* **Severe Physical Occlusion:** Detection confidence degrades when more than 60% of a banknote's surface area is obstructed by fingers or overlapping objects. Future iterations will incorporate heavily occluded training samples.
* **Counterfeit Verification:** The model performs visual denomination classification only and does not validate UV security threads or tactile intaglio features.
* **Planned Enhancements:**
  * Integrate Web Speech API audio feedback for visually impaired accessibility.
  * Export `best.pt` to ONNX / TensorRT / TFLite formats for edge and mobile deployment.

---

## 9. Authors & Acknowledgments

* **Lead Developer & AI Engineer:** [Mahfudin Adnan](https://www.nandev.my.id/) (`@AdnNyx`) — Informatics Engineering, Universitas Pancasakti Tegal
* **Project Contributors:** Amelia Laura Ardianti, Erza Rifa Nihayah, Nofal Azhar Safriansyah
* **Dataset Reference:** Derived from [`rupiah-banknotes-dataset`](https://github.com/anwarpage/rupiah-banknotes-dataset) (Anwar et al., 2025) supplemented with local hardware calibration captures.