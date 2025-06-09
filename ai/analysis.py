import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification, pipeline
import cv2
import numpy as np
from PIL import Image

model_name = "google/vit-base-patch16-224"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

classifier = pipeline(
    "image-classification",
    model=model,
    feature_extractor=feature_extractor,
    top_k=5
)

def is_watch(image_path: str) -> bool:
    img = Image.open(image_path).convert("RGB")
    results = classifier(img)
    for r in results:
        if 'watch' in r['label'].lower():
            return True
    return False

def symmetry_score(image_path: str) -> float:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    left = gray[:, :w//2]
    right = cv2.flip(gray[:, w-w//2:], 1)
    right = cv2.resize(right, (left.shape[1], left.shape[0]))
    diff = cv2.absdiff(left, right)
    return float(1.0 - (np.mean(diff) / 255.0))

def alignment_score(image_path: str) -> float:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    circles = cv2.HoughCircles( blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=0, maxRadius=0 )
    h, w = gray.shape
    cx, cy = w/2, h/2
    if circles is not None:
        x, y, _ = circles[0][0]
        offset = np.hypot(x-cx, y-cy)
        norm = offset / np.hypot(cx, cy)
        return float(1.0 - norm)
    return 0.0

def dominant_color(image_path: str, k: int = 3) -> tuple:
    img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    pixels = img.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans( pixels, k, None, criteria, attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    dom = centers[np.argmax(counts)].astype(int)
    return tuple(dom)

def analyze_watch(image_path: str) -> dict:
    is_w = is_watch(image_path)
    results = {"is_watch": is_w}
    if not is_w:
        return results
    results["symmetry_score"] = round(symmetry_score(image_path), 3)
    results["alignment_score"] = round(alignment_score(image_path), 3)
    results["dominant_color"] = dominant_color(image_path)
    return results