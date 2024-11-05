import serial
import pyvjoy
import time
import threading  # Import threading module
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import pandas as pd  # Import pandas for Excel export

# Set up the serial connection
try:
    ser = serial.Serial('COM6', 9600)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

# Set up vJoy device
j = pyvjoy.VJoyDevice(1)

# Graphing setup
time_data = deque(maxlen=600)
force_data = deque(maxlen=600)

# Data lists for Excel export
time_list = []
force_list = []

fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Brake Force')
ax.set_ylim(0, 2000)  # Assuming max brake force is 2000

initial_time = None  # To store the initial time for normalization

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to update joystick input in a separate thread
def update_joystick():
    global ser, initial_time

    while True:
        if ser is None or not ser.is_open:
            print("Serial port not open. Attempting to reconnect...")
            try:
                ser = serial.Serial('COM6', 9600)  # Reopen the port
            except serial.SerialException as e:
                print(f"Error reopening serial port: {e}")
                time.sleep(1)  # Wait before trying again
                continue

        try:
            # Read data from Arduino
            line_data = ser.readline().decode('utf-8').strip()

            if line_data:
                try:
                    if ':' not in line_data:
                        raise ValueError(f"Malformed data: {line_data}")
                    
                    _, numeric_str = line_data.split(':')
                    brake_force = float(numeric_str)

                    brake_axis_value = map_range(brake_force, 0, 800, 0, 32767)
                    j.set_axis(pyvjoy.HID_USAGE_Z, int(brake_axis_value))

                    current_time = time.time()
                    if initial_time is None:
                        initial_time = current_time

                    normalized_time = current_time - initial_time
                    time_data.append(normalized_time)
                    force_data.append(brake_force)
                    time_list.append(normalized_time)
                    force_list.append(brake_force)

                except ValueError as ve:
                    print(f"Data error: {ve}")

        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            if ser:
                ser.close()
                ser = None

# Start joystick control in a separate thread
joystick_thread = threading.Thread(target=update_joystick)
joystick_thread.daemon = True
joystick_thread.start()

# Graph update function
def update_graph(frame):
    line.set_data(time_data, force_data)

    if len(time_data) > 0:
        latest_time = time_data[-1]
        if latest_time < 10:
            ax.set_xlim(0, 10)
        else:
            ax.set_xlim(latest_time - 10, latest_time)
    
    return [line]

# Create animation for live graphing
ani = animation.FuncAnimation(fig, update_graph, interval=100)

plt.show()

# Save data to Excel when the program ends
data = {'Time (s)': time_list, 'Brake Force': force_list}
df = pd.DataFrame(data)
df.to_excel(r'C:\Users\FSAE09\Desktop\Brake Pressure 3301R project\brake_pressure_data_kai_jun_800.xlsx', index=False)

print("Data saved to brake_pressure_data.xlsx")

# Close the serial connection on exit
if ser and ser.is_open:
    ser.close()
