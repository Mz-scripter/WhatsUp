# 🚀 WhatsUp – Real-Time Anonymous Chat App

WhatsUp is a **real-time chat application** built with **Django** and **Django Channels**. It lets users create accounts, join chat rooms, and communicate instantly. Whether you're chatting with friends or collaborating in groups, WhatsUp makes conversations **seamless and fun**—and with **anonymous messaging**, you can speak your mind without revealing your identity!

## ✨ Features 

- **💬 Real-Time Messaging** – Instant chats powered by WebSockets.  
- **🔐 User Authentication** – Secure login & registration.  
- **👥 Group Chats** – Create or join group conversations.  
- **🕵️ Anonymous Messaging** – Send messages anonymously in group chats.  
- **✏️ Message Management** – Edit or delete your messages anytime.  
- **⌨️ Typing Indicators** – See when others are typing.


## 🛠 Installation  

Follow these steps to set up **WhatsUp** locally. You'll need **Python, pip, Git, and Redis** installed.  

### 1️⃣ Install and Run Redis  
- Download and install Redis from [here](https://redis.io/download).  
- Start the Redis server using:  
  ```
  redis-server
  ```

### 2️⃣ Clone the Repository
    ```
    git clone https://github.com/Mz-scripter/WhatsUp.git
    cd WhatsUp
    ```

### 3️⃣ Set Up a Virtual Environment
    ```
    python -m venv venv
    source venv/Scripts/activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

### 4️⃣ Install Dependencies
    ```
    pip install -r requirements.txt
    ```

### 5️⃣ Set Up the Database
    ```
    python manage.py migrate
    ```

### 6️⃣ Start the Development Server
    ```
    python manage.py runserver
    ```


## 🚀 Quick Start

1️⃣ Open your browser and visit: `http://127.0.0.1:8000/`
2️⃣ Sign up or log in.
3️⃣ Create or join a chat room.
4️⃣ Start chatting in real-time! 🎉


## 📁 Project Structure
    ```
    📂 WhatsUp/
    ├── 📂 chats/        # Core chat functionality
    ├── 📂 users/        # User authentication & management
    ├── 📂 templates/    # HTML templates for the frontend
    ├── 📂 static/       # CSS & other static assets
    ├── 📄 manage.py     # Django project entry point
    └── 📄 requirements.txt  # Dependencies
    ```

## ⚙️ Troubleshooting

### 💡 Redis Not Running?
    - Ensure Redis is installed and running:
        ```
        redis-server
        ```

### 💡 Static Files Not Loading?
    - Run:
        ```
        python manage.py collectstatic
        ```

### 💡 WebSocket Errors?
    - Ensure Django Channels is correctly set up in settings.py.


## 🤝 Contributing
Love WhatsUp? Want to improve it? Contributions are welcome! 🎉
- 🐛 Report bugs or 💡 suggest features via GitHub Issues.
- 🔧 Submit pull requests with your enhancements.

