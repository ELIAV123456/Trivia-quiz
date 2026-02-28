import tkinter as tk
from firebase_admin import credentials, initialize_app, db
import random
import firebase_admin

# ======================
# התחברות ל-Firebase
# ======================
cred = credentials.Certificate(r"C:\Users\USER\PyCharmMiscProject\triviaquizapp-8b15c-firebase-adminsdk-fbsvc-7b8c4c04f3.json")  # הקובץ שהורדת
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://triviaquizapp-8b15c-default-rtdb.firebaseio.com/'  # החלף ב-URL של הפרויקט שלך
})

# ======================
# עיצוב
# ======================

BG = "#1e1e2e"
CARD = "#2a2a3d"
BTN = "#4CAF50"
BTN2 = "#2196F3"

root = tk.Tk()
root.geometry("400x550")
root.title("Trivia App")
root.configure(bg=BG)

def clear():
    for w in root.winfo_children():
        w.destroy()

def title(text):
    tk.Label(root, text=text,
             bg=BG, fg="white",
             font=("Arial", 22, "bold")).pack(pady=15)

def msg(text, color="white"):
    tk.Label(root, text=text,
             bg=BG, fg=color,
             font=("Arial", 12)).pack(pady=5)

def input_box(label):
    frame = tk.Frame(root, bg=CARD)
    frame.pack(pady=8, padx=20, fill="x")
    tk.Label(frame, text=label,
             bg=CARD, fg="#bbbbbb",
             font=("Arial", 10)).pack(anchor="w", padx=10)
    e = tk.Entry(frame,
                 bg="#3a3a4d",
                 fg="white",
                 insertbackground="white",
                 relief="flat",
                 font=("Arial", 14))
    e.pack(fill="x", padx=10, pady=5)
    return e

def btn(text, command, color=BTN):
    tk.Button(root,
              text=text,
              command=command,
              bg=color,
              fg="white",
              font=("Arial", 12, "bold"),
              bd=0,
              padx=10,
              pady=8).pack(pady=6)

# ======================
# לוגיקה
# ======================

current_user = None

questions = [
    ("כמה זה 2+2?", "4"),
    ("בירת ישראל?", "ירושלים"),
    ("כמה ימים יש בשבוע?", "7"),
    ("כמה צבעים יש בקשת?", "7"),
    ("כמה רגליים יש לחתול?", "4"),
    ("מהו החיה הגדולה ביותר בעולם?", "לוויתן כחול"),
    ("כמה שעות יש ביום?", "24"),
    ("כמה דקות יש בשעה?", "60"),
    ("כמה חודשים יש בשנה?", "12"),
    ("מהי העיר הכי גדולה בישראל?", "תל אביב"),
    ("כמה כוכבים יש במערכת השמש?", "1"),
    ("איזה חומר נמצא במים במצב מוצק?", "קרח"),
    ("איזה צבעי דגל ישראל?", "כחול ולבן"),
    ("מי כתב את ״הארי פוטר״?", "ג׳יי קיי רולינג"),
    ("מהי המדינה הכי גדולה בעולם?", "רוסיה"),
    ("כמה קצות יש למשולש?", "3"),
    ("כמה צלעות יש למרובע?", "4"),
    ("מהו היבשת הקטנה ביותר?", "אוסטרליה"),
    ("כמה שחקנים יש בקבוצה בכדורגל?", "11"),
    ("מהו המספר הגדול ביותר בין 10, 12 ו-9?", "12"),
    ("מהו היסוד הכימי שמסומן ב-O?", "חמצן"),
    ("כמה שבועות יש בשנה?", "52"),
    ("מי גילה את אמריקה?", "כריסטופר קולומבוס"),
    ("מהי העיר הכי צפונית בעולם?", "סברבארד"),
    ("מהו ההר הגבוה ביותר בעולם?", "איוורסט"),
    ("כמה סנטימטרים יש במטר?", "100"),
    ("מהי השפה המדוברת ביותר בעולם?", "סינית מנדרינית"),
    ("מהו הים הגדול ביותר בעולם?", "הים הפיליפיני"),
    ("כמה כוכבים יש בדגל ארצות הברית?", "50"),
    ("מהי המילה הארוכה ביותר בעברית?", "וכשבהשתעשעויותיכם"),
    ("מהו הירח של כדור הארץ?", "ירח"),
    ("מי המציא את החשמל?", "תומאס אדיסון"),
    ("מהי מערכת הדם בגוף האדם?", "הלב וכלי הדם"),
    ("כמה עצמות יש בגוף האדם?", "206"),
    ("מהו הכוכב הקרוב ביותר לשמש?", "חמה"),
    ("איזה עץ נותן אצטרובל?", "אורן"),
    ("כמה צבעים יש בדגל גרמניה?", "3"),
    ("מהי החיה המהירה ביותר?", "צ׳יטה"),
    ("כמה ימים יש בפברואר בשנה רגילה?", "28"),
    ("כמה ימים יש בפברואר בשנה מעוברת?", "29"),
    ("מי היה ראש הממשלה הראשון של ישראל?", "דוד בן גוריון"),
    ("מהי הבירה של צרפת?", "פריז"),
    ("כמה מדינות יש באירופה?", "44"),
    ("מהי החיה הלאומית של ישראל?", "היעל"),
    ("מהו המאכל הלאומי של יפן?", "סושי"),
    ("מהו היסוד הכימי שמסומן ב-Fe?", "ברזל"),
    ("מהו האי הגדול ביותר בעולם?", "גרינלנד"),
    ("מי כתב את ״האודיסאה״?", "הומרוס"),
    ("מהו הכוח שמושך חפצים כלפי מטה?", "כבידה"),
    ("כמה קילומטרים יש בקילומטר מרובע?", "1000000"),
    ("מי צייר את המונה ליזה?", "לאונרדו דה וינצ׳י"),
    ("מהו הממלכה הגדולה ביותר בעולם?", "בריטניה"),
    ("מהו כלי הנשיפה?", "חצוצרה"),
    ("מהי התקופה בה חיו הדינוזאורים?", "המזוזואיקון"),
    ("מי גילה את הכבידה?", "אייזק ניוטון"),
    ("מהו הרכב האוויר שאנחנו נושמים?", "חנקן וחמצן"),
    ("מהו המטבע של ארצות הברית?", "דולר"),
]

def get_user_data():
    ref = db.reference("/users")
    return ref.get() or {}

def save_user_data(users):
    ref = db.reference("/users")
    ref.set(users)

def chack_index(name):
    users = get_user_data()
    if name in users:
        return name
    return None

# ======================
# לוח נקודות
# ======================
def scoreboard_screen():
    clear()
    title("🏆 לוח נקודות")

    users = get_user_data()
    # סדר לפי ניקוד יורד
    sorted_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)

    for u, data in sorted_users:
        frame = tk.Frame(root, bg=CARD)
        frame.pack(pady=5, padx=20, fill="x")
        tk.Label(frame, text=f"{u} - {data['points']} נקודות",
                 bg=CARD, fg="white",
                 font=("Arial", 13)).pack(pady=8)

    btn("חזרה", menu, "#888")

# ======================
# משחק
# ======================
def game():
    clear()
    title("🎮 משחק")
    users = get_user_data()
    if current_user not in users:
        users[current_user] = {"password": "dummy", "points": 0}  # נקודת התחלה
        save_user_data(users)

    current_points = users[current_user]["points"]
    qs = questions.copy()
    random.shuffle(qs)
    question_index = 0

    def ask():
        nonlocal question_index, current_points
        clear()
        title("❓ שאלה")
        msg(f"ניקוד: {current_points}")

        if question_index >= len(qs):
            end_game()
            return

        q, a = qs[question_index]

        frame = tk.Frame(root, bg=CARD)
        frame.pack(pady=20, padx=20, fill="x")
        tk.Label(frame, text=q, bg=CARD, fg="white", font=("Arial", 14), wraplength=300).pack(pady=15)
        ans = tk.Entry(root, bg="#3a3a4d", fg="white", insertbackground="white", font=("Arial", 14))
        ans.pack(pady=10)

        def check():
            nonlocal current_points
            if ans.get() == a:
                current_points += 1
                msg("🎉 נכון!", "green")
            else:
                msg(f"❌ טעות: {a}", "red")
            next_step()

        btn("בדוק", check)

    def next_step():
        def next_q():
            nonlocal question_index
            question_index += 1
            ask()
        btn("המשך", next_q)
        btn("סיים משחק", end_game, "#888")

    def end_game():
        clear()
        title("🏁 סוף משחק")
        # שמירת ניקוד ב-Firebase
        users = get_user_data()
        users[current_user]["points"] = current_points
        save_user_data(users)
        msg(f"הניקוד שלך: {current_points}")
        btn("שחק שוב", game)
        btn("לוח נקודות", scoreboard_screen, "#ff9800")
        btn("תפריט", menu, "#888")

    ask()

# ======================
# התחברות
# ======================
def login():
    clear()
    title("🔑 התחברות")
    name = input_box("שם משתמש")
    password = input_box("סיסמה")

    def submit():
        global current_user
        users = get_user_data()
        if name.get() not in users:
            msg("משתמש לא קיים", "red")
            return
        if users[name.get()]["password"] != password.get():
            msg("סיסמה שגויה", "red")
            return
        current_user = name.get()
        msg("התחברת בהצלחה!", "green")
        btn("המשך למשחק", game)

    btn("התחבר", submit)
    btn("חזרה", menu, "#888")

# ======================
# הרשמה
# ======================
def register():
    clear()
    title("📝 הרשמה")
    name = input_box("שם משתמש")
    password = input_box("סיסמה")

    def submit():
        users = get_user_data()
        if name.get() in users:
            msg("שם תפוס", "red")
            return
        users[name.get()] = {"password": password.get(), "points": 0}
        save_user_data(users)
        msg("נרשמת בהצלחה!", "green")

    btn("הרשם", submit)
    btn("חזרה", menu, "#888")

# ======================
# תפריט
# ======================
def menu():
    clear()
    title("🎮 Trivia Quiz")
    btn("התחברות", login)
    btn("הרשמה", register, BTN2)
    btn("צא", root.quit, "#ff5555")

# ======================
# הפעלת האפליקציה
# ======================
menu()
root.mainloop()