# color.py - Class to wrap a color value.

# Wrapper function for a color value.
class Color:
    # Initialize the color.
    def __init__(self, value = { "red": 0, "blue": 0, "green": 0, "white": 0 }):
        self.set(value)

    # Create a color from an HTML value (#RRGGBB).
    def from_html(colorstring):
        return Color(colorstring)

    def set(self, value):
        if isinstance(value, Color):
            self.red   = value.red
            self.green = value.green
            self.blue  = value.blue
            self.white = value.white
            return

        if isinstance(value, str):
            self.set_from_html(value)
            return

        self.red   = value["red"]
        self.green = value["green"]
        self.blue  = value["blue"]

        # White values are optional.
        if "white" in value:
            self.white = value["white"]
        else:
            self.white = 0

    def set_from_html(self, colorstring):
        if colorstring[0] == '#': 
            colorstring = colorstring[1:]

        if len(colorstring) != 6:
            raise ValueError("Knob color #%s is not in #RRGGBB format" % 
                             colorstring)
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]

        self.set(value = { "red": r, "green": g, "blue": b, "white": 0 })

    # Add the value to this color.
    def add(self, value):
        self.red   += value.red
        self.green += value.green
        self.blue  += value.blue
        self.white += value.white
