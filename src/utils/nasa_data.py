import requests
import json
from datetime import datetime, timedelta
import numpy as np


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


class NasaObjectData:
    def __init__(self, parsed_json: dict):
        self._parsed_json = parsed_json
        self.mass = self.find_mass()
        self.radius = self.find_mean_radius()
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

    def find_mean_radius(self) -> float:
        """
        Returns:
            (float): mean radius (m)
        """
        for k in self._parsed_json.keys():
            if 'mean_radius' in k:
                return float(self._parsed_json[k]) * 1000
        raise ValueError('Could not find mean radius')

    def find_mass(self) -> float:
        """
        Returns:
            (float): mass (kg)
        """
        for k in self._parsed_json.keys():
            if 'mass' in k:
                return float(self._parsed_json[k])

        density = self.find_density()
        radius = self.find_mean_radius()

        # convert g cm^-3 to kg m^-3
        volume = (4 / 3) * np.pi * radius**3
        mass = density * volume

        return mass

    def find_density(self) -> float:
        """
        Returns:
            (float): density (kg/m^3)
        """
        for k in self._parsed_json.keys():
            if 'density' in k or 'dens' in k:
                return float(self._parsed_json[k]) * 1000
        raise ValueError('Could not find density')


class NasaVectorData:
    def __init__(self, parsed_json: dict):
        self._parsed_json = parsed_json
        self.position = np.array(parsed_json['position'])
        self.velocity = np.array(parsed_json['velocity'])


class NasaData:
    def __init__(self, parsed_json: dict, start_time: datetime):
        self.object_data = NasaObjectData(parsed_json['object_data'])
        self.vector_data: NasaVectorData = NasaVectorData(
            parsed_json['vector_data'])

        # convert datetime to seconds
        self.ts = start_time.timestamp()


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
                    data[body_id] = NasaData(json.load(f),
                                             start_time=self.start_time)
                    print(f'Loaded {body_id} from cache')
                continue
            except FileNotFoundError:
                print(f'Downloading {body_id} data from NASA API')
                response = self._make_request(str(body_id))
                json_data = response.json()
                parsed = NasaDataParser(json_data['result']).parse()
                with open(f'data/nasa_cache/{cache_title}.json', 'w') as f:
                    json.dump(parsed, f, indent=4)
                with open(f'data/nasa_cache/{cache_title}_raw.txt', 'w') as f:
                    f.write(json_data['result'])
                data[body_id] = NasaData(parsed, start_time=self.start_time)

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
        """
        Args:
            data_lines (list[str]): The lines of data from the NASA API
        returns:
            mid_point (int): The index of the midpoint of the data

        Attempts to find the midpoint of nasa planet data, which
        can be used to split the data into two parts, each of which
        contains a key and a value.
        """
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
        """
        Args:
            lines (list[str]): The lines of data from the NASA API
        returns:
            object_info (dict): A dictionary containing the object info

        Attempts to parse the object info from the text data.
        """

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
            first_part = line[0:mid_point+1]
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
            ' (km^3/s^2)',
            ' (g cm^-3)'
        ]

        data_key_vales = {}
        for key, value in data_key_vales_str.items():
            mult = 1
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
                elif 'x 10^' in key:
                    mult = 10 ** self.str_to_float(key.split('^')[1])
                    key = key.split('x 10^')[0]
                elif '10^' in key:
                    mult = 10 ** self.str_to_float(key.split('^')[1])
                    key = key.split('10^')[0]
            key = key.split(',')[0]
            key = key.replace(' ', '_')
            key = key.lower()
            value_float = self.clean_value(value)
            if grams:
                value_float /= 1000
            data_key_vales[key] = value_float * mult

        return data_key_vales

    def clean_value(self, value: str) -> float:
        """
        Args:
            value (str): The value to clean
        returns:
            value (float): The cleaned value

        Attempts to clean the value of the data.
        """
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
        """
        Args:
            string (str): The string to convert
        returns:
            float | list[float]: The converted float or list of floats

        Attempts to convert a string to a float or list of floats.
        """

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

    def parse_values(self, lines: list[str]) -> dict[str, list[float]]:
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

            # convert from km to m
            x_pos = float(parts[2].strip()) * 1000
            y_pos = float(parts[3].strip()) * 1000
            z_pos = float(parts[4].strip()) * 1000

            x_vel = float(parts[5].strip()) * 1000
            y_vel = float(parts[6].strip()) * 1000
            z_vel = float(parts[7].strip()) * 1000

            # convert from JD to seconds
            pos = [x_pos, y_pos, z_pos]
            vel = [x_vel, y_vel, z_vel]
            values = {'position': pos, 'velocity': vel}

        return values

    def parse(self) -> dict:
        """
        Args:
            None
        returns:
            parsed_data (dict): The parsed data from the NASA API

        Attempts to parse the data from the NASA API.
        """
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
