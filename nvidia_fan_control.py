import time
from pynvml import *

# Fan curve parameters
temperature_points = [0, 40, 57, 70]
fan_speed_points = [30, 40, 80, 100]

# Sleep interval to reduce CPU activity
sleep_seconds = 3

# Temperature hysteresis needed to lower fan speed
temperature_hysteresis = 5

# Initialize nvml
nvmlInit()

# Get device count
device_count = nvmlDeviceGetCount()

# Print out Nvidia Driver Version and Device Count

print("============================================================")
print(f"Driver Version: {nvmlSystemGetDriverVersion()}")
#print(f"Number of GPUs: {device_count}")

# For every device get its handle and fan count
for i in range(device_count):
    handle = nvmlDeviceGetHandleByIndex(i)
    fan_count = nvmlDeviceGetNumFans(handle)
    name = nvmlDeviceGetName(handle)
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
for i in range(fan_count):
    nvmlDeviceSetFanSpeed_v2(handle, i, fan_speed_points[0])


# Main loop
while True:
    # get the temperature
    temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
    if temperature is None:
        exit(1)

    # print debug: temperature
    # print(f"temperature: {temperature}")

    # change fan speed if temperature is lower than step down or higher than previous 
    if temperature < step_down_temperature or temperature > previous_temperature:
        # calculate the point of the fan curve (temperature and fan speed arrays)
        point = 0
        while temperature >= temperature_points[point]:
            point += 1
        
        print("============================================================")

        # print debug: temperature
        print(f"Temperature: {temperature}°C")

        # print debug: num_total_curve_point
        print(f"Total Curve Point: {num_total_curve_point}")

        # print debug: point
        print(f"Current Curve Point: {point}")

        previous_point = point - 1
        # print debug: previous_point
        print(f"Previous_Curve_Point: {previous_point}")

        # logic for the fan speed incremental variation (instead of a stepped fan curve)

        # calculate temperature delta between the new point and previous point
        temperature_delta = temperature_points[point] - temperature_points[previous_point]
        # calculate fan speed delta between the new point and previous point
        fan_speed_delta = fan_speed_points[point] - fan_speed_points[previous_point]
        # calculate the temperature increment which will be used to calculate fan speed increment
        temperature_increment = temperature - temperature_points[previous_point]
        # calculate fan speed increment, it depends on the temperature increment and previous deltas
        fan_speed_increment = fan_speed_delta * temperature_increment / temperature_delta
        # save previous temperature
        previous_temperature = temperature
        # calculate step down temperature
        step_down_temperature = temperature - temperature_hysteresis

        # calculate the total fan speed
        fan_speed = round(fan_speed_points[previous_point] + fan_speed_increment)
        # print debug: fan_speed
        print(f"Fan_Speed: {fan_speed}%")

        print("============================================================")

        # logic for the fan speed incremental variation (instead of a stepped fan curve)

        # calculate temperature delta between the new point and previous point
        # temperature_delta = temperature_points[point] - temperature_points[previous_point]
        # print debug: temperature_delta
        print(f"Temperature_Delta: {temperature_delta}")

        # calculate fan speed delta between the new point and previous point
        # fan_speed_delta = fan_speed_points[point] - fan_speed_points[previous_point]
        # print debug: fan_speed_delta
        print(f"Fan_Speed_Delta: {fan_speed_delta}")

        # calculate the temperature increment which will be used to calculate fan speed increment
        # temperature_increment = temperature - temperature_points[previous_point]
        # print debug: temperature_increment
        print(f"Temperature_Increment: {temperature_increment}")

        # calculate fan speed increment, it depends on the temperature increment and previous deltas
        # fan_speed_increment = fan_speed_delta * temperature_increment / temperature_delta
        # print debug: fan_speed_increment
        print(f"Fan_Speed_Increment: {fan_speed_increment}")

        # calculate the total fan speed
        # fan_speed = round(fan_speed_points[previous_point] + fan_speed_increment)
        # print debug: fan_speed
        # print(f"Fan_Speed: {fan_speed}%")

        # set the fan speed if different from previous fan speed (setting fan speed is expensive!)
        if fan_speed != setted_fan_speed:
            for i in range(fan_count):
                nvmlDeviceSetFanSpeed_v2(handle, i, fan_speed)
            # save the new setted_fan_speed
            setted_fan_speed = fan_speed

        # save previous temperature
        # previous_temperature = temperature
        # print debug: previous temperature
        print(f"Previous_Temperature: {previous_temperature}°C")

        # calculate step down temperature
        # step_down_temperature = temperature - temperature_hysteresis
        # print debug: step down temperature
        print(f"Step_Down_Temperature: {step_down_temperature}")

        print("============================================================")

    # wait some second before resuming the program
    time.sleep(sleep_seconds)
