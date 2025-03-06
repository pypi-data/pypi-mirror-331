import os
import time
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from tqdm import tqdm
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

# Make RPi GPIO optional
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("RPi.GPIO not available. GPIO functionality will be disabled.")

class GPSData:
    def __init__(self, data):
        self.id = data.get('id')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.altitude = data.get('altitude')
        self.date_created = data.get('date_created')
        
    def __str__(self):
        return f"GPSData(id={self.id}, lat={self.latitude}, lon={self.longitude}, alt={self.altitude})"
       
        
class GPSManager:
    def __init__(self, db_path=None, gpio_pin=20, timeout=300):
        """Initialize GPS Manager."""
        
        if db_path is None:
            home_dir = os.path.expanduser("~/.gps")
            os.makedirs(home_dir, exist_ok=True)  # Create the directory if it doesn't exist
            db_path = os.path.join(home_dir, "gps_data.db")
            
        # Initialize GPIO if available
        self.gpio_pin = gpio_pin
        self.new_data = None
        self.gpio_enabled = RPI_AVAILABLE
        
        # Initialize SQLite database
        self.db_path = db_path
        self._init_database()
        
        self.timeout = timeout
        
    def _init_database(self):
        """Initialize the SQLite database with the required schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create GPS data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            time TEXT,
            date_created TEXT
        )
        ''')
        
        # Create metadata table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        # Initialize metadata if it doesn't exist
        cursor.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', 
                     ('last_record_id', '0'))
        
        conn.commit()
        conn.close()
            
    def _setup_gpio(self):
        """Initialize GPIO pin."""
        if not self.gpio_enabled:
            print("GPIO functionality is disabled.")
            return
            
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.cleanup(self.gpio_pin) 
        except Exception:
            pass
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        # print(f"GPIO {self.gpio_pin} initialized successfully.")
        
    def _setup_gpio_with_retry(self, retries=3, delay=1):
        """Retry GPIO setup up to 'retries' times with a delay between attempts."""
        if not self.gpio_enabled:
            return
            
        for attempt in range(1, retries + 1):
            try:
                # print(f"Attempt {attempt}/{retries}: Initializing GPIO {self.gpio_pin}")
                self._setup_gpio()
                return  # Exit the method if successful
            except Exception as e:
                # print(f"Error during GPIO initialization on attempt {attempt}: {e}")
                if self.gpio_enabled:
                    GPIO.cleanup(self.gpio_pin)
                if attempt < retries:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        raise RuntimeError(f"Failed to initialize GPIO {self.gpio_pin} after {retries} attempts")

    def set_gpio_low(self):
        """Set GPIO pin to LOW."""
        if not self.gpio_enabled:
            print("Simulating GPIO LOW (GPS would start now)")
            return
            
        GPIO.output(self.gpio_pin, GPIO.LOW)
        print("Starting GPS")

    def reset_gpio(self):
        """Reset GPIO pin (set it to HIGH)."""
        if not self.gpio_enabled:
            print("Simulating GPIO HIGH (GPS would stop now)")
            return
            
        GPIO.output(self.gpio_pin, GPIO.HIGH)
        print("GPS Stopped")

    def start_gpsd(self):
        """Start the gpsd service."""
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'gpsd'], check=True)
            print("gpsd service started.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start gpsd: {e}")
        except FileNotFoundError:
            print("systemctl not found. Running in simulation mode or non-Linux system.")

    def stop_gpsd(self):
        """Stop the gpsd service."""
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'gpsd'], check=True)
            print("gpsd service stopped.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop gpsd: {e}")
        except FileNotFoundError:
            print("systemctl not found. Running in simulation mode or non-Linux system.")

    def get_gps_data(self, progress_callback=None):
        """Fetch GPS data using gpsd with a progress bar."""
        try:
            session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
            print("Waiting for GPS fix...")

            with tqdm(total=self.timeout, desc="Time elapsed", unit="s") as pbar:
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    elapsed = int(time.time() - start_time)
                    pbar.n = elapsed
                    pbar.last_print_n = elapsed  # Sync progress bar display
                    pbar.refresh()
                    if progress_callback:
                        progress_callback({
                                "current_progress": pbar.n,
                                "total": pbar.total,
                                "elapsed_time_seconds": round(pbar.elapsed, 2),
                                "description": pbar.desc,
                                "unit": pbar.unit,
                                "start_time": pbar.start_t,
                                "last_print_time": pbar.last_print_t,
                                "last_print_progress": pbar.last_print_n,
                                "rate_units_per_second": round(pbar.format_dict["rate"], 2) if "rate" in pbar.format_dict else None,
                                "postfix": pbar.postfix,
                                "disable": pbar.disable,
                                "percentage_complete": round((pbar.n / pbar.total) * 100, 2) if pbar.total else None
                        })

                    try:
                        report = session.next()

                        # Display the current status on the same line
                        if report['class'] == 'SKY':
                            nSat = getattr(report, 'nSat', 0)
                            uSat = getattr(report, 'uSat', 0)
                            pbar.set_postfix_str(f"Satellites: {uSat}/{nSat} used")

                        if report['class'] == 'TPV' and getattr(report, 'mode', 0) >= 2:
                            # Successfully acquired fix
                            data = {
                                'latitude': getattr(report, 'lat', 'n/a'),
                                'longitude': getattr(report, 'lon', 'n/a'),
                                'altitude': getattr(report, 'alt', 'n/a'),
                                'time': getattr(report, 'time', 'n/a'),
                            }
                            pbar.set_postfix_str("GPS Fix Acquired!")
                            pbar.close()
                            print("\nGPS Data:", data)
                            return data

                    except KeyError:
                        pbar.set_postfix_str("Waiting for valid data...")
                    except StopIteration:
                        pbar.set_postfix_str("GPSD has terminated.")
                        break
                    except Exception as e:
                        pbar.set_postfix_str(f"Error: {e}")

                    time.sleep(1)

            pbar.close()
            print("\nTimeout reached: Unable to get GPS fix.")
            return None
        except NameError:
            print("GPS module not available. Simulating GPS data...")
            # Return simulated data for testing purposes
            import random
            return {
                'latitude': random.uniform(-90, 90),
                'longitude': random.uniform(-180, 180),
                'altitude': random.uniform(0, 1000),
                'time': datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }

    def save_gps_data(self, data) -> GPSData:
        """Save GPS data to SQLite with auto-increment ID and date_created."""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add date_created field
            data['date_created'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            # Insert data into gps_data table
            cursor.execute('''
            INSERT INTO gps_data (latitude, longitude, altitude, time, date_created)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('latitude'),
                data.get('longitude'),
                data.get('altitude'),
                data.get('time'),
                data.get('date_created')
            ))
            
            # Get the ID of the inserted row
            data['id'] = cursor.lastrowid
            
            # Update metadata table with the last record ID
            cursor.execute('UPDATE metadata SET value = ? WHERE key = ?',
                          (str(data['id']), 'last_record_id'))
            
            # Commit changes
            conn.commit()
            conn.close()

            print(f"GPS data saved with id: {data['id']} {data['latitude']}")
            return GPSData(data)
        except Exception as e:
            print(f"Error saving GPS data: {e}")
            return None
            
    def get_last_known_location(self):
        return self.get_last_gps_data()
        
    def get_last_gps_data(self):
        """Retrieve the last entered GPS data using the metadata last_record_id."""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the last record ID from metadata
            cursor.execute('SELECT value FROM metadata WHERE key = ?', ('last_record_id',))
            result = cursor.fetchone()
            
            if not result or result[0] == '0':
                print("No GPS data found.")
                conn.close()
                return None
                
            last_record_id = int(result[0])
            
            # Get the record with the ID
            cursor.execute('''
            SELECT id, latitude, longitude, altitude, time, date_created 
            FROM gps_data WHERE id = ?
            ''', (last_record_id,))
            
            record = cursor.fetchone()
            conn.close()
            
            if not record:
                print(f"No GPS data found with id {last_record_id}")
                return None
                
            # Convert record to dictionary
            data = {
                'id': record[0],
                'latitude': record[1],
                'longitude': record[2],
                'altitude': record[3],
                'time': record[4],
                'date_created': record[5]
            }
            
            return GPSData(data)
        except Exception as e:
            print(f"Error retrieving GPS data: {e}")
            return None
    
    def get_all_gps_data(self, limit=100):
        """Retrieve all GPS data entries, with optional limit."""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Get records with limit
            cursor.execute('''
            SELECT id, latitude, longitude, altitude, time, date_created 
            FROM gps_data ORDER BY id DESC LIMIT ?
            ''', (limit,))
            
            records = cursor.fetchall()
            conn.close()
            
            # Convert records to GPSData objects
            result = []
            for record in records:
                data = dict(record)
                result.append(GPSData(data))
                
            return result
        except Exception as e:
            print(f"Error retrieving GPS data: {e}")
            return []

    def run(self, progress_callback=None):
        """Main method to manage GPS process."""
        try:
            self._setup_gpio_with_retry()
            self.set_gpio_low()
            self.start_gpsd()
            self.new_data = self.get_gps_data(progress_callback)

            if self.new_data:
                return self.save_gps_data(self.new_data)
            else:
                print("No GPS data retrieved.")
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.stop_gpsd()
            self.reset_gpio()
            if self.gpio_enabled:
                try:
                    GPIO.cleanup(self.gpio_pin) 
                except Exception:
                    pass

