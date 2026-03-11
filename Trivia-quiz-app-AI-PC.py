import tkinter as tk
from firebase_admin import credentials, initialize_app, db
import firebase_admin
import random
import hashlib
import os
import sys
import re
import pygame
import threading
from dotenv import load_dotenv # חובה להוסיף

# טעינת משתני הסביבה מקובץ .env
load_dotenv()

# ======================
# הגדרות נתיבים
# ======================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ======================
# אתחול סאונד
# ======================
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    sound_ready = True
except:
    sound_ready = False

def play_sfx(name):
    if not sound_ready: return
    def _play():
        try:
            path = resource_path(os.path.join("sounds", f"{name}.mp3"))
            if os.path.exists(path):
                pygame.mixer.Sound(path).play()
        except: pass
    threading.Thread(target=_play, daemon=True).start()

# ======================
# חיבור ל-Firebase (מעודכן ומאובטח)
# ======================
firebase_ready = False

# שליפת הנתונים מה-ENV במקום לכתוב אותם בקוד
FIREBASE_JSON = os.getenv("FIREBASE_JSON_NAME")
DB_URL = os.getenv("FIREBASE_DB_URL")

try:
    if not firebase_admin._apps and FIREBASE_JSON and DB_URL:
        json_path = resource_path(FIREBASE_JSON)
        if os.path.exists(json_path):
            cred = credentials.Certificate(json_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': DB_URL
            })
            firebase_ready = True
except Exception as e:
    print(f"Firebase Error: {e}")

# ======================
# ניהול Session
# ======================
# גם כאן, עדיף להשתמש בשם קובץ כללי או להגדיר ב-ENV
SESSION_FILE = os.path.join(os.getcwd(), "user_session.txt")

def save_session(username):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            f.write(str(username))
    except:
        pass

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return f.read().strip() or None
        except:
            return None
    return None

def delete_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except:
            pass

# ======================
# עיצוב רספונסיבי
# ======================
BG, CARD, BTN, BTN2, BTN_EXIT = "#1e1e2e", "#2a2a3d", "#4CAF50", "#2196F3", "#ff5555"

root = tk.Tk()
root.geometry("450x700")
root.title("TriviaQuiz")
root.configure(bg=BG)

main_container = None

def clear_screen():
    global main_container
    for w in root.winfo_children(): w.destroy()
    main_container = tk.Frame(root, bg=BG)
    main_container.place(relx=0.5, rely=0.5, anchor="center")

def create_title(text):
    tk.Label(main_container, text=text, bg=BG, fg="white", font=("Arial", 26, "bold"), pady=20).pack()

def create_input(label, is_pass=False):
    frame = tk.Frame(main_container, bg=CARD, padx=15, pady=10)
    frame.pack(pady=10, fill="x")
    tk.Label(frame, text=label, bg=CARD, fg="#bbbbbb", font=("Arial", 11)).pack(anchor="e")
    e = tk.Entry(frame, bg="#3a3a4d", fg="white", insertbackground="white", font=("Arial", 16),
                 show="*" if is_pass else "", justify="right", bd=0)
    e.pack(fill="x", pady=5)
    return e

def create_btn(text, command, color=BTN):
    b = tk.Button(main_container, text=text, command=command, bg=color, fg="white", font=("Arial", 14, "bold"),
                  bd=0, cursor="hand2", width=25, activebackground="#66bb6a")
    b.pack(pady=10, ipady=8)
    return b

def hash_pass(p):
    return hashlib.sha256((str(p) + "TriviaQuiz").encode()).hexdigest()

def get_questions():
    if not firebase_ready: return [("אין חיבור", "שגיאה")]
    try:
        data = db.reference("/questions").get()
        if not data: return []
        if isinstance(data, dict): return [(v['q'], v['a']) for v in data.values() if v and 'q' in v]
        if isinstance(data, list): return [(q['q'], q['a']) for q in data if q and 'q' in q]
    except:
        return []
    return []

# ======================
# מנוע המשחק
# ======================
class TriviaGame:
    def __init__(self, user, questions_list):
        self.user = user
        self.questions = random.sample(questions_list, min(10, len(questions_list)))
        self.idx = 0
        self.score = 0
        self.timer_id = None
        self.is_checking = False
        self.next_round()

    def next_round(self):
        clear_screen()
        if self.idx >= len(self.questions):
            self.finish_game()
            return

        self.is_checking = False
        q_text, _ = self.questions[self.idx]
        create_title(f"שאלה {self.idx + 1} מתוך {len(self.questions)}")

        stat_f = tk.Frame(main_container, bg=BG)
        stat_f.pack(fill="x")
        tk.Label(stat_f, text=f"🏆 ניקוד: {self.score}", bg=BG, fg="white", font=("Arial", 12)).pack(side="left")
        self.time_left = 15
        self.timer_lbl = tk.Label(stat_f, text=f"⏱️ {self.time_left}", bg=BG, fg="#ffcc00", font=("Arial", 14, "bold"))
        self.timer_lbl.pack(side="right")

        card = tk.Frame(main_container, bg=CARD, pady=40, padx=20)
        card.pack(pady=20, fill="x")
        tk.Label(card, text=q_text, bg=CARD, fg="white", font=("Arial", 18, "bold"), wraplength=400,
                 justify="center").pack()

        self.ans_entry = tk.Entry(main_container, bg="#3a3a4d", fg="white", font=("Arial", 20), justify="center",
                                  insertbackground="white", bd=0)
        self.ans_entry.pack(pady=15, fill="x", ipady=10)
        self.ans_entry.focus_set()
        self.ans_entry.bind("<Return>", lambda e: self.check_answer())

        create_btn("בדוק תשובה", self.check_answer)
        create_btn("פרוש", self.finish_game, BTN_EXIT)
        self.run_timer()

    def run_timer(self):
        if not root.winfo_exists(): return
        if self.time_left > 0:
            self.time_left -= 1
            if self.timer_lbl.winfo_exists():
                self.timer_lbl.config(text=f"⏱️ {self.time_left}")
            self.timer_id = root.after(1000, self.run_timer)
        else:
            self.check_answer(is_timeout=True)

    def check_answer(self, is_timeout=False):
        if self.is_checking: return
        self.is_checking = True
        if self.timer_id: root.after_cancel(self.timer_id)

        _, correct_raw = self.questions[self.idx]
        user_input = " ".join(self.ans_entry.get().split()).lower()
        valid_options = [opt.strip().lower() for opt in re.split(r'[/|]', str(correct_raw))]

        if not is_timeout and user_input in valid_options and user_input != "":
            self.score += 1
            res_txt, res_color = "✨ תשובה נכונה!", "#4CAF50"
            play_sfx("correct") # סאונד תשובה נכונה
        else:
            first_ans = str(correct_raw).replace('|', '/').split('/')[0]
            res_txt = f"⌛ זמן עבר! התשובה: {first_ans}" if is_timeout else f"❌ טעות! התשובה: {first_ans}"
            res_color = "#ff5555"
            play_sfx("wrong") # סאונד טעות

        tk.Label(main_container, text=res_txt, bg=BG, fg=res_color, font=("Arial", 14, "bold")).pack(pady=15)
        self.idx += 1
        root.after(2000, self.next_round)

    def finish_game(self):
        if self.timer_id: root.after_cancel(self.timer_id)
        clear_screen()
        create_title("🏁 סיכום משחק")
        if firebase_ready:
            db.reference(f"/users/{self.user}/points").transaction(lambda c: (c if c is not None else 0) + self.score)

        tk.Label(main_container, text=f"השגת {self.score} נקודות", bg=BG, fg="white", font=("Arial", 20)).pack(pady=30)
        create_btn("משחק חדש", lambda: TriviaGame(self.user, get_questions()))
        create_btn("תפריט ראשי", main_menu, "#888")

# ======================
# ניהול מסכים
# ======================
def main_menu():
    clear_screen()
    create_title("🎮 Trivia Quiz")
    if current_user:
        tk.Label(main_container, text=f"שלום, {current_user}", bg=BG, fg=BTN2, font=("Arial", 14)).pack(pady=10)
        create_btn("התחל משחק", lambda: TriviaGame(current_user, get_questions()))
        create_btn("לוח תוצאות", show_leaderboard, "#ff9800")
        create_btn("התנתק", handle_logout, BTN_EXIT)
    else:
        create_btn("התחברות", login_page)
        create_btn("הרשמה", register_page, BTN2)
    create_btn("יציאה", root.quit, "#444")

def login_page():
    clear_screen()
    create_title("🔑 כניסה")
    u_f, p_f = create_input("שם משתמש"), create_input("סיסמה", True)

    def do_login():
        global current_user
        name = u_f.get().strip()
        users = db.reference("/users").get() or {}
        if name in users and users[name]["password"] == hash_pass(p_f.get()):
            current_user = name
            save_session(name)
            main_menu()
        else:
            tk.Label(main_container, text="פרטים שגויים", bg=BG, fg="red").pack()

    create_btn("התחבר", do_login)
    create_btn("חזרה", main_menu, "#888")

def register_page():
    clear_screen()
    create_title("📝 הרשמה")
    u_f, p_f = create_input("שם משתמש"), create_input("סיסמה", True)

    def do_reg():
        name, pwd = u_f.get().strip(), p_f.get()
        if len(name) < 2 or len(pwd) < 4: return
        db.reference(f"/users/{name}").set({"password": hash_pass(pwd), "points": 0})
        login_page()

    create_btn("הירשם", do_reg)
    create_btn("חזרה", main_menu, "#888")

def show_leaderboard():
    clear_screen()
    create_title("🏆 מובילים")
    data = db.reference("/users").get() or {}
    top = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:5]
    for i, (u, d) in enumerate(top, 1):
        f = tk.Frame(main_container, bg=CARD)
        f.pack(pady=5, fill="x")
        tk.Label(f, text=f"{i}. {u} — {d.get('points', 0)}", bg=CARD, fg="white", font=("Arial", 14), padx=20).pack(
            pady=10)
    create_btn("חזרה", main_menu, "#888")

def handle_logout():
    global current_user
    current_user = None
    delete_session()
    main_menu()

current_user = load_session()
main_menu()
root.mainloop()