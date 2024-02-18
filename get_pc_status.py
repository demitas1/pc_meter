from subprocess import Popen, PIPE
import re

# check command availabity by using 'command -v'
# $ commnad -v <command>

def check_command_available(command_name):
    # Run the command -v to check if the command is available
    process = Popen(f'command -v {command_name}', shell=True, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    return process.returncode == 0


for command in ['sensors', 'mpstat', 'nvidia-smi', 'free']:
    if not check_command_available(command):
        print(f'command of "{command}" is not available.')
        exit()


#
# get CPU temperature
#

process = Popen(['sensors'], stdout=PIPE, stderr=PIPE)
out, err = process.communicate()
out_lines = out.decode('utf-8').split('\n')
for l in out_lines:
    m = re.match(r'Tctl:\s+\+?(\d+(\.\d*)?)', l)
    if m:
        cpu_temp = float(m.group(1))
        print(f'CPU temperature = {cpu_temp}')

print('================================')

#
# get CPU usage
#

process = Popen('LC_ALL=C mpstat -P ALL', shell=True, stdout=PIPE, stderr=PIPE)
#process = Popen(['mpstat', '1', '1'], stdout=PIPE, stderr=PIPE)
out, err = process.communicate()
out_lines = out.decode('utf-8').split('\n')
for l in out_lines:
    m = re.match(r'\S+\s+(all|\d+)(\s+([\d\.]+)){10}', l)
    if m:
        cpu_index = m.group(1)
        cpu_usage = round(100.0 - float(m.group(3)), 2)
        print(f'CPU usage: {cpu_index} = {cpu_usage}')

print('================================')

#
# get GPU status
#

process = Popen(['nvidia-smi', '--query'], stdout=PIPE, stderr=PIPE)
out, err = process.communicate()
out_lines = out.decode('utf-8').split('\n')


def parse_text(input_lines):
    result = {}
    current_dict = result
    stack = [(0, result)]

    for line in input_lines:
        if len(line.strip()) == 0:
            continue  # skip blank lines
        if line[0] == '=':
            continue  # skip title line

        m = re.match(r'(.+?)\s+:\s+(.*)$', line)
        if m:
            key_value_pair = [m.group(1), m.group(2)]
        else:
            key_value_pair = [line]

        if len(key_value_pair) == 2:
            key = key_value_pair[0].strip()
            value = key_value_pair[1].strip()
            current_dict[key] = value
        else:
            key = key_value_pair[0].strip()
            indent_level = len(key_value_pair[0]) - len(key_value_pair[0].lstrip())
            while stack and stack[-1][0] >= indent_level:
                current_dict = stack.pop()[1]
            current_dict[key] = {}
            stack.append((indent_level, current_dict))
            current_dict = current_dict[key]

    return result


query_result = parse_text(out_lines)
for k, v in query_result.items():
    m = re.match(r'GPU [\d:\.]+', k)
    if m:
        print(f'Utillization: {v["Utilization"]}')
        print(f'Temperature: {v["Temperature"]}')
        print(f'GPU Power Readings: {v["GPU Power Readings"]}')

print('================================')

#
# get Memory usage
#

process = Popen(['free'], stdout=PIPE, stderr=PIPE)
out, err = process.communicate()
out_lines = out.decode('utf-8').split('\n')

for l in out_lines:
    m = re.match(r'Mem:\s+(\d+)\s+(\d+)', l)
    if m:
        memory_total = float(m.group(1))
        memory_used = float(m.group(2))
        memory_usage = round(memory_used / memory_total * 100, 2)
        print(f'Memory usage: {memory_usage} %')
