import json
import random


class ObjectStyle:
    """
    A class to manage the style for an object in a simulation.
    """

    def __init__(self, id: str, style: dict):
        self._id = id
        self._style = style

    def random_color(self) -> str:
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

    @property
    def color(self) -> str:
        try:
            return self._style['color']
        except KeyError:
            return self.random_color()

    @property
    def name(self) -> str:
        try:
            return self._style['name']
        except KeyError:
            return self._id

    def to_json(self) -> dict:
        return {
            'color': self.color,
            'name': self.name
        }


class Styles:
    """
    A class to manage styles for objects in a simulation.
    """

    def __init__(self):
        self._styles_raw = self._load_styles()

    def _load_styles(self) -> dict:
        """
        Loads the styles from the style.json file.
        """

        try:
            with open('style.json', 'r') as f:
                styles = json.load(f)
        except FileNotFoundError:
            styles = {}
            with open('style.json', 'w') as f:
                json.dump(styles, f, indent=4)

        return styles

    def save_styles(self):
        """
        Saves the styles to the style.json file.
        """

        with open('style.json', 'w') as f:
            json.dump(self._styles_raw, f, indent=4)

    def get_style(self, id: str) -> ObjectStyle:
        """
        Args:
            id (str): The id to get the style for.
        Returns:
            ObjectStyle: The style for the id.

        Gets the style for an id.
        """

        try:
            style = ObjectStyle(id, self._styles_raw[id])
        except KeyError:
            style = ObjectStyle(id, {})

        self._styles_raw[id] = style.to_json()
        self.save_styles()

        return style

    def get_styles(self, ids: list[str]) -> dict[str, ObjectStyle]:
        """
        Args:
            ids (list[str]): The list of ids to get styles for.
        Returns:
            dict[str, ObjectStyle]: A dictionary of styles.

        Gets the styles for a list of ids.
        """
        return {id: self.get_style(id) for id in ids}
