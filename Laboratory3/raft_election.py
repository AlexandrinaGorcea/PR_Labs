import socket
import threading
import time
import random

NUM_NODES = 5
ELECTION_TIMEOUT_MIN = 1
ELECTION_TIMEOUT_MAX = 3
HEARTBEAT_INTERVAL = 0.5
PORT = 6020

# Global variables
nodes = []
leader = None


class Node(threading.Thread):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.state = 'follower'
        self.votes_received = 0
        self.last_heartbeat_time = time.time()
        self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.current_term = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', PORT + self.id))
        self.sock.settimeout(0.1)  # Set a small timeout for non-blocking receive

    def run(self):
        global leader
        while True:
            if self.state == 'follower':
                self.follower_behavior()
            elif self.state == 'candidate':
                self.candidate_behavior()
            elif self.state == 'leader':
                self.leader_behavior()
            time.sleep(0.1)  # Sleep to avoid busy-waiting

    def follower_behavior(self):
        current_time = time.time()
        if current_time - self.last_heartbeat_time > self.election_timeout:
            self.convert_to_candidate()
        else:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode()
                if message.startswith('heartbeat'):
                    self.last_heartbeat_time = time.time()
                    print(f"Node {self.id} received heartbeat from leader")
                elif message.startswith('vote_request'):
                    sender_id = int(message.split()[1])
                    self.send_vote(sender_id)
            except socket.timeout:
                pass  # No data received, continue

    def convert_to_candidate(self):
        global leader
        self.state = 'candidate'
        self.votes_received = 1
        self.current_term += 1
        print(f"Node {self.id} is now a candidate in term {self.current_term}")
        self.request_votes()

    def request_votes(self):
        for i in range(NUM_NODES):
            if i != self.id:
                self.sock.sendto(f'vote_request {self.id}'.encode(), ('localhost', PORT + i))

    def candidate_behavior(self):
        if self.votes_received > NUM_NODES // 2:
            self.state = 'leader'
            leader = self.id
            print(f"Node {self.id} is now the leader")
        else:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode()
                if message.startswith('vote'):
                    self.votes_received += 1
            except socket.timeout:
                pass  # No data received, continue

    def leader_behavior(self):
        for i in range(NUM_NODES):
            if i != self.id:
                self.sock.sendto('heartbeat'.encode(), ('localhost', PORT + i))
        time.sleep(HEARTBEAT_INTERVAL)

    def send_vote(self, candidate_id):
        self.sock.sendto('vote'.encode(), ('localhost', PORT + candidate_id))


def main():
    global nodes
    for i in range(NUM_NODES):
        node = Node(i)
        nodes.append(node)
        node.start()


if __name__ == '__main__':
    main()