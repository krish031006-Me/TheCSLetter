# TheCSLetter
# 📧 Newsletter Creator & Sender

A **newsletter creator & sender web application** with **SQLite-based user and topic management**.  
This project automates content delivery to multiple users, making it easy to organize and send updates efficiently.

---

## 🚀 Features

- **🌐 Web Interface with Flask** – Manage users, topics, and trigger newsletters via a simple web dashboard.  
- **📤 Newsletter Sending** – Core logic handled by `generate.py` for generating and sending emails.  
- **👥 Subscriber & Topic Management** – Store and manage users and newsletter topics using SQLite.  
- **💡 Developer-Friendly** – Example: weekly digests for programmers.  
- **🛠 Easy to Extend** – Add new templates, content sources, or scheduling.

---

## 🛠️ Tech Stack

- **Python** used for backend development.
- **Flask** for the web app.
- **SQLite** for database management.
- **SMTP** for email delivery.

---

## 📂 Project Structure

newsletter-project/
│  
├── app.py # Flask app with routes, forms, and newsletter triggers  
├── generate.py # Core script to generate & send newsletters  
├── helpers.py # Helper functions (login_required)  
├── users.db # SQLite database for users and topics  
├── templates/ # Newsletter templates  
├── static/ # Contains stylesheets, JS scripts, and images  
├── requirements.txt # list of all the modules needed  
└── README.md # Project documentation  

---

## ⚡ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/krish031006-Me/TheCSLetter.git
cd TheCSLetter
````

### 2. Install Dependencies
```bash 
pip install -r requirements.txt
```

### 3. Configure Email Settings
Enable App Passwords in your email provider.

senderEmail = "your_email@example.com"
password = "your_app_password"

### 4. Run the Flask App
```bash
python app.py
```
# or
```bash
python -m flask run
```
Open your browser and go to http://127.0.0.1:5000 to access the dashboard.

### 📬 Example Newsletter
Subject: Codeforces Weekly Digest

Howdy fellow coder,  
Here is another newsletter on Codeforces. Hope you like it! 😊  

Codeforces is a website that hosts competitive programming contests...

### 🌱 Future Improvements
Add multiple newsletter templates.

Support HTML & CSS formatting for richer newsletters.

Enable automatic scheduling via CRON or Celery.

Add a web interface for subscriber import/export.

### 🧑‍💻 Author
Krish Bhardwaj
Sophomore @ PIET | CS Student | Learning Full-Stack Development | Wants to learn ML and Docker

### ⭐ Contribute
This is primarily a learning project, but contributions, suggestions, and ideas are welcome!

### 📄 License
This project is licensed under the MIT License.

---
