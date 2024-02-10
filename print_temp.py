import psutil
from subprocess import Popen, PIPE
import re

cpu_count = psutil.cpu_count()
print(f'CPU count: {cpu_count}')

cpu_load0 = round(psutil.getloadavg()[0] / cpu_count * 100, 2)
print(f'CPU load: {cpu_load0} %')
print(f'Memory usage: {psutil.virtual_memory().percent} %')
temps = psutil.sensors_temperatures()
for label_device, info in temps.items():
    for tempinfo in info:
        print(f'{label_device} {tempinfo.label}: {tempinfo.current} \u2103')

process = Popen(['gpustat'], stdout=PIPE, stderr=PIPE)
out, err = process.communicate()
gpu_out = out.decode('utf-8').strip().split('|')

# print(f'GPU: {gpu_out}')
m = re.match(r'\s*(\d+).*,\s+(\d+) %', gpu_out[1])
if m:
    gpu_temp = float(m.group(1))
    gpu_load = float(m.group(2))
    print(f'GPU: {gpu_temp} \u2103, {gpu_load} %')
