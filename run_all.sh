#!/bin/bash

# Lancer le serveur pigpiod (nécessaire pour le C++)
sudo pkill pigpiod
#sleep1

# Activate virutal environment
source env/bin/activate

# Lancer le contrôleur moteur en arrière-plan
sudo ./motor_control &

# Lancer le serveur web
python3 web_server.py &

# Lancer le script Python (QR Code Reader)
python3 app_qr_code.py 


