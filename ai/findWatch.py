from PIL import Image
from transformers import pipeline

watch_model_classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)
WATCH_LABELS = [
    "Rolex Submariner",
    "Rolex Daytona",
    "Rolex GMT-Master II",
    "Rolex Datejust",
    "Rolex Explorer"
]

fake_detector = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)
FAKE_LABELS = ["real watch", "fake watch"]

def find_watch_model(image_path: str) -> list[tuple[str, float]]:
    """
    Renvoie une liste de (label, score) pour les 5 modèles Rolex.
    """
    img = Image.open(image_path).convert("RGB")
    out = watch_model_classifier(images=img, candidate_labels=WATCH_LABELS)
    return [(entry['label'], float(entry['score'])) for entry in out]


def assess_reality(image_path: str) -> float:
    img = Image.open(image_path).convert("RGB")
    out = fake_detector(images=img, candidate_labels=FAKE_LABELS)
    for entry in out:
        if entry['label'] == "real watch":
            return round(float(entry['score']) * 100, 1)
    return 0.0
