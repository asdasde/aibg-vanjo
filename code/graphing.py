import re


def get_energy_values(path_to_log):
    with open(path_to_log, 'r') as f:
        lines = f.readlines()
    energy_values = []
    regex = re.compile(r'turn [0-9]+ : ([0-9]+) xp: [0-9]+')
    for line in lines:
        result = regex.match(line)
        if result:
            energy_values.append(int(result.group(1)))
    return energy_values


if __name__ == '__main__':
    energy_values = get_energy_values('../error.log')
    print(energy_values)
