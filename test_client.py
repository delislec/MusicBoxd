import zmq

def main():
    # Set up the ZeroMQ REQ socket
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)  # REQ (Request) socket
    socket.connect("tcp://localhost:5556")  # Connect to port 5556
    print("Client connected to server on port 5556.")

    try:
        # Send a test request
        request = {"action": "test", "message": "Hello from client!"}
        print("Sending request:", request)
        socket.send_json(request)

        # Receive the response
        response = socket.recv_json()
        print("Received response:", response)
    except Exception as e:
        print("Error in client:", e)

if __name__ == "__main__":
    main()
