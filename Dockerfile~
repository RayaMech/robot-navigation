# Use Raspberry Pi OS (Raspbian) base image
FROM balenalib/raspberrypi4-64-debian:bullseye

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libpigpio-dev \
    libssl-dev \
    libatlas-base-dev \
    libopencv-dev \
    libwebp6 \
    libwebp-dev \
    libcamera-apps \
    libcamera-dev \
    python3 \
    python3-opencv \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    pigpio \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build and install Eclipse Paho MQTT C
RUN git clone https://github.com/eclipse/paho.mqtt.c.git && \
    cd paho.mqtt.c && \
    cmake -Bbuild -H. -DPAHO_WITH_SSL=TRUE && \
    cmake --build build/ --target install && \
    ldconfig && \
    cd .. && rm -rf paho.mqtt.c

# Build and install Eclipse Paho MQTT C++
RUN git clone https://github.com/eclipse/paho.mqtt.cpp.git && \
    cd paho.mqtt.cpp && \
    cmake -Bbuild -H. && \
    cmake --build build/ --target install && \
    ldconfig && \
    cd .. && rm -rf paho.mqtt.cpp

# Install Poetry (latest stable)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (Poetry installs into /root/.local/bin by default)
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /home/app

# Install Poetry (latest stable)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (Poetry installs into /root/.local/bin by default)
ENV PATH="/root/.local/bin:$PATH"

# Copy application files
COPY . .

# Compile C++ motor control app
RUN g++ motor_control.cpp -std=c++17 -o motor_control \
    -lpigpio -lrt -lpaho-mqttpp3 -lpaho-mqtt3as

# Set up Python virtual environment and install requirements
RUN pip3 install --upgrade pip && \
    pip3 install opencv-python paho-mqtt RPi.GPIO && \
    pip3 install -r requirements.txt

# Make the shell script executable
RUN chmod +x run_all.sh

# Expose necessary ports: MQTT + camera stream
EXPOSE 1883 8554 5000

# Default command to run the whole system
CMD ["bash", "-c", "./run_all.sh"]
