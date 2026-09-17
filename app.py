from flask import Flask, render_template, request, jsonify
import paramiko
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/execute", methods=["POST"])
def execute_command():
    data = request.json or {}
    ip = data.get("ip")
    command = data.get("command")
    username = "admin"
    password = "cisco"

    if not ip or not command:
        return jsonify({"error": "Both IP Address and Command are required."}), 400

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
            disabled_algorithms=dict(pubkeys=[], kex=[], ciphers=[])
        )

        shell = client.invoke_shell()
        time.sleep(1)

        shell.send("terminal length 0\n")
        time.sleep(0.5)
        shell.recv(1000)

        shell.send(f"{command}\n")
        time.sleep(1.5)

        output = shell.recv(65535).decode("utf-8", errors="ignore")
        client.close()

        return jsonify({"output": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
