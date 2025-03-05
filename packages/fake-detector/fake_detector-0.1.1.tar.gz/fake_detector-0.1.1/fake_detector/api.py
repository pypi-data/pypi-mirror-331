from flask import Flask, request, jsonify
from flask_cors import CORS
from fake_detector.detector import FakeDetector

app = Flask(__name__)
CORS(app)

detector = FakeDetector()

@app.route('/analyze', methods=['POST'])
def detect_fake():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data["text"]
        result = detector.detect(text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
