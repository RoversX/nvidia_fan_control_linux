# A simple script to control nvidia GPU fan speed in Linux.
(No GUI Required,just need SSH)(Support Multiple GPUs and GPU index validation)(Perhaps the simplest)

#### Fan curve points Graph
<img width="500" alt="Screenshot 2024-06 at 3 04 05 PM" src="https://github.com/RoversX/nvndia_fan__control_linux/assets/85817538/a25a720f-ac68-487a-b760-2c81b5b74136">

## Quick Start 
Set up Environment
```bash
python3 -m venv fan
```
Activate Environment
```bash
source fan/bin/activate
```
Install pynvml
```bash
pip3 install pynvml
```
Get python file
```bash
wget https://raw.githubusercontent.com/RoversX/nvidia_fan_control_linux/main/nvidia_fan_control.py
```
Return to the previous directory maybe
```bash
cd ``
```
Create fan.sh for simple use
```bash
nano fan.sh
```
Copy script into the file
```sh
#!/bin/bash

# Use sudo to elevate privileges and activate the virtual environment
sudo bash <<EOF
source /home/x/Workspace/fan/bin/activate
python /home/x/Workspace/fan/nvidia_fan_control.py
deactivate
EOF
```
Start fan control
```bash
./fan.sh
```
### Requirements

NVIDIA's driver 🤗

## Version 1

### Enhanced Points
A more user-friendly UI has been added to the original version to facilitate user adjustment.
### Example Output
```bash
x@x:~$ ./fan.sh
[sudo] password for x: 
============================================================
Driver Version: 535.183.01
GPU 0: NVIDIA GeForce RTX 2080 Ti
Fan Count: 1
============================================================
Temperature: 42°C
Total Curve Point: 4
Current Curve Point: 2
Previous_Curve_Point: 1
Fan_Speed: 45%
============================================================
Temperature_Delta: 17
Fan_Speed_Delta: 40
Temperature_Increment: 2
Fan_Speed_Increment: 4.705882352941177
Previous_Temperature: 42°C
Step_Down_Temperature: 37
============================================================

```

### If you want to draw fan speed curve
```py
import matplotlib.pyplot as plt

# Fan Curve Parameters
temperature_points = [0, 40, 57, 70]
fan_speed_points = [30, 40, 80, 100]

# Draw curve
plt.figure(figsize=(8, 6))
plt.plot(temperature_points, fan_speed_points, marker='o', linestyle='-', color='b', markersize=8)
plt.title('Fan Speed Curve')
plt.xlabel('Temperature (°C)')
plt.ylabel('Fan Speed (%)')
plt.grid(True)
plt.xticks(temperature_points)
plt.yticks(fan_speed_points)
plt.tight_layout()
plt.show()
```

### Improved based on: 
https://github.com/Cippo95/nvidia-fan-control



## Reference Version

### Original Source:

https://gist.github.com/AlexKordic/65f031b708177a01a002cc19f0d7298c

### Example Output


```bash
:~$ ./fan.sh
Driver Version: 535.183.01
0:NVIDIA GeForce RTX 2080 Ti fans=1 27-100
0:NVIDIA GeForce RTX 2080 Ti t=36 27 >> 40
0:NVIDIA GeForce RTX 2080 Ti t=36 43 >> 40
0:NVIDIA GeForce RTX 2080 Ti t=36 41 >> 40
0:NVIDIA GeForce RTX 2080 Ti t=36 39 >> 40
0:NVIDIA GeForce RTX 2080 Ti t=35 40 >> 37
0:NVIDIA GeForce RTX 2080 Ti t=35 36 >> 37
0:NVIDIA GeForce RTX 2080 Ti t=34 37 >> 35

```



An interesting resource: https://askubuntu.com/questions/42494/how-can-i-change-the-nvidia-gpu-fan-speed
