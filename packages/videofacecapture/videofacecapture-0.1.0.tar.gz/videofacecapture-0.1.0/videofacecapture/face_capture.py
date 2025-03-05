# videofacecapture/face_capture.py
import cv2
import os
import numpy as np

class VideoFaceCapture:
    """A tool to capture and save faces from videos or images using modern face detection."""
    
    def __init__(self, use_dnn=True, model_path=None, config_path=None, cascade_path=None):
        """Initialize with DNN or Haar cascade face detector."""
        self.use_dnn = use_dnn
        if use_dnn:
            # Default DNN model paths (user must provide if not specified)
            self.model_path = model_path or "res10_300x300_ssd_iter_140000.caffemodel"
            self.config_path = config_path or "deploy.prototxt"
            if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
                raise ValueError("DNN model or config file not found. Provide valid paths.")
            self.net = cv2.dnn.readNetFromCaffe(self.config_path, self.model_path)
        else:
            # Fallback to Haar cascade
            cascade_path = cascade_path or cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                raise ValueError("Failed to load Haar cascade file.")

    def _detect_faces(self, frame, output_dir, face_count):
        """Detect faces in a frame and save them to the output directory."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if self.use_dnn:
            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            detections = self.net.forward()
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:  # Confidence threshold
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x, y, x2, y2) = box.astype("int")
                    face_image = frame[y:y2, x:x2]
                    if face_image.size > 0:  # Ensure valid crop
                        output_path = os.path.join(output_dir, f"face_{face_count}.jpg")
                        cv2.imwrite(output_path, face_image)
                        face_count += 1
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            for (x, y, w, h) in faces:
                face_image = frame[y:y+h, x:x+w]
                output_path = os.path.join(output_dir, f"face_{face_count}.jpg")
                cv2.imwrite(output_path, face_image)
                face_count += 1
        
        return face_count

    def capture_from_videos(self, video_dir, output_dir="faces_output"):
        """Capture faces from all videos in the specified directory."""
        if not os.path.isdir(video_dir):
            raise ValueError(f"Video directory '{video_dir}' does not exist.")
        
        face_count = 0
        for video_file in os.listdir(video_dir):
            if video_file.lower().endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(video_dir, video_file)
                cap = cv2.VideoCapture(video_path)
                
                if not cap.isOpened():
                    print(f"Warning: Could not open video '{video_file}'. Skipping.")
                    continue
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    face_count = self._detect_faces(frame, output_dir, face_count)
                
                cap.release()
        
        return face_count

    def capture_from_images(self, image_dir, output_dir="faces_output"):
        """Capture faces from all images in the specified directory."""
        if not os.path.isdir(image_dir):
            raise ValueError(f"Image directory '{image_dir}' does not exist.")
        
        face_count = 0
        for image_file in os.listdir(image_dir):
            if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(image_dir, image_file)
                frame = cv2.imread(image_path)
                if frame is None:
                    print(f"Warning: Could not load image '{image_file}'. Skipping.")
                    continue
                face_count = self._detect_faces(frame, output_dir, face_count)
        
        return face_count
