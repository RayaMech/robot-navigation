from flask import Flask, render_template_string, request, redirect, url_for
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Global mode variable
mode = "AUTO"

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "qr/navigation"
MQTT_TOPIC_MODE = "qr/mode"

# Setup MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# HTML Page Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Motor Control</title>
</head>
<body>
    <h1>Motor Control - Mode: {{ mode }}</h1>
    
    <form method="POST" action="/mode">
        <button type="submit" name="mode" value="{{ 'MANUAL' if mode == 'AUTO' else 'AUTO' }}">
            Switch to {{ 'Manual' if mode == 'AUTO' else 'Auto' }}
        </button>
    </form>

    {% if mode == 'MANUAL' %}
    <hr>
    <form method="POST" action="/control">
        <button type="submit" name="action" value="FORWARD">Forward</button>
        <button type="submit" name="action" value="BACKWARD">Backward</button>
        <button type="submit" name="action" value="STOP">Stop</button>
    </form>
    {% else %}
    <p>QR Code control is active.</p>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, mode=mode)

@app.route('/mode', methods=['POST'])
def switch_mode():
    global mode
    new_mode = request.form.get("mode")
    if new_mode in ["AUTO", "MANUAL"]:
        mode = new_mode
        print(f"[INFO] Mode changed to {mode}")
        mqtt_client.publish(MQTT_TOPIC_MODE, mode)
    return redirect(url_for('index'))

@app.route('/control', methods=['POST'])
def control():
    global mode
    if mode != "MANUAL":
        print("[WARNING] Ignored command in AUTO mode.")
        return redirect(url_for('index'))

    action = request.form.get("action")
    if action in ["FORWARD", "BACKWARD", "STOP"]:
        print(f"[INFO] Publishing manual command: {action}")
        mqtt_client.publish(MQTT_TOPIC_COMMAND, action)
    return redirect(url_for('index'))

if __name__ == "__main__":
    print("Starting Flask web server...")
    app.run(host="0.0.0.0", port=5000)
