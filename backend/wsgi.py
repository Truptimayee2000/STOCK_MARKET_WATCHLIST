from stock_market_api import app
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    socketio.send("Hello from server!")

if __name__ == "__main__":
    socketio.run(app, debug=True)
