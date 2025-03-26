# WhatsUp

**WhatsUp** is real-time chat application built with Django and Django Channels. It lets users create accounts, join chat rooms, and communicate instantly with features like group chats and anonymous messaging. Whether you're chatting with your friends or collaborating in groups, WhatsUp makes it seamless and fun!


## Features

- **Real-time Messaging**: Chat instantly using WebSockets.
- **User Authentication**: Secure login and registration.
- **Group Chats**: Create or join group conversations.
- **Anonymous Messaging**: Send messages anonymously in group chats.
- **Message Management**: Edit or delete your messages anytime.
- **Typing Indicators**: See when others are typing.


## Installation

Follow these steps to set up WhatsUp locally. You’ll need Python, pip, Git, and Redis installed.

1. **Install and Run Redis**
    Download and install Redis from [https://redis.io/download](https://redis.io/download), then start the server.
2. **Clone the Repository**
    ```
    git clone https://github.com/Mz-scripter/WhatsUp.git
    ```
3. **Navigate to the Directory**
    ```
    cd WhatsUp
    ```
4. **Create a Virtual Environment**
    ```
        python -m venv venv
    ```
5. **Activate the Virtual Environment**
    ```
    source venv/Scripts/activate
    ```
6. **Install Dependencies**
    ```
    pip install -r requirements.txt
    ```
7. **Set Up the Database**
    ```
    python manage.py migrate
    ```
8. **Create a Superuser (Optional)
    ```
    python manage.py runserver
    ```


## Quick Start 💻
    1. Visit `http://127.0.0.1:8000/chats` in your browser.
    2. Sign up or login.
    3. Create or join a chat room.
    4. Start chatting in real-time.


## Project Structure 📁
    - `chats/` - Core chat functionality.
    - `users/` - Core user functionality.
    - `templates/` - HTML templates for the frontend.
    - `static/` - CSS assets


## Troubleshooting ⚙
    - **Redis Not Running**
        Ensure Redis is installed and running. Check with `redis-server`
    - **Static Files Not Loading**
        Run `python manage.py collectstatic` and verify `STATIC_URL` in `settings.py`
    - **WebSocket Errors**
        Confirm Dango channels is configured in `settings.py`


## Contributing 🤝
Love WhatsUp? Want to improve it? I welcome contributions!
    - Report bugs or suggest features via issues.
    - Submit pull requests with your enhancements.


## License 📃
Licensed under the MIT License