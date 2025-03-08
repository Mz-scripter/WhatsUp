# WhatsUp

Start Redis Server
sudo systemctl enable redis-server
sudo systemctl start redis-server
systemctl status redis-server
redis-cli
ping

Run the server with daphne
daphne -p 8000 whatsup.asgi:application