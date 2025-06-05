import zmq

def main():
    # Set up the ZeroMQ REP socket
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)  # REP (Response) socket
    socket.bind("tcp://*:5556")  # Bind to port 5556
    print("Server ready on port 5556.")

    while True:
        try:
            # Receive request
            message = socket.recv_json()
            print("Received request:", message)

            # Create a response
            response = {"status": "ok", "message": "Test response received!"}
            print("Sending response:", response)

            # Send the response
            socket.send_json(response)
        except Exception as e:
            print("Error in server:", e)

if __name__ == "__main__":
    main()
