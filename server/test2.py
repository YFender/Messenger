import time
import subprocess
import datetime

from pyngrok import ngrok
tunnel = ngrok.connect(8080)
ngrok.install_ngrok()

def restart():
    pass

restart()