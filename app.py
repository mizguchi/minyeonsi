import os
import random
import secrets
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))


OPTIONS = [
    {"id": "joke", "text": "아재개그하기"},
    {"id": "ctf", "text": "후방에서 CTF 풀기"},
    {"id": "study", "text": "도서관에서 시험 공부하기"},
    {"id": "coffee", "text": "학카에서 커피 사주기"},
    {"id": "walk", "text": "광교호수공원 산책하기"},
    {"id": "meal", "text": "밥 사주기"},
]

ACTIVITIES = {
    "ctf": {
        "scene": "ctf",
        "delta": -1,
        "steps": [
            {"speaker": "", "text": "후방에서 민정과 함께 CTF 문제를 풀기 시작했다.", "mood": "normal", "sprite": "girl/computer1"},
            {"speaker": "민정", "text": "....", "mood": "bored", "sprite": "girl/computer1"},
            {"speaker": "민정", "text": "아.. 재미없어", "mood": "bored", "effect": -1, "sprite": "girl/computer2"},
        ],
    },
    "study": {
        "scene": "library",
        "delta": -1,
        "steps": [
            {"speaker": "", "text": "도서관에서 민정과 시험 공부를 시작했다.", "mood": "normal", "sprite": "girl/computer1"},
            {"speaker": "민정", "text": "....", "mood": "bored", "sprite": "girl/computer1"},
            {"speaker": "민정", "text": "아.. 재미없어", "mood": "bored", "effect": -1, "sprite": "girl/computer2"},
        ],
    },
    "coffee": {
        "scene": "cafe",
        "delta": 1,
        "steps": [
            {"speaker": "", "text": "학생회관 카페. 민정이 제일 좋아하는 아이스 아메리카노 샷추가 사이즈업을 말없이 내민다.", "mood": "normal"},
            {"speaker": "민정", "text": "....", "mood": "normal", "sprite": "girl/cafe1"},
            {"speaker": "민정", "text": "..어, 고마워. 잘 먹을게", "mood": "normal", "sprite": "girl/cafe1"},
            {"speaker": "", "text": "민정의 얼굴이 붉어진다.", "mood": "blush", "effect": 1, "sprite": "girl/cafe2"},
        ],
    },
    "walk": {
        "scene": "lake",
        "delta": 1,
        "steps": [
            {"speaker": "", "text": "호숫가 한 바퀴 산책.. 물결에 캠프 네온이 비쳤다.", "mood": "normal", "sprite": "girl/lake1"},
            {"speaker": "민정", "text": "....", "mood": "happy", "sprite": "girl/lake1"},
            {"speaker": "민정", "text": "밤 공기 좋다. 이런 건 혼자보단 낫네.", "mood": "happy", "effect": 1, "sprite": "girl/lake2"},
        ],
    },
}

MEALS = {
    "kane": "밥 사줘서 고마워. 잘먹을게.",
    "sarang": "이름값 하네. ....사랑집이라서 고른 거야?",
    "tsutsu": "밥 사줘서 고마워. 잘먹을게.",
}


def require_game():
    if not session.get("started"):
        return redirect(url_for("index"))
    return None


def get_score():
    return int(session.get("likability", 0))


def load_flag():
    env_flag = os.environ.get("CHALLENGE_FLAG")
    if env_flag:
        return env_flag.strip()

    flag_path = BASE_DIR / "flag.txt"
    if flag_path.exists():
        return flag_path.read_text(encoding="utf-8").strip()

    return "FLAG_NOT_CONFIGURED"


@app.context_processor
def inject_game_state():
    return {
        "player_name": session.get("player_name", "나"),
        "likability": get_score(),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:12]
        if not name:
            return render_template("index.html", error="이름을 입력해주세요."), 400

        session.clear()
        session["started"] = True
        session["player_name"] = name
        session["likability"] = 0
        return redirect(url_for("opening"))

    return render_template("index.html")


@app.get("/opening")
def opening():
    guard = require_game()
    if guard:
        return guard
    return render_template("opening.html", scene="campus")


@app.get("/game")
def game():
    guard = require_game()
    if guard:
        return guard
    return render_template("game.html", scene="meeting", options=random.sample(OPTIONS, 3))


@app.post("/activity/<activity_id>")
def activity(activity_id):
    guard = require_game()
    if guard:
        return guard

    activity_data = ACTIVITIES.get(activity_id)
    if not activity_data:
        abort(404)

    session["likability"] = get_score() + activity_data["delta"]
    session["last_result"] = activity_id
    return redirect(url_for("activity_result"))


@app.get("/activity/result")
def activity_result():
    guard = require_game()
    if guard:
        return guard

    activity_id = session.get("last_result")
    activity_data = ACTIVITIES.get(activity_id)
    if not activity_data:
        return redirect(url_for("game"))

    return render_template(
        "activity.html",
        scene=activity_data["scene"],
        steps=activity_data["steps"],
    )


@app.get("/meal")
def meal():
    guard = require_game()
    if guard:
        return guard
    return render_template("meal.html", scene="meeting")


@app.post("/meal/<restaurant>")
def meal_result(restaurant):
    guard = require_game()
    if guard:
        return guard

    line = MEALS.get(restaurant)
    if not line:
        abort(404)

    session["likability"] = get_score() + 1
    steps = [
        {"speaker": "민정", "text": "....", "mood": "happy", "sprite": "girl/meal"},
        {"speaker": "민정", "text": line, "mood": "happy", "effect": 1, "sprite": "girl/meal"},
    ]
    return render_template("activity.html", scene=restaurant, steps=steps)


@app.get("/joke")
def joke():
    guard = require_game()
    if guard:
        return guard

    nonce = secrets.token_urlsafe(18)
    session["joke_nonce"] = nonce
    return render_template("joke.html", scene="joke", joke_nonce=nonce)


@app.post("/api/joke")
def api_joke():
    guard = require_game()
    if guard:
        return jsonify({"error": "게임을 먼저 시작해주세요."}), 401

    data = request.get_json(silent=True) or {}
    nonce = data.get("nonce", "")
    expected_nonce = session.pop("joke_nonce", None)
    if not expected_nonce or not secrets.compare_digest(str(nonce), expected_nonce):
        return jsonify({"error": "이미 사용했거나 잘못된 요청입니다."}), 400

    try:
        client_score = int(data.get("likability"))
    except (TypeError, ValueError):
        return jsonify({"error": "호감도 값이 올바르지 않습니다."}), 400

    client_score = max(-100000, min(client_score, 100000))
    success = random.random() < 0.5
    delta = 1 if success else -1
    session["likability"] = client_score + delta

    return jsonify({
        "success": success,
        "delta": delta,
        "likability": session["likability"],
        "speaker": "" if success else "민정",
        "message": "민정이 피식 웃는다.." if success else "그게 뭔데 이 십덕아..",
    })


@app.get("/confession")
def confession():
    guard = require_game()
    if guard:
        return guard

    nonce = secrets.token_urlsafe(18)
    session["confession_nonce"] = nonce
    return render_template("confession.html", scene="confession", confession_nonce=nonce)


@app.post("/confession")
def confession_result():
    guard = require_game()
    if guard:
        return guard

    nonce = request.form.get("nonce", "")
    expected_nonce = session.pop("confession_nonce", None)
    if not expected_nonce or not secrets.compare_digest(nonce, expected_nonce):
        abort(400)

    if get_score() >= 10000:
        session["flag_authorized"] = True
        return redirect(url_for("ending"))

    return redirect(url_for("confession_failure"))


@app.get("/confession/failure")
def confession_failure():
    guard = require_game()
    if guard:
        return guard
    return render_template("failure.html", scene="confession")


@app.get("/ending")
def ending():
    guard = require_game()
    if guard:
        return guard
    if not session.get("flag_authorized"):
        return redirect(url_for("game"))
    return render_template("ending.html", flag=load_flag(), scene="confession")


@app.post("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
