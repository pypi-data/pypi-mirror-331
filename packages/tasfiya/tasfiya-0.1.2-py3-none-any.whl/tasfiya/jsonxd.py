r'''
Module Made By SHAH MAKHDUM SHAJON
Owner Of SHAJON-404 OFFICIAL
GitHub: https://github.com/SHAJON-404
Telegram: https://t.me/SHAJON404_OFFICIAL
Facebook: https://www.facebook.com/mdshahmakhdum.shajon
'''

import os
import random

# FBAN/FB4A;FBAV/268.1.0.54.121;FBBV/211681919;FBDM/{density=2.0,width=720,height=1402};FBLC/en_US;FBRV/213106641;FBCR/cricket;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-A102U;FBSV/9;FBOP/19;FBCA/armeabi-v7a:armeabi;

def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), 'txt', filename)

def fbav():
    file_path = get_file_path("fbav.txt")
    with open(file_path, "r") as file:
        xd = file.read().splitlines()
        return random.choice(xd)

def fbdm():
    file_path = get_file_path("fbdm.txt")
    with open(file_path, "r") as file:
        xd = file.read().splitlines()
        return random.choice(xd)

def fbcr():
    file_path = get_file_path("fbcr.txt")
    with open(file_path, "r") as file:
        xd = file.read().splitlines()
        return random.choice(xd)

def fblc():
    locales = [
        "en_US", "en_GB", "en_CA", "en_AU", "en_NZ",
        "en_IE", "en_ZA", "en_IN", "en_PH", "en_SG",
        "en_MY", "en_HK", "en_BZ", "en_JM", "en_TT",
        "en_BW", "en_AG", "en_NA", "en_ZW", "en_PK"
    ]
    return random.choice(locales)