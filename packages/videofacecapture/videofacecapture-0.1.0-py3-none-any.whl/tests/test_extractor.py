from videofacecapture.face_capture import VideoFaceCapture

# Use DNN detector
# capture = VideoFaceCapture(
#     use_dnn=True,
#     model_path="res10_300x300_ssd_iter_140000.caffemodel",
#     config_path="deploy.prototxt.txt"
# )
# face_count = capture.capture_from_videos("videos", output_dir="faces_output")
# print(f"Captured {face_count} faces")

# Or use Haar cascade
capture = VideoFaceCapture(use_dnn=False)
face_count = capture.capture_from_videos("videos", output_dir="faces_output_has")
print(f"Captured {face_count} faces")