from flask import Flask, render_template, request, jsonify
import openai, os, datetime, pytz

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

_cache_day = None
_cache_schedule = None

def ai_generate(prompt):
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    return res.choices[0].message["content"].strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    text = data.get("text", "")
    action = data.get("action", "rewrite")

    if not text:
        return jsonify({"error": "Teks tidak boleh kosong."})

    if action == "rewrite":
        prompt = f"Tulis ulang berita berikut agar lebih singkat, jelas, dan alami:\n{text}"
    elif action == "title":
        prompt = f"Buat judul menarik dan SEO-friendly untuk berita berikut:\n{text}"
    elif action == "hashtag":
        prompt = f"Buat 10 hashtag relevan untuk berita berikut, bagi dua: TikTok dan Instagram:\n{text}"
    else:
        prompt = f"Ringkas teks berikut dengan gaya berita profesional:\n{text}"

    return jsonify({"result": ai_generate(prompt)})

def ai_schedule():
    global _cache_day, _cache_schedule
    today = datetime.date.today().isoformat()
    if _cache_day == today and _cache_schedule:
        return _cache_schedule

    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.datetime.now(tz)
    day = now.strftime("%A")
    time_str = now.strftime("%H:%M")

    prompt = f"""
    Hari ini {day}, jam {time_str} WIB.
    Berdasarkan algoritme terbaru TikTok dan Instagram 2025,
    buat jadwal upload konten yang berpotensi FYP dan trending hari ini.
    Pertimbangkan juga tren mingguan (weekday produktif, weekend santai).
    Jelaskan waktu dan alasannya dengan emoji.
    """

    result = ai_generate(prompt)
    _cache_day = today
    _cache_schedule = result
    return result

@app.route("/schedule")
def schedule_page():
    return render_template("schedule.html")

@app.route("/get_schedule")
def get_schedule():
    return jsonify({"schedule": ai_schedule()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
