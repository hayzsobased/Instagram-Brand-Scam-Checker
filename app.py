from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

SERPAPI_KEY = "72198a0f30d73de1f350732c8578d2d537ca0d81a833f93f6cdda378f1de4940"

BACKGROUND_URL = "https://d7hftxdivxxvm.cloudfront.net/?quality=80&resize_to=width&src=https%3A%2F%2Fartsy-media-uploads.s3.amazonaws.com%2F2RNK1P0BYVrSCZEy_Sd1Ew%252F3417757448_4a6bdf36ce_o.jpg&width=910"  # ← Replace this with your image URL

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Scam Checker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: auto;
            padding: 20px;
            background: url('{{ bg_url }}') no-repeat center center fixed;
            background-size: cover;
            color: #fff;
            text-shadow: 1px 1px 2px #000;
        }
        input, button {
            padding: 10px;
            width: 100%;
            margin-top: 10px;
            font-size: 16px;
        }
        .results {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.6);
            border-radius: 8px;
        }
        .score {
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
        }
        a {
            color: #aaf;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h2>Instagram Scam Checker</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Instagram brand username" required>
        <button type="submit">Check</button>
    </form>

    {% if score is not none %}
        <div class="score">
            Trust Score for '{{ user }}': {{ score }}/100<br>
            {% if score > 75 %}
                ✅ Likely Safe
            {% elif score > 40 %}
                ⚠️ Caution Advised
            {% else %}
                ❌ Possibly a Scam
            {% endif %}
        </div>
    {% endif %}

    {% if results %}
        <div class="results">
            <h4>Top Search Results:</h4>
            <ul>
                {% for title, link in results %}
                    <li><a href="{{ link }}" target="_blank">{{ title }}</a></li>
                {% endfor %}
            </ul>
        </div>
    {% elif error %}
        <p class="results">{{ error }}</p>
    {% endif %}
</body>
</html>
"""

NEGATIVE_KEYWORDS = ["scam", "not legit", "fraud", "fake", "never arrived", "stole", "ripoff", "untrustworthy"]
POSITIVE_KEYWORDS = ["legit", "trustworthy", "real", "recommended", "honest", "arrived", "good quality"]

def calculate_trust_score(texts):
    score = 50
    for text in texts:
        lower = text.lower()
        for word in NEGATIVE_KEYWORDS:
            if word in lower:
                score -= 10
        for word in POSITIVE_KEYWORDS:
            if word in lower:
                score += 10
    return max(0, min(score, 100))

def serpapi_searches(username):
    results = []
    texts_for_score = []
    queries = [
        f"instagram brand {username} legit",
        f"is {username} legit site:reddit.com"
    ]

    for query in queries:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": 10
        }

        try:
            res = requests.get("https://serpapi.com/search", params=params)
            data = res.json()
            for r in data.get("organic_results", []):
                title = r.get("title")
                link = r.get("link")
                if title and link:
                    results.append((title, link))
                    texts_for_score.append(title)
        except Exception as e:
            print("Error with query:", query, e)

    score = calculate_trust_score(texts_for_score)
    return results, score

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error = None
    user = None
    score = None

    if request.method == "POST":
        user = request.form.get("username").strip()
        if user:
            results, score = serpapi_searches(user)
            if not results:
                error = "No search results found or API limit reached."
        else:
            error = "Please enter a username."

    return render_template_string(HTML_TEMPLATE, results=results, error=error, user=user, score=score, bg_url=BACKGROUND_URL)

if __name__ == "__main__":
    app.run(debug=True)
