import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager
from PiBrew import socketio, app

manager = Manager(app)

@manager.command
def run():
    socketio.run(app)

if __name__ == "__main__":
    manager.run()
