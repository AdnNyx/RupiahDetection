class RupiahCounter:
    def __init__(self, model_names):
        self.class_mapping = {}
        for cls_id, name in model_names.items():
            try:
                nominal = int(name.replace('idr_', ''))
                self.class_mapping[cls_id] = nominal
            except ValueError:
                pass
                
        self.reset_session()

    def reset_session(self):
        self.counted_tracks = set()  
        self.denomination_counts = {nominal: 0 for nominal in self.class_mapping.values()}
        self.total_amount = 0

    def process_tracks(self, tracks):
        current_detections = []
        
        for track in tracks:
            track_id = track['track_id']
            class_id = track['class_id']
            
            if class_id not in self.class_mapping:
                continue
                
            nominal = self.class_mapping[class_id]
            is_counted = track_id in self.counted_tracks

            if track_id is not None and not is_counted:
                self.counted_tracks.add(track_id)
                self.denomination_counts[nominal] += 1
                self.total_amount += nominal
                is_counted = True

            current_detections.append({
                "track_id": track_id,
                "class_id": class_id,
                "denomination": nominal,
                "counted": is_counted,
                "bbox": track['bbox'],
                "confidence": track['confidence']
            })

        return current_detections

    def get_summary(self):
        total_notes = sum(self.denomination_counts.values())
        return {
            "total_notes": total_notes,
            "total_amount": self.total_amount,
            "details": self.denomination_counts
        }