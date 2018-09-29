import copy
from datetime import datetime
from .color import Color
from .packets import PacketType, ArtNetDMXPacket


class ArtNetNode(object):
    """Contains an art net node(LED-controller)"""

    def __init__(self, name, ip_address, port=6454, max_history_size=5):
        """
        :param name: name of the device
        :param ip_address:
        :param port: default is 6454
        :param max_history_size: value between 0-100, default is 5
        """
        self.name = name
        self.ip_address = ip_address
        # Contains a dict with universes and their LED strips. E.g.: {1: led_strip, 3:led_strip}
        self.universe = {}
        # Contains a dict with slots. E.g.: {slot_1: {universe: 1, led: 0-3}, slot_2: {universe: 1, led: 4-6}}
        self.slots = {}
        self.send_queue = []
        self.sequence = 1
        if port not in range(65536):
            raise ValueError("Only values between 0-65535 are valid for ports")
        self.port = port

        self.device_last_seen = datetime.min
        self.slot_history = []
        if max_history_size not in range(101):
            raise ValueError("Only values between 0-100 are valid for history size")
        self._max_history_size = max_history_size
        self.color_history = []

    def illuminate_multiple_slots(self, slots, color):
        """Illuminate multiple slots, in one color, don't add them to illuminated history. Slots delimiter is ';'"""
        slot_color = {}
        for slot_name in slots.split(';'):
            slot = 'slot_' + str(slot_name)
            if self.slots.get(slot) and Color.colors.get(color):
                slot_color[slot] = color

        led_strip_dict = self._history_led_strip_builder(slot_color)

        for entry in led_strip_dict:
            self._sequenzer()
            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(entry),
                                                   led_strip_dict[
                                                       entry].to_byte_array()).packet_to_byte_array())
        if len(slot_color) > 0:
            return True
        else:
            return False

    def illuminate_multiple_slots_opcua_call(self, parent, slot_name, color):
        """Only use this method for calls from python-opcua"""
        from opcua import ua
        ret = self.illuminate_multiple_slots(slot_name.Value, color.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_slot(self, slot_name, color):
        """Illuminates a slot and adds it to the illuminated slots history"""
        return self.illuminate_slot_with_history(slot_name, color, 0)

    def illuminate_slot_dont_coll_history(self, slot_name, color):
        """Illuminates the given slot but don't add it to the history of illuminated slots"""
        slot = 'slot_' + str(slot_name)
        if self.slots.get(slot) and Color.colors.get(color):
            led_strip_dict = self._history_led_strip_builder({slot: color})

            for entry in led_strip_dict:
                self._sequenzer()
                self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(entry),
                                                       led_strip_dict[entry].to_byte_array()).packet_to_byte_array())
            return True
        else:
            return False

    def illuminate_slot_dont_coll_history_opcua_call(self, parent, slot_name, color):
        """Only use this method for calls from python-opcua"""
        from opcua import ua
        ret = self.illuminate_slot_dont_coll_history(slot_name.Value, color.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_slot_opcua_call(self, parent, slot_name, color):
        """Only use this method for calls from python-opcua"""
        from opcua import ua
        ret = self.illuminate_slot_with_history(slot_name.Value, color.Value, 0)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_slot_with_history(self, slot_name, color, history_to_illu):
        slot = 'slot_' + str(slot_name)

        if self.slots.get(slot) and Color.colors.get(color):

            slot_history = self._history_builder(slot_name, color, history_to_illu)
            led_strip_dict = self._history_led_strip_builder(slot_history)

            for entry in led_strip_dict:
                self._sequenzer()
                self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(entry),
                                                       led_strip_dict[entry].to_byte_array()).packet_to_byte_array())

            if slot in self.slot_history:
                self.slot_history.remove(slot)
            self.slot_history.insert(0, slot)
            if len(self.slot_history) > self._max_history_size:
                self.slot_history.pop()

            return True
        else:
            return False

    def illuminate_slot_with_history_opcua_call(self, parent, slot_name, color, history_to_illu):
        from opcua import ua
        ret = self.illuminate_slot_with_history(slot_name.Value, color.Value, history_to_illu.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_universe(self, universe, color):
        if self.universe.get(universe):
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))

            for c in tmp_led_strip.led_strip:
                c.set_color(color)

            self._sequenzer()
            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                   tmp_led_strip.to_byte_array()).packet_to_byte_array())
            return True
        else:
            return False

    def illuminate_universe_opcua_call(self, parent, universe, color):
        from opcua import ua
        ret = self.illuminate_universe(str(universe.Value), color.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_universe_rgb(self, universe, red, green, blue):
        if self.universe.get(universe):
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))

            for c in tmp_led_strip.led_strip:
                c.red = red
                c.green = green
                c.blue = blue

            self._sequenzer()
            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                   tmp_led_strip.to_byte_array()).packet_to_byte_array())
            return True
        else:
            return False

    def illuminate_universe_rgb_opcua_call(self, parent, universe, red, green, blue):
        from opcua import ua
        ret = self.illuminate_universe_rgb(str(universe.Value), red.Value, green.Value, blue.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_all(self, color):
        for universe in self.universe:
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))
            for c in tmp_led_strip.led_strip:
                c.set_color(color)

            self._sequenzer()
            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                   tmp_led_strip.to_byte_array()).packet_to_byte_array())
        return True

    def illuminate_all_opcua_call(self, parent, color):
        from opcua import ua
        ret = self.illuminate_all(color.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_from_to(self, universe, start_led, end_led, color):
        if self.universe.get(universe) and start_led >= 0:
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))

            if end_led < len(tmp_led_strip.led_strip):
                for i in range(start_led, end_led + 1, 1):
                    tmp_led_strip.led_strip[i].set_color(color)

                self._sequenzer()
                self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                       tmp_led_strip.to_byte_array()).packet_to_byte_array())
                return True
            else:
                return False
        else:
            return False

    def illuminate_from_to_opcua_call(self, parent, universe, start_led, end_led, color):
        from opcua import ua
        ret = self.illuminate_from_to(str(universe.Value), start_led.Value, end_led.Value, color.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def illuminate_from_to_rgb(self, universe, start_led, end_led, red, green, blue):
        if self.universe.get(universe) and start_led >= 0:
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))

            if end_led <= len(tmp_led_strip.led_strip):
                for i in range(start_led, end_led + 1, 1):
                    tmp_led_strip.led_strip[i].red = red
                    tmp_led_strip.led_strip[i].green = green
                    tmp_led_strip.led_strip[i].blue = blue

                self._sequenzer()
                self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                       tmp_led_strip.to_byte_array()).packet_to_byte_array())
                return True
            else:
                return False
        else:
            return False

    def illuminate_from_to_rgb_opcua_call(self, parent, universe, start_led, end_led, red, green, blue):
        from opcua import ua
        ret = self.illuminate_from_to_rgb(str(universe.Value), start_led.Value, end_led.Value,
                                          red.Value, green.Value, blue.Value)
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def all_off(self):
        for universe in self.universe:
            tmp_led_strip = copy.deepcopy(self.universe.get(universe))

            self._sequenzer()
            self.send_queue.append(ArtNetDMXPacket(PacketType.ART_DMX, self.sequence, 0, int(universe),
                                                   tmp_led_strip.to_byte_array()).packet_to_byte_array())
        return True

    def all_off_opcua_call(self, parent):
        from opcua import ua
        ret = self.all_off()
        return [ua.Variant(ret, ua.VariantType.Boolean)]

    def _illuminate_from_to(self, start_led, end_led, led_strip, color):
        """Illuminates leds from start to end with given color and returns a LEDStrip"""
        for i in range(start_led, end_led + 1, 1):
            led_strip.led_strip[i].set_color(color)
        return led_strip

    def _extract_start_end_led(self, slot):
        """Returns start and end led from a given slot"""
        leds = self.slots.get(slot).get('led')
        led_split = leds.split('-')
        start_led = int(led_split[0])
        end_led = int(led_split[1])
        return start_led, end_led

    def _history_builder(self, slot_name, color, history_to_illu):
        """Build history of slots that have to be illuminated"""
        slot = 'slot_' + str(slot_name)
        tmp_slot_history = copy.deepcopy(self.slot_history)
        if slot in tmp_slot_history:
            tmp_slot_history.remove(slot)
        history_to_build = {}
        if len(self.color_history) < self._max_history_size:
            dif = self._max_history_size - len(self.color_history)
            for i in range(dif):
                self.color_history.append('red')

        if len(tmp_slot_history) < history_to_illu:
            history_to_illu = len(tmp_slot_history)
        for i in range(history_to_illu):
            history_to_build[tmp_slot_history[i]] = self.color_history[i]

        if self.slots.get(slot) and Color.colors.get(color):
            history_to_build[slot] = color
        return history_to_build

    def _history_led_strip_builder(self, slot_history):
        """Needs a slot_history dict from _history_builder to build LEDStrips that can be send"""
        led_strip_dict = {}
        for universe in self.universe:
            led_strip_dict[universe] = copy.deepcopy(self.universe.get(universe))
        for slot in slot_history:
            universe = self.slots.get(slot).get('universe')
            if universe not in led_strip_dict.keys():
                led_strip_dict[universe] = copy.deepcopy(self.universe[universe])

            start_led, end_led = self._extract_start_end_led(slot)
            led_strip_dict[universe] = self._illuminate_from_to(start_led, end_led, led_strip_dict[universe],
                                                                slot_history[slot])

        return led_strip_dict

    def _sequenzer(self):
        if self.sequence < 255:
            self.sequence += 1
        else:
            self.sequence = 1
        return self.sequence


class LEDStrip(object):
    def __init__(self, strip_length=1):
        """:param strip_length: default is 1"""
        if strip_length < 0:
            raise ValueError("Strip value has to be 0 or larger")
        self.strip_length = strip_length
        self.led_strip = [Color(0, 0, 0) for _ in range(strip_length)]

    def to_byte_array(self):
        """:return: A byte array with the colors for each LED"""
        led_byte_array = bytearray()

        for color in self.led_strip:
            led_byte_array.append(color.green)
            led_byte_array.append(color.red)
            led_byte_array.append(color.blue)

        return led_byte_array

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.led_strip == other.led_strip:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
