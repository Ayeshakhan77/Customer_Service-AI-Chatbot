# 🤖 AI Customer Service Chatbot  
A lightweight, modular customer service chatbot built using **Flask**, **Python**, **SQLite**, and **TF-IDF NLP**.  
The system supports **three user roles** (Customer, Agent, Admin), real-time chat updates, human escalation, and role-based dashboards.

---

## 📌 Features

### 🟣 **Customer**
- Chat with AI chatbot (TF-IDF–based response engine)
- Automatic escalation to human agent
- Real-time message updates (Observer pattern)
- Post-chat feedback (rating + comment)

### 🔵 **Agent**
- View escalated chat requests
- Respond to customer messages
- Real-time incoming chat polling
- Manage active chat sessions

### 🟠 **Admin**
- View users, chats, and feedback
- Manage knowledge base Q/A pairs  
- System monitoring dashboard

---

## 🏗️ System Architecture

### ✔ **Service-Oriented Architecture (SOA)**
- Independent services for Auth, Chatbot, Messaging, and Dashboard

### ✔ **Layered Architecture**
- Presentation Layer (HTML, CSS, JS)
- Application Layer (Flask MVC)
- Business Logic Layer (ChatBotEngine + Observers)
- Data Layer (SQLite)

---

## 🧩 Design Patterns Used

### 🔹 **Singleton Pattern**
Used in `ChatBotEngine` to ensure:
- Only **one instance** of TF-IDF model loads  
- Faster performance and less memory usage

### 🔹 **Observer Pattern**
Implemented through **JavaScript polling**:
- Customer and Agent dashboards “observe” message table
- UI updates automatically when new messages arrive

### 🔹 **MVC Pattern**
- `templates/` → Views  
- `app.py` → Controller  
- `models.py` → Models  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap, JS |
| NLP | scikit-learn (TF-IDF Vectorizer) |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |

---


---

## 💬 How It Works

### ⚡ Chatbot Flow (TF-IDF Engine)
1. User sends a message  
2. ChatBotEngine preprocesses and vectorizes input  
3. Compares with stored KB questions  
4. If similarity ≥ threshold → return best answer  
5. Else → escalate to agent  

### 🔁 Observer Flow (Real-time Updates)
- JS polls backend `/api/get_messages`
- If new messages found → UI updates automatically

---

🚀 Future Enhancements

Replace TF-IDF with a lightweight LLM

Add WebSockets for true real-time updates

Add analytics dashboard for admin

Voice chatbot integration

Deployment on Render/Verge/AWS

⭐ If you like this project, don’t forget to star the repo!

## ▶️ Running the Project

### **How to run th project : **
```bash
pip install -r requirements.txt

python app.py    

http://127.0.0.1:5000/


