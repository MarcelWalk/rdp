from cProfile import label
import subprocess
import pytermgui as ptg
import base64
import configparser
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

config = configparser.ConfigParser()
config.read('hosts.conf')
my_key = "DdMXMD7NHPsSrrqN"

def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding

def remote(self):
    ip = "" 
    user = "" 
    password = ""
    key = ""

    for host in config.sections():
        
        
        if config[host]["IP"] == self.label:
            ip = config[host]["IP"]
            user = config[host]["User"]
            password = config[host]["Password"]
            key = my_key

    p = subprocess.run("xfreerdp -u {1} -p '{2}' -v {0}".format(
        ip,
        user,
        decrypt(key.encode('utf-8'),password.replace("!encrypted#","")).decode('utf-8')),
        shell=True,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)

def check_encryption(pwd:str):
    for host in config.sections():
        if not config[host]["Password"].startswith("!encrypted#"):
            config[host]["Password"] = "{}{}".format("!encrypted#", encrypt(pwd.encode('utf-8'), config[host]["Password"].encode('utf-8')))
    with open('hosts.conf', 'w') as configfile:
        config.write(configfile)

def main():
    check_encryption(pwd=my_key)

    with ptg.WindowManager() as manager:

        window = (
            ptg.Window(
                width=60,
                box="DOUBLE",
            )
            .set_title("RDP")
            .center()
        )

        for host in config.sections():
            btn = ptg.Button(label=config[host]['IP'], onclick=remote)
            window._add_widget(btn)

        manager.add(window)

main()