import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager
from PiBrew import socketio, app, thread

manager = Manager(app)

@manager.command
def run():
    socketio.run(app, host='0.0.0.0', port=8888)

if __name__ == "__main__":
    try:
    	manager.run()
    finally:
    	thread._stop.set()
