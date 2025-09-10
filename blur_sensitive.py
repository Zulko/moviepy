import cv2
import re
import pytesseract
from pytesseract import Output
from moviepy.editor import VideoFileClip

# ========= CONFIG =========
input_path = "Screen Recording 2025-09-04 184139.mp4"   # Your input video file
output_path = "Screen_Recording_Blurred.mp4"            # Output video file
ocr_interval = 5  # Run OCR every N frames (5 is a good balance)
# ==========================

# Regex patterns for sensitive data
patterns = {
    "phone": re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d"),
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "access_code": re.compile(r"\b[A-Z0-9]{6,}\b"),
    "name": re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b"),
}

# Load video
clip = VideoFileClip(input_path)
fps = clip.fps
width, height = clip.size

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Frame loop
frame_count = 0
active_boxes = []

for frame in clip.iter_frames(fps=fps, dtype="uint8"):
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Run OCR every N frames
    if frame_count % ocr_interval == 0:
        active_boxes = []
        data = pytesseract.image_to_data(frame_bgr, output_type=Output.DICT)
        n_boxes = len(data['level'])

        for j in range(n_boxes):
            text = data['text'][j].strip()
            if not text:
                continue
            if any(p.search(text) for p in patterns.values()):
                (x, y, w, h) = (data['left'][j], data['top'][j], data['width'][j], data['height'][j])
                if w > 0 and h > 0:
                    active_boxes.append((x, y, w, h))

    # Apply blur to all active boxes
    for (x, y, w, h) in active_boxes:
        roi = frame_bgr[y:y+h, x:x+w]
        if roi.size > 0:
            blur = cv2.GaussianBlur(roi, (51, 51), 30)
            frame_bgr[y:y+h, x:x+w] = blur

    out.write(frame_bgr)
    frame_count += 1

out.release()
print(f"✅ Blurred video saved to: {output_path}")
