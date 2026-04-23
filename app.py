from flask import Flask, render_template_string, request, redirect, url_for
from collections import Counter
import os

app = Flask(__name__)

# ---------------------------
# LOAD WORDS
# ---------------------------
def load_words(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [w.strip().lower() for w in f if len(w.strip()) == 5]

all_words = load_words("koncnebesede.txt")


# ---------------------------
# FILTER
# ---------------------------
def filter_words(words, guess, result):
    new_words = []

    for word in words:
        ok = True

        for i in range(5):
            if result[i] == "z":
                if word[i] != guess[i]:
                    ok = False
                    break

            elif result[i] == "r":
                if guess[i] not in word or word[i] == guess[i]:
                    ok = False
                    break

            elif result[i] == "c":
                if guess[i] in word:
                    ok = False
                    break

        if ok:
            new_words.append(word)

    return new_words


# ---------------------------
# FREQUENCY + SCORING
# ---------------------------
def compute_global_frequency(words):
    c = Counter()
    for w in words:
        c.update(set(w))
    return c

freq = compute_global_frequency(all_words)

def score_word(word):
    return sum(freq[c] for c in set(word))

def best_10(words):
    scored = sorted([(w, score_word(w)) for w in words], key=lambda x: x[1], reverse=True)
    return scored[:10]


# ---------------------------
# GLOBAL STATE (IMPORTANT FIX)
# ---------------------------
current_words = all_words.copy()


# ---------------------------
# HTML
# ---------------------------
HTML = """
<!doctype html>
<html>
<head>
<title>burekov reševalec petke</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; max-width: 700px; margin:auto; padding:20px; background:#121213; color:white; }
input,button{padding:10px;margin:5px;border-radius:5px;border:none}
button{cursor:pointer;background:#538d4e;color:white}
.reset{background:#b59f3b}
</style>
</head>
<body>

<h1>BUREKOV REŠEVALEC PETKE</h1>

<p><b>Možnih besed:</b> {{ count }}</p>

<form method="post">
<input name="guess" placeholder="Burek" maxlength="5" required>
<input name="result" placeholder="z/r/c" maxlength="5" required>
<button type="submit">Potrdi</button>
</form>

<form action="/reset" method="post">
<button class="reset" type="submit">Nov burek</button>
</form>

<h2>Top 10 burekov</h2>
<h2>najbolsi je mesni</h2>
<ul>
{% for w,s in top10 %}
<li>{{ w }} ({{ s }})</li>
{% endfor %}
</ul>

<h2>Možnosti</h2>
<p>{{ words[:100] }}</p>

</body>
</html>
"""


# ---------------------------
# ROUTES
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    global current_words

    if request.method == "POST":
        guess = request.form["guess"].lower()
        result = request.form["result"].lower()

        if len(guess) == 5 and len(result) == 5:
            current_words = filter_words(current_words, guess, result)

    top10 = best_10(current_words)

    return render_template_string(
        HTML,
        count=len(current_words),
        top10=top10,
        words=current_words
    )


@app.route("/reset", methods=["POST"])
def reset():
    global current_words
    current_words = all_words.copy()
    return redirect(url_for("index"))


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)