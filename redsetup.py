import os
import requests
import json
from subprocess import call

class RedSetup():
    def __init__(self):
        self.login_type = None
        self.email = None
        self.password = None
        self.prefixes = None
        self.owner = None
        self.default_mod = None
        self.default_admin = None

    def make_settings(self):
        '''Borrowed and adapted from red.py'''
        print("Red - First run configuration\n")
        print("If you haven't already, create a new account:\n"
              "https://twentysix26.github.io/Red-Docs/red_guide_bot_accounts/"
              "#creating-a-new-bot-account")
        print("and obtain your bot's token like described.")
        print("\nInsert your bot's token:")

        choice = input("> ")

        if "@" not in choice and len(choice) >= 50:  # Assuming token
            self.login_type = "token"
            self.email = choice
            self.password = ""
        elif "@" in choice:
            self.login_type = "email"
            self.email = choice
            self.password = input("\nPassword> ")
        else:
            os.remove('data/red/settings.json')
            input("Invalid input. Restart Red and repeat the configuration "
                  "process.")
            exit(1)

        print("\nChoose a prefix. A prefix is what you type before a command.\n"
              "A typical prefix would be the exclamation mark.\n"
              "Can be multiple characters. You will be able to change it "
              "later and add more of them.\nChoose your prefix:")
        confirmation = False
        while confirmation is False:
            new_prefix = self.ensure_reply("\nPrefix> ").strip()
            print("\nAre you sure you want {0} as your prefix?\nYou "
                  "will be able to issue commands like this: {0}help"
                  "\nType yes to confirm or no to change it".format(new_prefix))
            confirmation = self.get_answer()

        self.prefixes = [new_prefix]
        if self.login_type == "email":
            print("\nOnce you're done with the configuration, you will have to type "
                  "'{}set owner' *in Discord's chat*\nto set yourself as owner.\n"
                  "Press enter to continue".format(new_prefix))
            self.owner = input("") # Shh, they will never know it's here
            if self.owner == "":
                self.owner = "id_here"
            if not self.owner.isdigit() or len(self.owner) < 17:
                if self.owner != "id_here":
                    print("\nERROR: What you entered is not a valid ID. Set "
                          "yourself as owner later with {}set owner".format(new_prefix))
                self.owner = "id_here"
        else:
            self.owner = "id_here"

        print("\nInput the admin role's name. Anyone with this role in Discord will be "
              "able to use the bot's admin commands")
        print("Leave blank for default name (Transistor)")
        self.default_admin = input("\nAdmin role> ")
        if self.default_admin == "":
            self.default_admin = "Transistor"

        print("\nInput the moderator role's name. Anyone with this role in Discord will "
              "be able to use the bot's mod commands")
        print("Leave blank for default name (Process)")
        self.default_mod = input("\nModerator role> ")
        if self.default_mod == "":
            self.default_mod = "Process"

        print("\nSaving the settings.")


        print("\nThe configuration is done. Continuing with installation.\nPress enter to continue")
        input("\n")

    def check_folders(self):
        folders = ("data", "data/red", "cogs", "cogs/utils")
        for folder in folders:
            if not os.path.exists(folder):
                print("Creating " + folder + " folder...")
                os.makedirs(folder)

    def save_settings(self):
        settings = {
            "EMAIL": self.email,
            "LOGIN_TYPE": self.login_type,
            "OWNER": self.owner,
            "PASSWORD": self.password,
            "PREFIXES": self.prefixes,
            "default": {
                "ADMIN_ROLE": self.default_admin,
                "MOD_ROLE": self.default_mod
            }
        }
        with open("data/red/settings.json", "w") as fout:
            s = json.dumps(settings, indent=4)
            fout.write(s)

    def create_service_file(self):
        svc_type = None
        fname = None
        dpath = None
        if os.path.isfile("/bin/systemctl"):
            svc_type = "systemd"
        elif os.path.isfile("/usr/sbin/service"):
            svc_type = "upstart"
        else:
            print("No supported service utilities!")

        if svc_type == "systemd":
            fname = "red.service"
            dpath = "/etc/systemd/system/"
            text = "[Unit]\nDescription=Red-DiscordBot\nAfter=multi-user.target\n\n[Service]\nWorkingDirectory=/home/{}/Red-DiscordBot\nUser={}\nGroup={}\nExecStart=/usr/bin/python3.5 /home/{}/Red-DiscordBot/red.py --no-prompt\nType=idle\nRestart=always\nRestartSec=15\n\n[Install]\nWantedBy=multi-user.target".format(os.environ["USER"], os.environ["USER"], os.environ["USER"], os.environ["USER"])
            with open("red.service", "w") as fout:
                fout.write(text)
        elif svc_type == "upstart":
            dpath = "/etc/init/"
            fname = "red.conf"
            text = "start on runlevel [2345]\nstop on runlevel [016]\n\nrespawn\nchdir /home/{}/Red-DiscordBot\nsetuid {}\nsetgid {}\nexec python3.5 red.py --no-prompt".format(os.environ["USER"], os.environ["USER"], os.environ["USER"])
            with open("red.conf", "w") as fout:
                fout.write(text)
        call(["sudo", "mv", fname, os.path.join(dpath, fname)])

    def ensure_reply(self, msg):
        choice = ""
        while choice == "":
            choice = input(msg)
        return choice

    def get_answer(self):
        choices = ("yes", "y", "no", "n")
        c = ""
        while c not in choices:
            c = input(">").lower()
        if c.startswith("y"):
            return True
        else:
            return False

def main():
    rs = RedSetup()
    rs.check_folders()
    rs.make_settings()
    rs.save_settings()
    rs.create_service_file()

if __name__ == "__main__":
    main()
