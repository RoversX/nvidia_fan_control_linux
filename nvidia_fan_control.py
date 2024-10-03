import time
from pynvml import *
import os

# Fan curve parameters
temperature_points = [0, 40, 57, 70]
fan_speed_points = [27, 40, 80, 100]

# GPU selection for fan curve application
# Specify which GPUs to control by their indices
# Examples:
#   gpus = []     : Control all detected GPUs (default)
#   gpus = [0]    : Control only the first GPU
#   gpus = [0, 1] : Control the first and second GPUs
# Note: GPU indices start at 0, so 0 is the first GPU, 1 is the second, etc.
gpus = []

# Enable or disable GPU Validation
# GPU_VALIDATION_SETTINGS controls whether GPU index validation is performed.
# When True, the program checks if the provided GPU indices are within the valid range.
# This can be useful for small systems, but in large GPU clusters (hundreds or thousands of GPUs),
# it can introduce performance overhead due to index checking.
# GPU index verification is disabled by default, set to 'True' to enable GPU number verification
GPU_VALIDATION_SETTINGS = {
    'ENABLE': True,  # Whether to enable GPU index validation
    'SHOW_INVALID_INDICES': True  # Only show invalid GPU indices when ENABLE is True
}

# Sleep interval to reduce CPU activity
sleep_seconds = 5

# Temperature hysteresis needed to lower fan speed
temperature_hysteresis = 5

# Initialize nvml
nvmlInit()

# Get device count
device_count = nvmlDeviceGetCount()

# Check for valid GPUs based on the validation flag
if GPU_VALIDATION_SETTINGS['ENABLE']:
    if not gpus:
        gpus = list(range(device_count))
    else:
        # First use any() to quickly check if there are invalid GPU indices
        if any(gpu >= device_count or gpu < 0 for gpu in gpus):
            # Only when you need to display invalid indexes, find and record specific invalid indexes
            if GPU_VALIDATION_SETTINGS['SHOW_INVALID_INDICES']: 
                invalid_gpus = [gpu for gpu in gpus if gpu >= device_count or gpu < 0]
                print(f"ERROR: Invalid GPU index found:{invalid_gpus}")
                print(f"Your system has {device_count} GPUs, and indexes range from 0 to {device_count - 1}.")
                print(f"Please check your gpus settings and correct the invalid index.（＾ｖ＾）")
            # If you don't need to display specific invalid indexes, print general error messages directly    
            else:
                print("ERROR: Invalid GPU index found")
                print(f"Your system has {device_count} GPUs, and indexes range from 0 to {device_count - 1}.")
                print(f"If you want to display specific invalid indexes, set 'SHOW_INVALID_INDICES' to 'True' ")
                print(f"Please check your gpus settings and correct the invalid index.（＾ｖ＾）")
            nvmlShutdown()
            exit(1)
    # If there is no valid GPU, prompt an error and exit
    if not gpus:
        print("Error: No valid GPU found. Please check your gpus settings.（＾ｖ＾）")
        print(f"Your system has {device_count} GPUs, and indexes range from 0 to {device_count - 1}.")
        nvmlShutdown()
        exit(1)

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
    if not gpus or i in gpus:
        handles.append(handle)
        fan_counts.append(fan_count)
        print(f"GPU {i}: {name}")
        print(f"Fan Count: {fan_count}")
    else:
        print(f"Skipping GPU {i}: {name}")

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
                while point < num_total_curve_point - 1 and temperature >= temperature_points[point + 1]:
                    point += 1

                previous_point = max(0, point)
                next_point = min(num_total_curve_point - 1, point + 1)

                # logic for the fan speed incremental variation (instead of a stepped fan curve)
                temperature_delta = temperature_points[next_point] - temperature_points[previous_point]
                fan_speed_delta = fan_speed_points[next_point] - fan_speed_points[previous_point]
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
Next_Curve_Point: {next_point}
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
