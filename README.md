# Robot Navigation with QR Code Detection and MQTT Control

## Description

Ce projet est une application complète pour un robot basé sur Raspberry Pi qui utilise :

- La détection de QR codes via caméra (libcamera + OpenCV)
- La communication MQTT pour la navigation et le contrôle moteur
- Un serveur web Flask pour gérer le mode manuel/auto et envoyer des commandes manuelles
- Un contrôle moteur en C++ utilisant pigpio et MQTT
- Un environnement Docker pour faciliter le déploiement

---

## Fonctionnalités

- Lecture continue de flux vidéo caméra via `libcamera-vid` et détection des QR codes en temps réel.
- Envoi automatique des données détectées sur un broker MQTT en mode automatique.
- Serveur web pour basculer entre modes AUTO et MANUEL.
- En mode MANUEL, contrôle moteur via interface web.
- Pipeline Dockerisée pour faciliter la compilation, déploiement et mise à jour.

---

## Structure du projet

- `motor_control.cpp` : Contrôle moteur en C++ utilisant pigpio et MQTT.
- `app_qr_code.py` : Script Python pour la détection des QR codes et publication MQTT.
- `web_server.py` : Serveur Flask pour interface web et contrôle manuel.
- `run_all.sh` : Script bash pour lancer tous les composants.
- `Dockerfile` : Image Docker basée sur Raspberry Pi OS avec toutes les dépendances.
- `requirements.txt` : Dépendances Python (Flask, OpenCV, paho-mqtt, etc.).

---

## Prérequis

- Raspberry Pi 4 (64-bit)
- Docker et Docker Compose installés
- MQTT broker (ex: Mosquitto) accessible localement ou sur le réseau
- Accès réseau au Raspberry Pi (pour interface web et streaming caméra)

---

## Installation et déploiement

1. **Cloner le dépôt**

```bash
git clone https://github.com/RayaMech/robot-navigation.git
cd robot-navigation
Construire l’image Docker

bash
Copy code
docker build -t robot-navigation:latest .
Lancer le système

bash
Copy code
docker run --privileged -p 5000:5000 -p 8554:8554 -p 1883:1883 robot-navigation:latest
Accéder à l’interface web

Ouvrir dans un navigateur :

cpp
Copy code
http://<IP_RASPBERRY_PI>:5000
Mode automatique / manuel

En mode automatique : le robot suit les QR codes détectés.

En mode manuel : contrôle moteur via l’interface web.

Utilisation
Pour arrêter le programme, appuyer sur q dans la fenêtre OpenCV ou arrêter le conteneur Docker.

Le mode peut être basculé via l’interface web.

Contribution
N’hésitez pas à proposer des améliorations, ouvrir des issues ou pull requests.

Licence
Ce projet est sous licence MIT.

Contact
Rayane Mechik - rayane.mechik.etu@univ-lille.fr
