from flask import Flask, render_template, redirect, session, url_for, request, jsonify
import paho.mqtt.client as mqtt
import yaml
import sys
import os, time


app = Flask(__name__)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa832323'
zuordnung = dict()
zuordnungtime = 0

@app.context_processor
def inject_title():
    return dict(title="ESP Verwaltung")


@app.route("/", methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        if request.form['password'] == 'admin':
            session['login'] = True
            return render_template("list.html", result=getzuordnung()["list"])
        else:
            error = "Wrong Password"
            return render_template("login.html", error=error)
    else:
        if 'login' in session:
            return render_template("list.html", result=getzuordnung()["list"])
        else:
            return render_template("login.html", error=error)


@app.route('/_add')
def add():
    id = request.args.get('id', 0, type=str)
    room = request.args.get('room', 0, type=str)
    if is_hex(id) and room.isalnum() and 1 <= len(room) <= 100:
        addzuordnung(id, room)
        return {"id": id, "room": room}
    else:
        return {"error": True}


@app.route('/_del')
def delete():
    id = request.args.get('id', 0, type=str)
    if is_hex(id):
        delzuordnung(id)
        return {"done": True}
    else:
        return {"error": True}


def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def addzuordnung(id, room):
    with open("zuordnung.yaml", 'r+') as stream:
        try:
            cur_yaml = yaml.safe_load(stream)
            cur_yaml['list'].update({id: room})
            stream.seek(0)
            yaml.safe_dump(cur_yaml, stream)
        except yaml.YAMLError as exc:
            print(exc)


def delzuordnung(id):
    with open("zuordnung.yaml", 'r+') as stream:
        try:
            cur_yaml = yaml.safe_load(stream)
            cur_yaml['list'].pop(id, None)
            stream.truncate(0)
            stream.seek(0)
            yaml.dump(cur_yaml, stream)
            return True
        except yaml.YAMLError as exc:
            print(exc)
            return False

def getzuordnung():
    with open("zuordnung.yaml") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    topic = str(msg.topic).split('/')
    if topic[1] in getZuordnung()['list'] and len(topic) == 3 and str(msg.payload) != "0":
        client.publish(f"classroom/{getZuordnung()['list'][topic[1]]}/{topic[2]}", msg.payload)


def bridge():
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['host'], config['port'], 60)
    client.loop_forever()


def getZuordnung():
    moddate = os.stat("zuordnung.yaml")[8]
    if moddate != zuordnungtime:
        with open("zuordnung.yaml", 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    return zuordnung


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("raw/#")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "-w":
        app.run(host='0.0.0.0')
    elif len(sys.argv) == 2 and sys.argv[1] == "-b":
        bridge()
    else:
        print('''ESP Verwaltung
        Argumente
        -w Webserver
        -b Bridge
        ''')
