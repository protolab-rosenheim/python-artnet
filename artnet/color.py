class Color:
    colors = {'black': [0, 0, 0], 'blue': [0, 0, 50], 'cyan': [0, 50, 50], 'green': [0, 50, 0], 'magenta': [50, 0, 50],
              'orange': [50, 25, 0], 'pink': [50, 0, 20], 'red': [50, 0, 0], 'yellow': [50, 50, 0],
              'white': [50, 50, 50]}
    colors_hex = {'#008000': [0, 70, 0], '#0000FF': [0, 0, 50], '#FF8C00': [50, 25, 0], '#000000': [0, 0, 0],
                  '#ff0000': [50, 0, 0], '#800080': [50, 0, 50]}

    def __init__(self, red=0, green=0, blue=0):
        if red not in range(256):
            raise ValueError("Only a red value between 0-255 is allowed")
        self.red = red

        if green not in range(256):
            raise ValueError("Only a green value between 0-255 is allowed")
        self.green = green

        if blue not in range(256):
            raise ValueError("Only a green value between 0-255 is allowed")
        self.blue = blue

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            same = True
            if not self.red == other.red:
                same = False
            if not self.green == other.green:
                same = False
            if not self.blue == other.blue:
                same = False

            return same
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_color(self, color='red'):
        if color.startswith('#'):
            self.red, self.green, self.blue = self.colors_hex[color]
        else:
            self.red, self.green, self.blue = self.colors[color]