from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import subprocess
import os
import sys

class GameHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run_game():
    python_executable = sys.executable
    game_path = os.path.join(os.path.dirname(__file__), 'main.py')
    try:
        subprocess.Popen([python_executable, game_path], cwd=os.path.dirname(__file__))
    except Exception as e:
        print(f"Error starting game: {e}")

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, GameHandler)
    print("Server running at http://localhost:8000")
    print("Game window should open separately")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start the game
    run_game()

    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Open the browser
    webbrowser.open('http://localhost:8000')

    # Keep the main thread running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down server...")