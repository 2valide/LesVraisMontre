import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification, pipeline
from ai.findWatch import find_watch_model, assess_reality
from PIL import Image

feature_extractor = AutoFeatureExtractor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")
classifier = pipeline(
    "image-classification",
    model=model,
    feature_extractor=feature_extractor,
    top_k=5
)

def analyze_watch(image_path: str) -> dict:
    img = Image.open(image_path).convert("RGB")
    results = classifier(img)
    is_w = any('watch' in r['label'].lower() for r in results)
    output = {"is_watch": is_w}
    if not is_w:
        return output
    output["watch_models"] = find_watch_model(image_path)
    output["reality_score"] = assess_reality(image_path)
    return output

