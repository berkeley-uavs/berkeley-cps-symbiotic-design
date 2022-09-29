import argparse
import threading
import time

from backend.operations.rating import Rating
from os import walk
from time import strftime

from sym_cps.optimizers.concrete_opt import ConcreteOptimizer
from sym_cps.optimizers.params_opt import ParametersOptimizer
from sym_cps.optimizers.topo_opt import TopologyOptimizer
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from typing import Any, Dict

from flask import Flask, Response, request
from flask_socketio import SocketIO, emit

from src.backend.shared.paths import build_path, storage_path

parser = argparse.ArgumentParser(description="Launching Flask Backend")
parser.add_argument("--serve", default=False, type=bool, help="indicate if serving the pages")
args = parser.parse_args()

if args.serve:
    print("Serving the web pages from the build folder")
    app = Flask(__name__, static_folder=str(build_path), static_url_path="/")
else:
    print("Launching Backend")
    app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

c_library, designs = parse_library_and_seed_designs()
topo_opt = TopologyOptimizer(library=c_library)
concr_opt = ConcreteOptimizer(library=c_library)
para_opt = ParametersOptimizer(library=c_library)


users: Dict[str, Any] = {}
# String dictionary associating the id of the request to talk to the user with the session id given by the frontend.

cookies: Dict[str, str] = {}
# String dictionary association the id of the session with that of the cookie that can open it.


@socketio.on("connect")
def connected() -> None:
    """Establish the connection between the front and the back while checking
    that the session is not already in use."""
    print("Connected")
    print(f'ID {request.args.get("id")}')
    lock = threading.Lock()
    lock.acquire()
    session_id = str(request.args.get("id"))
    cookie = str(request.args.get("cookie"))
    tab_id = str(request.args.get("tabId"))
    if session_id in users:  # Check if this session is already open
        if cookie != cookies[session_id]:
            emit("is-connected", False, room=request.sid)
            return
    else:
        users[session_id] = {}
    users[session_id][tab_id] = request.sid
    cookies[session_id] = cookie
    now = time.localtime(time.time())
    emit(
        "send-message", strftime("%H:%M:%S", now) + f" Connected to session {request.args.get('id')}", room=request.sid
    )
    emit("is-connected", True, room=request.sid)
    lock.release()


@socketio.on("session-existing")
def check_if_session_exist(session_id: str) -> None:
    """Check if a session is free and if the user can enter it.

    Arguments:
        session_id: the id of the wanted session.
    """
    tab_id = str(request.args.get("tabId"))
    cookie = str(request.args.get("cookie"))
    print("check if following session exists : " + session_id)
    dir_path, dir_names, filenames = next(walk(storage_path))
    found = False
    sessions_folder = f"s_" + session_id
    for dir_name in dir_names:
        if dir_name == sessions_folder:
            found = True
    if session_id == "default" or session_id == "contracts":
        found = False

    if found:
        if session_id in users and cookie != cookies[session_id]:
            found = False
    print(f"users : {users}")
    emit("receive-answer", found, room=users[str(request.args.get("id"))][tab_id])


@socketio.on("disconnect")
def disconnected() -> None:
    """It disconnects the user of the session he was attached to."""
    print("Disconnected")
    print(request.args)
    print(f'ID {request.args.get("id")}')

    session_id = str(request.args.get("id"))
    tab_id = str(request.args.get("tabId"))

    if session_id in users and tab_id in users[session_id]:
        now = time.localtime(time.time())
        emit(
            "send-message",
            f"{strftime('%H:%M:%S', now)} Session {request.args.get('id')} disconnected",
            room=request.sid,
        )
        del users[session_id][tab_id]


@app.route("/")
def index() -> Response:
    return app.send_static_file("index.html")


def send_message_to_user(content: str, room_id: str, crometype: str) -> None:
    """Simplified version to send a notification and a message to a user.

    Arguments:
        content: The content of the message.
        room_id: Where to send the notification and the message.
        crometype: The type of notification to send.
    """
    now = time.localtime(time.time())
    emit("send-notification", {"crometypes": crometype, "content": content}, room=room_id)
    emit("send-message", f"{strftime('%H:%M:%S', now)} - {content}", room=room_id)


@socketio.on("create-design")
def create_design(data: Dict) -> None:
    """Create the design and the mealy according to the strategy indicated

    Arguments:
        data: A dictionary that contains all the information about the synthesis that will be created.
    """
    print(f"create-design received with {data}")
    try:
        json_content = Rating.generate_design(data, request.args.get("id"))
        send_message_to_user(f"The mealy has been created using {data['strategy']} method", request.sid, "success")
        emit("design-created", json_content, room=request.sid)
    except Exception as e:
        emit("design-created", False, room=request.sid)
        emit(
            "send-notification",
            {"content": "The mealy creation has failed. See the console for more information", "crometypes": "error"},
            room=request.sid,
        )
        emit("send-message", f"Mealy \"{data['name']}\" can't be created. Error : {str(e)} ", room=request.sid)


if __name__ == "__main__":
    print("Starting the backend in development mode")
    socketio.run(app, host="0.0.0.0")