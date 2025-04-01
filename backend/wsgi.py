from stock_market_api import app
from flask_socketio import SocketIO

# Initialize SocketIO with threading mode and allow CORS from any origin
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Handle socket connection event
@socketio.on('connect')
def handle_connect():
    print("Client connected")

# Handle socket disconnection event
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Handle incoming messages
@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    socketio.send("Hello from server!")

# This will allow the app to run when executed directly
if __name__ == "__main__":
    socketio.run(app, debug=True)
