# raspi-tools: Raspberry Pi Utility Library

`raspi-tools` is a Python library that simplifies working with GPS modules, GPIO pins, and other Raspberry Pi functionalities. It includes components to manage GPS data, interact with GPIO pins, and more.

---

## Features

1. **GPS Module (`GPSManager`)**

   - Fetch GPS data using `gpsd`.
   - Save GPS data to a database (`TinyDB`).
   - Retrieve the last known GPS location.

2. **GPIO Module (`BoardLED`)**
   - Control Raspberry Pi’s built-in board LED.
   - Flash, turn on, or turn off the LED.

---

## Installation

### 1. Prerequisites

#### Hardware Setup:

- A Raspberry Pi with a GPS module (e.g. Neo6 GPS) connected to the UART port.

#### System Dependencies:

- Install `gpsd` and related tools:
  ```bash
  sudo apt update
  sudo apt install gpsd gpsd-clients python3-gps -y
  ```

#### Configure `gpsd`:

1. Open the `gpsd` configuration file:
   ```bash
   sudo nano /etc/default/gpsd
   ```
2. Update the following fields:
   ```plaintext
   DEVICES="/dev/serial0"
   GPSD_OPTIONS="-n"
   ```
3. Restart `gpsd`:
   ```bash
   sudo systemctl restart gpsd
   ```

#### Verify GPS Functionality:

1. Test with `cgps`:
   ```bash
   cgps -s
   ```
2. Check the `gpsd` service status:
   ```bash
   sudo systemctl status gpsd
   ```

---

### 2. Library Installation

#### Install from PyPI:

```bash
pip install raspi-tools
```

#### Install from Source:

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd raspi-tools
   ```
2. Build and install:
   ```bash
   python3 -m build
   pip install dist/raspi_tools-1.0.0.tar.gz
   ```

---

## Usage

### 1. GPSManager

#### Fetch and Save GPS Data

```python
from raspi_tools import GPSManager

# Initialize GPSManager
gps_manager = GPSManager()

# Fetch and save GPS data
gps_manager.run()
```

#### Retrieve Last Known Location

```python
# Get the last saved GPS data
last_data = gps_manager.get_last_gps_data()

if last_data:
    print(f"Latitude: {last_data.latitude}")
    print(f"Longitude: {last_data.longitude}")
else:
    print("No GPS data available.")
```

---

### 2. BoardLED

#### Control Raspberry Pi Board LED

```python
from raspi_tools import BoardLED

# Initialize the LED manager
led = BoardLED()

# Turn the LED on
led.on()

# Turn the LED off
led.off()

# Flash the LED 5 times
led.flash(times=5, interval=0.2)
```

---

## Advanced Configuration

### GPSManager Initialization

You can specify custom paths or configurations for GPS data storage:

```python
gps_manager = GPSManager(db_path="/custom/path/gps_data.json", gpio_pin=20, timeout=300)
```

### BoardLED Initialization

Customize LED operations for different GPIO pins or external LEDs:

```python
led = BoardLED(pin=21)
led.flash(times=3, interval=1.0)
```

---

## FAQs

### 1. Why is my GPS not providing data?

- Ensure the GPS module is properly connected to the UART port.
- Verify `gpsd` is running:
  ```bash
  sudo systemctl status gpsd
  ```
- Test GPS functionality with:
  ```bash
  cgps -s
  ```

### 2. How do I clear GPS data from the database?

To clear all stored GPS data:

```python
from tinydb import TinyDB
db = TinyDB('/path/to/gps_data.json')
db.truncate()
```

---

## Troubleshooting

1. **GPIO Errors**:

   - If you encounter `GPIO not allocated`, ensure proper cleanup:
     ```python
     import RPi.GPIO as GPIO
     GPIO.cleanup()
     ```

2. **GPS Fix Timeout**:

   - Increase the timeout when fetching GPS data:
     ```python
     gps_manager = GPSManager(timeout=600)
     gps_manager.run()
     ```

3. **Permissions Issues**:
   - Ensure the script is run with appropriate permissions:
     ```bash
     sudo python3 your_script.py
     ```

---

## Contributing

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch and open a pull request.

---

## License

This project is licensed under the MIT License.
