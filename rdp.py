import subprocess
import pytermgui as ptg

def remote(self):
    p = subprocess.run("xfreerdp -u User -p '1234' -v 192.168.122.101",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

CONFIG = """
config:
    Label:
        styles:
            value: dim bold

    Window:
        styles:
            border: '60'
            corner: '60'

    Container:
        styles:
            border: '96'
            corner: '96'
"""

with ptg.YamlLoader() as loader:
    loader.load(CONFIG)

with ptg.WindowManager() as manager:

    btn = ptg.Button(label="192.168.122.101", onclick=remote)

    window = (
        ptg.Window(
            "",
            btn,
            width=60,
            box="DOUBLE",
        )
        .set_title("RDP")
        .center()
    )

    manager.add(window)