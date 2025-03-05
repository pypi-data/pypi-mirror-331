
import os
import random
import socket
import shutil

class BlackSpammerBD:
    def __init__(self):
        self.connection_code = None
        self.connected = False

    def generate_code(self):
        self.connection_code = str(random.randint(10000000, 99999999))
        return self.connection_code

    def connect(self, code):
        if code == self.connection_code:
            self.connected = True
            return "✅ Connection Successful!"
        return "❌ Invalid Code!"

    def list_files(self):
        if not self.connected:
            return "❌ No connection found!"
        return os.listdir(".")

    def download_file(self, filename):
        if not self.connected:
            return "❌ No connection found!"
        if os.path.exists(filename):
            shutil.copy(filename, f"/tmp/{filename}")
            return f"✅ {filename} downloaded successfully!"
        return "❌ File not found!"

    def upload_file(self, filename):
        if not self.connected:
            return "❌ No connection found!"
        if os.path.exists(filename):
            shutil.copy(filename, "./")
            return f"✅ {filename} uploaded successfully!"
        return "❌ File not found!"

    def share_file(self, filename):
        if not self.connected:
            return "❌ No connection found!"
        return f"✅ Share link: http://fileshare.com/{filename}"

def main():
    bsb = BlackSpammerBD()
    while True:
        cmd = input("BSB> ").strip().split()
        if not cmd:
            continue
        if cmd[0] == "-start":
            print("Connection Code:", bsb.generate_code())
        elif cmd[0] == "-connect" and len(cmd) > 1:
            print(bsb.connect(cmd[1]))
        elif cmd[0] == "-list" and cmd[1] == "all":
            print(bsb.list_files())
        elif cmd[0] == "-download" and len(cmd) > 1:
            print(bsb.download_file(cmd[1]))
        elif cmd[0] == "-upload" and len(cmd) > 1:
            print(bsb.upload_file(cmd[1]))
        elif cmd[0] == "-share" and len(cmd) > 1:
            print(bsb.share_file(cmd[1]))
        elif cmd[0] == "exit":
            break
