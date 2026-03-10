from flask import Flask, render_template, request, session, redirect, url_for
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "crypto_secret"

ADMIN_KEY = "ASCKII2026"

# Timer duration in seconds (3 minutes)
TIMER_DURATION = 180


# -----------------------------
# DATABASE SETUP
# -----------------------------

def init_db():

    conn = sqlite3.connect("teams.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS teams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT,
        score INTEGER,
        played_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# HELPER — remaining seconds
# -----------------------------

def get_remaining():
    """Returns how many seconds are left for the current team."""
    start_time = session.get("start_time")
    if not start_time:
        return TIMER_DURATION
    elapsed = (datetime.now() - datetime.fromisoformat(start_time)).total_seconds()
    return max(0, int(TIMER_DURATION - elapsed))


# -----------------------------
# WORD DATABASE
# -----------------------------

tech_words = {

# --- BASIC TECH WORDS ---
"wifi":         "Signal that gives internet without a wire",
"google":       "Website where you search for anything",
"mouse":        "Small device you click to use a computer",
"keyboard":     "Device with buttons used to type",
"internet":     "Connection that lets you use websites and apps",
"phone":        "Device used to call, text and use apps",
"screen":       "The display part of any device",
"email":        "Message sent online like a digital letter",
"youtube":      "Website to watch and upload videos",
"password":     "Secret word used to open an account",
"upload":       "Sending a file from your device to internet",
"download":     "Saving a file from internet to your device",
"browser":      "App used to open websites",
"chrome":       "Google's app to browse the internet",
"tablet":       "Touchscreen device bigger than a phone",
"monitor":      "Screen connected to a desktop computer",
"printer":      "Machine that prints files on paper",
"scanner":      "Machine that copies paper into digital file",
"bluetooth":    "Short range wireless connection between devices",
"charger":      "Device that fills battery with power",
"laptop":       "Portable computer that can be folded",
"speaker":      "Device that plays sound out loud",
"microphone":   "Device that captures your voice",
"headphone":    "Device worn on ears to listen privately",
"camera":       "Device used to click photos and record videos",
"router":       "Device that spreads wifi to all devices at home",
"server":       "Computer that stores data for many users",
"firewall":     "System that blocks harmful access to a computer",

# --- C LANGUAGE KEYWORDS ---
"auto":         "Automatically sets storage of a local variable",
"break":        "Exits the loop or switch immediately",
"case":         "One option to match inside a switch",
"char":         "Stores a single character like A or Z",
"const":        "Value that cannot be changed after setting",
"continue":     "Skips current loop step and goes to next",
"default":      "Runs in switch when no case matches",
"do":           "Runs loop body first then checks condition",
"double":       "Stores decimal numbers with high precision",
"else":         "Runs when the if condition is false",
"extern":       "Variable declared outside the current file",
"float":        "Stores decimal numbers like 3.14",
"for":          "Loop that runs a fixed number of times",
"if":           "Runs a block only when condition is true",
"int":          "Stores whole numbers like 1, 10, 100",
"register":     "Stores variable in CPU for faster access",
"return":       "Sends a value back from a function",
"switch":       "Checks a value and jumps to matching case",
"void":         "Means function returns no value",
"while":        "Repeats loop as long as condition is true",
"pointer":      "Stores memory address of another variable",
"array":        "Stores multiple values of same type together",
"function":     "Block of code written once used many times",
"printf":       "Used to display output on screen in C",
"scanf":        "Used to take input from user in C",
"recursion":    "Function that calls itself to solve a problem",
"header":       "File included at top of C program for built-in functions",
"compiler":     "Converts C code into machine understandable language",
"syntax":       "Rules that must be followed while writing code",
"variable":     "Named space in memory to store a value",
"loop":         "Repeats a block of code multiple times",
}


telugu_movies = [
"RRR","Baahubali","Magadheera","Arjun Reddy",
"Pokiri","Ala Vaikunthapurramuloo","Gabbar Singh",
"Race Gurram","Janatha Garage","Bharat Ane Nenu",
"Temper","Fidaa","Geetha Govindam","Julayi",
"Dookudu","Mirchi","Maharshi","Krack",
"Bimbisara","Karthikeya 2","Dasara","HanuMan","Devara"
]


telugu_dialogues = [
"ramulo ramula",
"chuttamalle chuttesavu",
"Aaya sher",
"swing jaraa",
"bahubalii",
"inkem inkem kavalee",
"hilessa hilessa",
"Rangamma Mangamma",
"Odiyamma Heatuu",
"Maate Vinadhuga.",
"Laahe Laahe",
"Adhento gani unnapatuga"
]


# -----------------------------
# START PAGE
# -----------------------------

@app.route("/", methods=["GET", "POST"])
def start():

    if request.method == "POST":

        team = request.form["team"]

        # ✅ Timer starts HERE — the moment team submits their name
        session["team"]       = team
        session["score"]      = 0
        session["start_time"] = datetime.now().isoformat()  # <-- timer begins

        conn = sqlite3.connect("teams.db")
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO teams (team_name, score, played_at) VALUES (?,?,?)",
            (team, 0, datetime.now())
        )
        conn.commit()
        conn.close()

        return redirect(url_for("game"))

    return render_template("start.html")


# -----------------------------
# GAME PAGE
# -----------------------------

@app.route("/game")
def game():

    if "team" not in session:
        return redirect(url_for("start"))

    # Check if time already ran out before even loading hint
    remaining = get_remaining()
    if remaining <= 0:
        return redirect(url_for("timeout"))

    word = random.choice(list(tech_words.keys()))
    session["word"] = word

    hint = tech_words[word]

    return render_template(
        "index.html",
        hint=hint,
        timer=remaining,               # passes exact remaining seconds
        word=word,
        team=session.get("team"),
        score=session.get("score", 0)
    )


# -----------------------------
# CHECK ANSWER
# -----------------------------

@app.route("/unlock", methods=["POST"])
def unlock():

    guess = request.form["password"].strip().lower()
    word  = session.get("word")

    # ✅ Server-side time check — uses the SAME start_time from registration
    remaining = get_remaining()
    if remaining <= 0:
        return redirect(url_for("timeout"))

    if guess == word:

        session["score"] += 1

        conn = sqlite3.connect("teams.db")
        cur  = conn.cursor()
        cur.execute(
            "UPDATE teams SET score=? WHERE team_name=?",
            (session["score"], session["team"])
        )
        conn.commit()
        conn.close()

        reward_type  = random.choice(["movie", "dialogue"])
        reward_value = (
            random.choice(telugu_movies)   if reward_type == "movie"
            else random.choice(telugu_dialogues)
        )

        session["reward_type"]  = reward_type
        session["reward_value"] = reward_value

        return redirect(url_for("reward"))

    else:

        hint       = tech_words[word]
        small_hint = f"{len(word)} letters"
        remaining  = get_remaining()   # recalculate after processing

        return render_template(
            "index.html",
            hint=hint,
            error=True,
            small_hint=small_hint,
            timer=remaining,
            word=word,
            team=session.get("team"),
            score=session.get("score", 0)
        )


# -----------------------------
# TIMEOUT PAGE
# -----------------------------

@app.route("/timeout")
def timeout():
    word = session.get("word", "???")
    return render_template(
        "timeout.html",
        word=word,
        team=session.get("team"),
        score=session.get("score", 0)
    )


# -----------------------------
# REWARD PAGE
# -----------------------------

@app.route("/reward")
def reward():
    remaining = get_remaining()
    if remaining <= 0:
        return redirect(url_for("timeout"))

    return render_template(
        "secret.html",
        reward_type=session.get("reward_type"),
        reward_value=session.get("reward_value"),
        team=session.get("team"),
        score=session.get("score"),
        timer=remaining
    )


# -----------------------------
# NEXT TEAM — clears everything
# -----------------------------

@app.route("/next_team")
def next_team():
    session.clear()
    return redirect(url_for("start"))


# -----------------------------
# ADMIN LOGIN
# -----------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":
        key = request.form["key"]
        if key == ADMIN_KEY:
            conn = sqlite3.connect("teams.db")
            cur  = conn.cursor()
            cur.execute("SELECT * FROM teams")
            data = cur.fetchall()
            conn.close()
            return render_template("admin.html", data=data)

    return render_template("admin_login.html")


if __name__ == "__main__":
    app.run(debug=True)
