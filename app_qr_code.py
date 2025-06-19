import cv2
import subprocess
import time
import paho.mqtt.client as mqtt
import os
import socket
import fcntl
import struct


# --- Disable GUI ---
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# --- Configuration ---
MQTT_BROKER = "localhost"  # Or IP of your MQTT broker
MQTT_PORT = 1883
MQTT_TOPIC = "qr/navigation"
MODE_TOPIC = "qr/mode"
mode = "AUTO"  # Default mode: AUTO or MANUAL

# --- MQTT Callback ---
def on_message(client, userdata, msg):
    global mode
    if msg.topic == MODE_TOPIC:
        mode = msg.payload.decode().strip().upper()
        print(f"[MODE] Updated to {mode}")

# --- MQTT Setup ---
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()
mqtt_client.subscribe(MODE_TOPIC)

# --- Get IP Adress ---
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24]
    )

ip = get_ip_address('wlan0')
if ip:
    stream_url = f"tcp://{ip}:8554"
    print("Stream URL:", stream_url)
else:
    print("Could not get IP address for wlan0")


# --- Start libcamera-vid process ---
libcamera_command = [
    "libcamera-vid", "-t", "0", "--inline", "--listen",
    "-o", "tcp://0.0.0.0:8554", "--width", "640", "--height", "480", "--framerate", "15"
]

libcamera_process = subprocess.Popen(libcamera_command)
print("libcamera-vid launched. Waiting for initialization...")
time.sleep(2)

# --- OpenCV Stream Setup ---
stream_url = f"tcp://{ip}:8554"  # Replace with your Pi IP
cap = cv2.VideoCapture(stream_url)
detector = cv2.QRCodeDetector()

# --- Main Loop ---
while True:
    ret, img = cap.read()
    if not ret or img is None:
        print("Failed to capture frame.")
        continue

    data, bbox, _ = detector.detectAndDecode(img)

    if bbox is not None and len(bbox) > 0:
        bbox = bbox.astype(int)
        for i in range(len(bbox[0])):
            pt1 = tuple(bbox[0][i])
            pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])
            cv2.line(img, pt1, pt2, color=(255, 0, 0), thickness=2)

        if data:
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 250, 120), 2)
            print("QR Code detected:", data)

            if mode == "AUTO":
                mqtt_client.publish(MQTT_TOPIC, data)
                print(f"[MQTT] Sent '{data}' to {MQTT_TOPIC}")
            else:
                print(f"[SKIPPED] Not sending '{data}' (Manual mode)")
	
	
    #cv2.imshow("QR Code Detector", img)
    #if cv2.waitKey(1) == ord("q"):
    #    break
    

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
mqtt_client.loop_stop()
mqtt_client.disconnect()
libcamera_process.terminate()
