import cv2
from ultralytics import YOLO
from .counter import RupiahCounter

class ObjectDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.counter = RupiahCounter(self.model.names)

    def process_frame(self, frame):
        results = self.model.track(frame, persist=True, conf=0.65, iou=0.4, verbose=False)
        
        tracks = []
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            confs = results[0].boxes.conf.cpu().tolist()

            for box, t_id, c_id, conf in zip(boxes, track_ids, class_ids, confs):
                tracks.append({
                    "track_id": t_id,
                    "class_id": c_id,
                    "confidence": conf,
                    "bbox": box.tolist()
                })

        processed_detections = self.counter.process_tracks(tracks)
        
        for det in processed_detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            color = (0, 255, 0) if det['counted'] else (0, 0, 255)
            label = f"Rp{det['denomination']:,} (ID:{det['track_id']})"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame, processed_detections