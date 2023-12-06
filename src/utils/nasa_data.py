import requests
import json
from datetime import datetime, timedelta
import numpy as np
# Get the data from the NASA API


def test_request():
    body = '399'
    requester = NasaQuery()
    response = requester._make_request(body)
    json_data = response.json()
    text_data = json_data['result']
    with open('test_data.txt', 'w') as f:
        f.write(text_data)


def test_parser():
    with open('test_data.txt', 'r') as f:
        data = f.read()
    parser = NasaDataParser(data)
    parsed = parser.parse()
    print(parsed)


class NasaObjectData:
    def __init__(self, parsed_json: dict):
        self._parsed_json = parsed_json
        self.mass = parsed_json['mass']
        self.radius = parsed_json['vol._mean_radius']
        self.rot_rate = self.find_rot_rate()

    def find_rot_rate(self) -> float:
        """
        Returns:
            (float): rotation rate (radians per second)
        """
        for k in self._parsed_json.keys():
            if 'rot._rate' in k:
                return self._parsed_json[k]
        return 0.0


class NasaData:
    def __init__(self, parsed_json: dict):
        self.object_data = NasaObjectData(parsed_json['object_data'])
        self.vector_data: dict['str',
                               dict['str', np.ndarray]] = parsed_json['vector_data']


class NasaQuery:
    def __init__(self,
                 center: str = '500@0',
                 start_time: datetime = datetime.now(),
                 object_data: bool = True):
        self.url = 'https://ssd.jpl.nasa.gov/api/horizons.api?format=json'
        self.center = center
        self.start_time = start_time
        self.stop_time = start_time + timedelta(days=1)
        self.object_data = object_data
        self.csv_format = True
        self.make_emphemeris = True
        self.emphemeris_type = 'VECTOR'
        self.step_size = '1%20d'

    def _make_request(self, body: str):

        url = self.url
        url += f'&COMMAND=\'{body}\''
        if self.object_data:
            url += '&OBJ_DATA=\'YES\''
        else:
            url += '&OBJ_DATA=\'NO\''

        url += '&MAKE_EPHEM=\'YES\''
        url += f'&EPHEM_TYPE=\'{self.emphemeris_type}\''
        url += f'&CENTER=\'{self.center}\''
        url += f'&START_TIME=\'{self.start_time.strftime("%Y-%m-%d")}\''
        url += f'&STOP_TIME=\'{self.stop_time.strftime("%Y-%m-%d")}\''
        url += f'&STEP_SIZE=\'{self.step_size}\''
        url += '&CSV_FORMAT=\'YES\''
        url += '&VEC_TABLE=\'2\''

        # specify kg and km
        url += '&OUT_UNITS=\'KM-S\''

        return requests.get(url)

    def get_data(self, bodies: list[int]) -> dict[int, NasaData]:

        data = {}

        print(f'Getting data for {len(bodies)} bodies...')

        for body_id in bodies:
            cache_title = f'{body_id}_{self.start_time.strftime("%Y-%m-%d")}'
            try:
                with open(f'data/nasa_cache/{cache_title}.json', 'r') as f:
                    data[body_id] = NasaData(json.load(f))
                    print(f'Loaded {body_id} from cache')
                continue
            except FileNotFoundError:
                print(f'Downloading {body_id} data from NASA API')
                response = self._make_request(str(body_id))
                json_data = response.json()
                parsed = NasaDataParser(json_data['result']).parse()
                with open(f'data/nasa_cache/{cache_title}.json', 'w') as f:
                    json.dump(parsed, f, indent=4)
                data[body_id] = NasaData(parsed)

        return data


class NasaDataParser:
    def __init__(self, data: str):
        self.data = data

    def get_chunks(self, lines: list[str]) -> list[list[str]]:
        """
        Args:
            lines (list[str]): The lines of data from the NASA API
        returns:
            chunks (list[list[str]]):

        Splits the data into chunks,
        nasa separates its data with lines of *'s
        """
        chunks = []
        chunk = []

        for line in lines:
            if line.startswith('*'):
                if len(chunk) > 0:
                    chunks.append(chunk)
                    chunk = []
            else:
                chunk.append(line)

        return chunks

    def get_midpoint(self, data_lines: list[str]) -> int:
        first_data_line = data_lines[0]
        first_data_line = first_data_line.split('=')
        hit_val = False
        hit_whitespace = False
        mid_point = 0
        for i, c in enumerate(first_data_line[1]):
            if not hit_val:
                if c != ' ':
                    hit_val = True
            elif not hit_whitespace:
                if c == ' ':
                    hit_whitespace = True
            else:
                if c != ' ':
                    mid_point = i - 1
                    break
        # add back the length of the first part of the line
        mid_point += len(first_data_line[0])
        return mid_point

    def parse_object_info(self, lines: list[str]) -> dict:
        data_lines = []
        title_lines = []
        for line in lines:
            if '=' in line:
                data_lines.append(line)
            else:
                title_lines.append(line)

        mid_point = self.get_midpoint(data_lines)

        data_key_vales_raw = []
        for line in data_lines:
            first_part = line[0:mid_point]
            second_part = line[mid_point:]
            if '=' in first_part:
                data_key_vales_raw.append(first_part)
            if '=' in second_part:
                data_key_vales_raw.append(second_part)

        data_key_vales_str = {}
        for line in data_key_vales_raw:
            key = line.split('=')[0].strip()
            value = line.split('=')[1].strip()
            data_key_vales_str[key] = value

        crop_keys = [
            ' (km)',
            ' km',
            ' g/cm^3',
            ' s',
            ' (Ts)',
            ' (Te)',
            ' (kg)',
            ' (deg)',
            ' (rad/s)',
        ]

        data_key_vales = {}
        for key, value in data_key_vales_str.items():
            mult = 1
            key = key.split(',')[0]
            grams = False
            if '(g)' in key:
                grams = True
            for crop_key in crop_keys:
                if crop_key in key:
                    key = key.replace(crop_key, '')
                key = key.strip()
                if 'x10^' in key:
                    mult = 10 ** self.str_to_float(key.split('^')[1])
                    key = key.split('x10^')[0]
                if 'x 10^' in key:
                    mult = 10 ** self.str_to_float(key.split('^')[1])
                    key = key.split('x 10^')[0]
            key = key.replace(' ', '_')
            key = key.lower()
            value_float = self.clean_value(value)
            if grams:
                value_float /= 1000
            data_key_vales[key] = value_float * mult

        return data_key_vales

    def clean_value(self, value: str) -> float:
        value = value.strip()
        value = value.split('+-')[0]
        value = value.split('+/-')[0]
        mult = 1
        if 'x10^' in value:
            mult = 10 ** self.str_to_float(value.split('^')[1])
            value = value.split('x 10^')[0]
        value_float = self.str_to_float(value)
        return value_float * mult

    def str_to_float(self, string: str) -> float | list[float]:
        parts = [string]
        parsed = []
        if ',' in string:
            parts = string.split(',')
        for part in parts:
            chars = ''
            for i, c in enumerate(part):
                if c.isdigit():
                    chars += c
                elif c == '.':
                    # check surrounding chars
                    try:
                        if part[i + 1].isdigit() and part[i - 1].isdigit():
                            chars += c
                    except IndexError:
                        pass
            if len(chars) > 0:
                parsed.append(float(chars))
            else:
                parsed.append(0)
        if len(parsed) == 1:
            return parsed[0]
        else:
            return parsed

    def parse_values(self, lines: list[str]) -> dict[str, dict[str, list[float]]]:
        """
        Args:
            lines (list[str]): The lines of data from the NASA API
        returns:
            values (dict[str, dict[str, np.ndarray]]):
                A dictionary of the values of the data
                The first key is the name of the body
                The second key is the name of the value
                The value is a numpy array of the values
        """
        values = {}
        for line in lines:
            if ',' not in line:
                continue
            parts = line.split(',')
            ts = float(parts[0].strip())
            pos = [float(parts[2].strip()), float(
                parts[3].strip()), float(parts[4].strip())]
            vel = [float(parts[5].strip()), float(
                parts[6].strip()), float(parts[7].strip())]
            values[ts] = {'position': pos, 'velocity': vel}
        return values

    def parse(self):
        parsed_data = {}
        lines = self.data.split('\n')
        chunks = self.get_chunks(lines)
        object_data = self.parse_object_info(chunks[0])
        parsed_data['object_data'] = object_data
        for chunk in chunks:
            if '$$SOE' in chunk[0]:
                values = self.parse_values(chunk)
                parsed_data['vector_data'] = values
        return parsed_data


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


def main_():
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


def main():
    test_request()
    requester = NasaQuery()
    data = requester.get_data(
        [
            199,
            299,
            399,
            499,
            599,
            699,
            799,
            899,
            10
        ]
    )
    with open('data/nasa_data_test.json', 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    main()
