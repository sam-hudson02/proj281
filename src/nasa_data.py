import requests
import json

# Get the data from the NASA API


def make_request(body: str):
    url = f"https://ssd.jpl.nasa.gov/api/horizons.api?format=json&COMMAND='{body}'&OBJ_DATA='NO'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTOR'&CENTER='500@0'&START_TIME='2023-12-01'&STOP_TIME='2023-12-02'&STEP_SIZE='1%20d'"
    return requests.get(url)


def get_data():

    bodies = {
        'mercury': '199',
        'venus': '299',
        'earth': '399',
        'mars': '499',
        'jupiter': '599',
        'saturn': '699',
        'uranus': '799',
        'neptune': '899',
        'sun': '10'
    }

    data = {}

    for name, body in bodies.items():
        response = make_request(body)
        data[name] = response.json()

    return data


masses = {
    'mercury': 3.301e23,
    'venus': 4.867e24,
    'earth': 5.972e24,
    'mars': 6.417e23,
    'jupiter': 1.898e27,
    'saturn': 5.683e26,
    'uranus': 8.681e25,
    'neptune': 1.024e26,
    'sun': 1.989e30
}


def scrape_values(lines: list[str]):
    state_search = False
    state_search_i = 0
    values = {}
    for line in lines:
        line = line.strip()
        # replace all double spaces with single spaces
        while '  ' in line:
            line = line.replace('  ', ' ')

        if line.startswith('$$SOE'):
            state_search = True
        if line.startswith('$$EOE'):
            state_search = False

        if state_search:
            if state_search_i == 1:
                data_time = line.split('=')[0].strip()
                values['time'] = data_time

            if state_search_i == 2:
                data_x = float(line.split('=')[1][0:-2].strip()) * 1000
                data_y = float(line.split('=')[2][0:-2].strip()) * 1000
                data_z = float(line.split('=')[3].strip()) * 1000

                values['position'] = [data_x, data_y, data_z]

            if state_search_i == 3:
                data_x = float(line.split('=')[1][0:-2].strip()) * 1000
                data_y = float(line.split('=')[2][0:-2].strip()) * 1000
                data_z = float(line.split('=')[3].strip()) * 1000

                values['velocity'] = [data_x, data_y, data_z]

            state_search_i += 1

    return values


def main():
    all_data = get_data()
    to_save = {}
    for name, data in all_data.items():
        results = data['result']
        lines = results.split('\n')
        values = scrape_values(lines)
        values['mass'] = masses[name]
        print(name, values)
        to_save[name] = values
    with open('data/nasa_data.json', 'w') as f:
        json.dump(to_save, f, indent=4)


if __name__ == '__main__':
    main()
