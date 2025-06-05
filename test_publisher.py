# test_publisher.py
import zmq
import time

def test_publisher():
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind("tcp://*:5556")  # Bind to port 5556
    time.sleep(1)  # Allow time for the socket to initialize

    # Simulate sending a recommendation message
    message = {
        "type": "music",
        "titles": [
            {"name": "Mock Song 1", "artists": [{"name": "Mock Artist 1"}]},
            {"name": "Mock Song 2", "artists": [{"name": "Mock Artist 2"}]}
        ],
        "error_flag": False,
        "error_message": ""
    }
    
    print(f"Debug: Broadcasting message: {message}")
    publisher.send_string("recommendation", zmq.SNDMORE)
    publisher.send_json(message)  # Send the message to subscribers

if __name__ == "__main__":
    test_publisher()
