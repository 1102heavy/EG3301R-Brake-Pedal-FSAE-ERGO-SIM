import serial
import pyvjoy
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import pandas as pd  # Import pandas for Excel export

#Extract Data from AC

#Create Machine Learning Model to predict lock up

# Set up the serial connection (adjust the COM port)
try:
    ser = serial.Serial('COM6', 9600)  # Ensure the port is open # Just Have no timeout at all. Solve problem f malfunction data.
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

# Set up vJoy device
j = pyvjoy.VJoyDevice(1)  # Create virtual joystick object for vJoy Device 1

# Graphing setup
time_data = deque(maxlen=600)  # Reduced size for faster updates
force_data = deque(maxlen=600)  # Reduced size for faster updates

# Create lists to store data for Excel export
time_list = []
force_list = []

fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')  # Make sure the line is a tuple by adding a comma
ax.set_xlabel('Time (s)')
ax.set_ylabel('Brake Force')

# Set y-axis limits to avoid rescaling
ax.set_ylim(0, 2000)  # Assuming max brake force is 2000

initial_time = None  # To store the initial time for normalization

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Update function for the animation
def update(frame):
    global ser, initial_time

    # Check if the serial connection is still open
    if ser is None or not ser.is_open:
        print("Serial port not open. Attempting to reconnect...")
        try:
            ser = serial.Serial('COM6', 9600)  # Reopen the port
        except serial.SerialException as e:
            print(f"Error reopening serial port: {e}")
            return [line]  # Return line object even if there's an error

    try:
        # Read the data from Arduino
        line_data = ser.readline().decode('utf-8').strip()

        if line_data:
            try:
                # Expecting format: "Pressure:<numeric_value>"
                # Validate the data format first
                if ':' not in line_data:
                    raise ValueError(f"Malformed data: {line_data}")

                pressure_str, numeric_str = line_data.split(':')
                
                # Try to convert the numeric part into a float
                brake_force = float(numeric_str) 

                # Map the brake force (0 - max force) to joystick axis (0 - 32767)
                brake_axis_value = map_range(brake_force, 0, 800, 0, 32767)

                # Set the vJoy Axis for the brake (e.g., Axis Z)
                j.set_axis(pyvjoy.HID_USAGE_Z, int(brake_axis_value))

                # Get the current time
                current_time = time.time()

                # Initialize the initial time for normalization
                if initial_time is None:
                    initial_time = current_time  # Set initial time on the first data point

                # Normalize the time to start from 0
                normalized_time = current_time - initial_time

                # Append normalized time and force data to the deques
                time_data.append(normalized_time)
                force_data.append(brake_force)

                # Store the data in lists for Excel export
                time_list.append(normalized_time)
                force_list.append(brake_force)

                # Update the line data
                line.set_data(time_data, force_data)

                # Adjust x-axis limits
                if normalized_time < 10:
                    ax.set_xlim(0, 10)  # Fixed limit for the first 10 seconds
                else:
                    ax.set_xlim(normalized_time - 10, normalized_time)  # Dynamic scrolling window

            except ValueError as ve:
                print(f"Data error: {ve}")  # Handle bad data or conversion errors

    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        if ser:
            ser.close()  # Close the port and reset the variable
            ser = None

    return [line]  # Return the line object in a list (sequence of Artist objects)

# Create an animation
ani = animation.FuncAnimation(fig, update, interval=0)  # Faster updates, but not 0 for stability

plt.show()

# Close serial connection on exit
if ser and ser.is_open:
    ser.close()

# After the animation ends, save the data to an Excel file
data = {
    'Time (s)': time_list,
    'Brake Force': force_list
}

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)

# Write the DataFrame to an Excel file
df.to_excel(r'C:\Users\FSAE09\Desktop\Brake Pressure 3301R project\brake_pressure_data_kai_jun_800.xlsx', index=False)# Excel file is created in the current directory

print("Data saved to brake_pressure_data.xlsx")
