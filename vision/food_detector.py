from transformers import pipeline
from PIL import Image

# --------------------------------------------------
# Vision pipelines
# --------------------------------------------------

classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)

# --------------------------------------------------

FOOD_LABELS = [
    "pizza",
    "salad",
    "rice",
    "curry",
    "noodles",
    "burger",
    "sandwich",
    "pasta",
    "chicken",
    "fish",
    "vegetables",
    "fruit bowl",
    "breakfast plate",
    "indian meal",
    "thali",
    "healthy food",
]

# --------------------------------------------------

def describe_food(image_path: str) -> str:
    """
    Identify food in image using CLIP.
    """

    image = Image.open(image_path).convert("RGB")

    results = classifier(image, FOOD_LABELS)

    top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    names = [r["label"] for r in top]

    return (
        "Detected food items: "
        + ", ".join(names)
    )
