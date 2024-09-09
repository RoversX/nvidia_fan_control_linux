import time
from pynvml import *
import os

# Fan curve parameters
temperature_points = [0, 40, 57, 70]
fan_speed_points = [27, 40, 80, 100]

# Sleep interval to reduce CPU activity
sleep_seconds = 5

# Temperature hysteresis needed to lower fan speed
temperature_hysteresis = 5

# Initialize nvml
nvmlInit()

# Get device count
device_count = nvmlDeviceGetCount()

# Print out Nvidia Driver Version and Device Count
print("============================================================")
print(f"Driver Version: {nvmlSystemGetDriverVersion()}")

# For every device get its handle and fan count
handles = []
fan_counts = []
for i in range(device_count):
    handle = nvmlDeviceGetHandleByIndex(i)
    fan_count = nvmlDeviceGetNumFans(handle)
    name = nvmlDeviceGetName(handle)
    handles.append(handle)
    fan_counts.append(fan_count)
    print(f"GPU {i}: {name}")
    print(f"Fan Count: {fan_count}")

# Initialize starting temperatures and fan speed
step_down_temperature = 0
previous_temperature = 0
setted_fan_speed = fan_speed_points[0]

# Validate temperature and fan speed points arrays length
if len(temperature_points) != len(fan_speed_points):
    raise ValueError("temperature_points and fan_speed_points must have the same length")
else:
    num_total_curve_point = len(temperature_points)

# Validate temperature and fan speed values
for i in range(len(temperature_points) - 1):
    if temperature_points[i] >= temperature_points[i + 1]:
        raise ValueError("temperature_points must be strictly increasing")
    if fan_speed_points[i] > fan_speed_points[i + 1]:
        raise ValueError("fan_speed_points must be increasing")

# Set the minimum fan speed (it also enables manual fan control)
for handle, fan_count in zip(handles, fan_counts):
    for i in range(fan_count):
        nvmlDeviceSetFanSpeed_v2(handle, i, fan_speed_points[0])

# Function to clear specified number of lines
def clear_lines(num_lines):
    for _ in range(num_lines):
        print('\033[1A\033[K', end='')

# Function to print information and return the number of lines printed
def print_info(info):
    lines = info.split('\n')
    for line in lines:
        print(line)
    return len(lines)

# Main loop
last_lines = 0
try:
    while True:
        for handle, fan_count in zip(handles, fan_counts):
            # get the temperature
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            if temperature is None:
                exit(1)

            # change fan speed if temperature is lower than step down or higher than previous 
            if temperature < step_down_temperature or temperature > previous_temperature:
                # calculate the point of the fan curve (temperature and fan speed arrays)
                point = 0
                # 这是唯一的修改：将 num_total_curve_point 改为 num_total_curve_point - 1
                while point < num_total_curve_point - 1 and temperature >= temperature_points[point]:
                    point += 1

                previous_point = max(0, point - 1)

                # logic for the fan speed incremental variation (instead of a stepped fan curve)
                temperature_delta = temperature_points[point] - temperature_points[previous_point]
                fan_speed_delta = fan_speed_points[point] - fan_speed_points[previous_point]
                temperature_increment = temperature - temperature_points[previous_point]
                fan_speed_increment = fan_speed_delta * temperature_increment / temperature_delta if temperature_delta != 0 else 0
                previous_temperature = temperature
                step_down_temperature = temperature - temperature_hysteresis

                # calculate the total fan speed
                fan_speed = round(fan_speed_points[previous_point] + fan_speed_increment)

                # Prepare information to be printed
                info = f"""============================================================
Temperature: {temperature}°C
Total Curve Point: {num_total_curve_point}
Current Curve Point: {point}
Previous_Curve_Point: {previous_point}
Fan_Speed: {fan_speed}%
============================================================
Temperature_Delta: {temperature_delta}
Fan_Speed_Delta: {fan_speed_delta}
Temperature_Increment: {temperature_increment}
Fan_Speed_Increment: {fan_speed_increment}
Previous_Temperature: {previous_temperature}°C
Step_Down_Temperature: {step_down_temperature}
============================================================"""

                # Clear previous output
                if last_lines > 0:
                    clear_lines(last_lines)

                # Print new information and record number of lines
                last_lines = print_info(info)

                # set the fan speed if different from previous fan speed (setting fan speed is expensive!)
                if fan_speed != setted_fan_speed:
                    for i in range(fan_count):
                        nvmlDeviceSetFanSpeed_v2(handle, i, fan_speed)
                    # save the new setted_fan_speed
                    setted_fan_speed = fan_speed

        # wait some second before resuming the program
        time.sleep(sleep_seconds)
finally:
    # reset to auto fan control
    for handle, fan_count in zip(handles, fan_counts):
        for i in range(fan_count):
            nvmlDeviceSetDefaultFanSpeed_v2(handle, i)
    nvmlShutdown()
