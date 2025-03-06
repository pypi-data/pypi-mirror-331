
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class JWTHandler(BaseHTTPRequestHandler):
    # Shared state to signal when JWT is received
    jwt_received = threading.Event()
    jwt_value = None

    # We don't want default messages being printed in command line.
    def log_message(self, format, *args):
        pass  # Override to suppress logging

    def do_GET(self):
        # Parse the query string
        parsed_url = urlparse(self.path)
        if parsed_url.path != '/':
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found\n")
            return
        query_params = parse_qs(parsed_url.query)
        # Extract the 'jwt' value
        jwt_values = query_params.get('jwt')
        jwt = jwt_values[0] if jwt_values else None

        if jwt:
            JWTHandler.jwt_value = jwt  # Store the received JWT
            JWTHandler.jwt_received.set()  # Signal that the JWT has been received
        else:
            print("Failed to authenticate.")
            exit(1)

        # Respond with a 200 OK
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Logged in! Please switch back to your terminal to continue..\n")

def start_server_in_background():
    # Create and bind the server
    try:
        server = HTTPServer(('localhost', 0), JWTHandler)
    except OSError as e:
        raise RuntimeError(f"Failed to bind the server: {e}")

    # Get the assigned port
    assigned_port = server.server_address[1]

    # Start the server in a separate thread
    try:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
    except Exception as e:
        raise RuntimeError(f"Failed to start the server thread: {e}")

    return assigned_port, server, JWTHandler