from transformers import pipeline

class FakeDetector:
    def __init__(self):
        # Load a pre-trained fake news detection model from Hugging Face
        self.classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-fake-news")

    def detect(self, text: str):
        if not text:
            return {"error": "No text provided"}
        try:
            result = self.classifier(text)[0]  # Get the classification result
            return {"label": result['label'], "confidence": float(result['score'])}
        except Exception as e:
            return {"error": str(e)}
