from http import server
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import os
from dotenv import load_dotenv
import time
from mcrcon import MCRcon

load_dotenv()

hostName = "192.168.2.10"
serverPort = 25501

server = None


def rcon(cmd):
    ip = os.getenv("MC_rcon_ip")
    secret = os.getenv("MC_rcon_secret")
    try:
        with MCRcon(ip, secret) as mcr:
            answ = mcr.command(cmd)
    except:
        return None
    return answ


def send200(self, message):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes(f"{message}\n", "utf-8"))


def server_start():
    global server
    minecraft_dir = os.getenv("MC_Server_dir")
    server_jar = os.getenv("MC_Server_jar_file")
    minRam = os.getenv("MC_alloc_mem_min")
    maxRam = os.getenv("MC_alloc_mem_max")
    java_parameters = "-XX:+UseG1GC -Dsun.rmi.dgc.server.gcInterval=2147483646 -XX:+UnlockExperimentalVMOptions -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M -Dfml.readTimeout=180"

    executable = f"~/minecraft-server/jdk8u312-b07/bin/java -server {java_parameters} -Xms{minRam} -Xmx{maxRam} -jar {server_jar} nogui"
    if server is not None:
        return 1  # "Server is already started"
    print(
        f"starting minecraft server - dir: {minecraft_dir} | executable: {executable}"
    )
    server = subprocess.Popen(
        executable, stdin=subprocess.PIPE, cwd=minecraft_dir, shell=True
    )
    return 0  # "Starting server"


def server_command(command):
    if server is None:
        return
    server.stdin.write((command + "\n").encode())
    server.stdin.flush()


def server_stop():
    global server
    if server is None:
        return 1
    server_command("stop")
    server.kill()
    server = None
    return 0


def start(self):
    code = server_start()
    if code == 0:
        send200(self, "ok")
    else:
        send200(self, "error")


def stop(self):
    code = server_stop()
    if code == 0:
        send200(self, "ok")
    else:
        send200(self, "error")


def list(self):
    answ = rcon("/list")
    if answ is None:
        send200(self, "error")
    else:
        send200(self, answ)


def state(self):
    global server
    if server is None:
        send200(self, "off")
    else:
        answ = rcon("/list")
        if answ is None:
            send200(self, "starting")
        else:
            send200(self, "on")


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path.find("start") == 1:
            return start(self)
        if self.path.find("stop") == 1:
            return stop(self)
        if self.path.find("list") == 1:
            return list(self)
        if self.path.find("state") == 1:
            return state(self)
        return self.send_response(404)


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped")
