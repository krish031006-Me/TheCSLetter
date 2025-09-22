from cs50 import SQL
db = SQL("sqlite:///users.db")
username = "kaka"
details = db.execute("SELECT * FROM users WHERE username = ?", username)
if details[0]["status"] == 'unsubscribed':
    print("Helo")
else:
    print("Helooooo")
