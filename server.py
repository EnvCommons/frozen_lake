from openreward.environments import Server
from env import FrozenLakeEnvironment

if __name__ == "__main__":
    server = Server([FrozenLakeEnvironment])
    server.run()
