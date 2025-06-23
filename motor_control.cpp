#include <iostream>
#include <chrono>
#include <thread>
#include <string>
#include <csignal>
#include <unistd.h>
#include <mqtt/async_client.h>
#include <pigpio.h>
#include <pthread.h>

class MotorDriver {
public:
    MotorDriver(int ain1, int ain2, int pwm, int stby)
        : AIN1(ain1), AIN2(ain2), PWMA(pwm), STBY(stby) {}

    bool init() {
        if (gpioInitialise() < 0) {
            std::cerr << "Erreur pigpio" << std::endl;
            return false;
        }
        gpioSetMode(AIN1, PI_OUTPUT);
        gpioSetMode(AIN2, PI_OUTPUT);
        gpioSetMode(PWMA, PI_OUTPUT);
        gpioSetMode(STBY, PI_OUTPUT);
        gpioWrite(STBY, 1); // Activer
        return true;
    }

    void forward(int speed_percent) {
        std::cout << "[+] Avance" << std::endl;
        gpioWrite(AIN1, 1);
        gpioWrite(AIN2, 0);
        gpioPWM(PWMA, mapSpeed(speed_percent));
    }

    void backward(int speed_percent) {
        std::cout << "[-] Recule" << std::endl;
        gpioWrite(AIN1, 0);
        gpioWrite(AIN2, 1);
        gpioPWM(PWMA, mapSpeed(speed_percent));
    }

    void stop() {
        std::cout << "[=] Stop" << std::endl;
        gpioPWM(PWMA, 0);
        gpioWrite(AIN1, 0);
        gpioWrite(AIN2, 0);
    }

    void cleanup() {
        gpioTerminate();
    }

private:
    int AIN1, AIN2, PWMA, STBY;

    int mapSpeed(int percent) {
        if (percent < 0) percent = 0;
        if (percent > 100) percent = 100;
        return percent * 255 / 100;
    }
};

// --- MQTT Callback Handler ---
class MotorCallback : public virtual mqtt::callback {
public:
    MotorCallback(MotorDriver& motor, int speed) : motor(motor), speed(speed) {}

    void message_arrived(mqtt::const_message_ptr msg) override {
        std::string payload = msg->to_string();
        std::cout << "[MQTT] Message reçu: " << payload << std::endl;

        if (payload == "FORWARD") {
            motor.forward(speed);
        } else if (payload == "BACKWARD") {
            motor.backward(speed);
        } else if (payload == "STOP") {
            motor.stop();
        }
    }

private:
    MotorDriver& motor;
    int speed;
};

MotorDriver* motor_ptr = nullptr;

void sigHandler(int signum) {
    std::cout << "\n[!] Caught signal " << signum << ", cleaning up and exiting..." << std::endl;
    if (motor_ptr) {
        motor_ptr->stop();
        motor_ptr->cleanup();
    }
    exit(signum);
}

// --- MQTT Thread ---
void* mqtt_thread(void* arg) {
    auto* motor = static_cast<MotorDriver*>(arg);

    const std::string ADDRESS = "tcp://localhost:1883";
    const std::string CLIENT_ID = "motor-controller";
    const std::string TOPIC = "qr/navigation";
    const int SPEED = 60;

    mqtt::async_client client(ADDRESS, CLIENT_ID);
    MotorCallback cb(*motor, SPEED);
    client.set_callback(cb);

    try {
        client.connect()->wait();
        client.subscribe(TOPIC, 1)->wait();
        std::cout << "[MQTT] Abonné à " << TOPIC << std::endl;

        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } catch (const mqtt::exception& e) {
        std::cerr << "[!] Erreur MQTT: " << e.what() << std::endl;
        motor->cleanup();
    }

    return nullptr;
}

int main() {
    MotorDriver motor(17, 27, 18, 22);
    motor_ptr = &motor;

    signal(SIGINT, sigHandler);
    signal(SIGTERM, sigHandler);

    if (!motor.init()) return 1;

    pthread_t mqtt_tid;
    if (pthread_create(&mqtt_tid, nullptr, mqtt_thread, &motor) != 0) {
        std::cerr << "Erreur création thread MQTT" << std::endl;
        return 1;
    }

    std::cout << "[Main] Application en attente de commandes MQTT..." << std::endl;

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    motor.cleanup();
    return 0;
}
