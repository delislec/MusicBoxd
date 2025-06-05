# test_subscriber.py
import zmq

def test_subscriber():
    ctx = zmq.Context()
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")  # Connect to the publisher's port (5556)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "recommendation")  # Subscribe to the "recommendation" topic

    print("Debug: Waiting for messages...")
    try:
        topic = subscriber.recv_string()
        response = subscriber.recv_json()
        print(f"Debug: Received message: {response}")
    except zmq.Again:
        print("Debug: No message received.")
    
if __name__ == "__main__":
    test_subscriber()
