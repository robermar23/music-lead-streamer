
class ColorSoundMapper:
    def __init__(self, frequency_hz, wavelength_cm, notes, frequency_thz, wavelength_nm, red_dec_hex, green_dec_hex, blue_dec_hex, cyan_dec, magenta_dec, yellow_dec, hue_hsb, saturation_hsb, brightness_hsb):
        self.frequency_hz = frequency_hz
        self.wavelength_cm = wavelength_cm
        self.notes = notes
        self.frequency_thz = frequency_thz
        self.wavelength_nm = wavelength_nm
        self.red_dec_hex = red_dec_hex
        self.green_dec_hex = green_dec_hex
        self.blue_dec_hex = blue_dec_hex
        self.cyan_dec = cyan_dec
        self.magenta_dec = magenta_dec
        self.yellow_dec = yellow_dec
        self.hue_hsb = hue_hsb
        self.saturation_hsb = saturation_hsb
        self.brightness_hsb = brightness_hsb
      
    def get_rgb(self):
        return (self.red_dec_hex, self.green_dec_hex, self.blue_dec_hex)

    @classmethod
    def create_instances(cls):
        """
        Creates a hard-coded collection of ColorSoundMapper instances.  Based off of [Klotsche 2012] Charles Klotsche. Color Medicine, published by Light Technology Publishing, May 21, 2012
        https://www.flutopedia.com/sound_color.htm
        :return: List of ColorSoundMapper instances.
        """
        return [
            cls(349.2, 98.88, "F₄", 384.0, 780.8, 82, 0, 0, 173, 255, 255, 0, 100, 32),
            cls(370.0, 93.33, "F#₄/G♭₄", 406.8, 736.9, 116, 0, 0, 139, 255, 255, 0, 100, 45),
            cls(392.0, 88.09, "G₄", 431.0, 695.6, 179, 0, 0, 76, 255, 255, 0, 100, 70),
            cls(415.3, 83.15, "G#₄/Ab₄", 456.6, 656.5, 238, 0, 0, 17, 255, 255, 0, 100, 93),
            cls(440.0, 78.48, "A₄", 483.8, 619.7, 255, 99, 0, 0, 156, 255, 23, 100, 100),
            cls(466.2, 74.07, "A#₄/Bb₄", 512.5, 584.9, 255, 236, 0, 0, 19, 255, 56, 100, 100),
            cls(493.9, 69.92, "B₄", 543.0, 552.1, 153, 255, 0, 102, 0, 255, 84, 100, 100),
            cls(523.2, 65.99, "C₅", 575.3, 521.1, 40, 255, 0, 215, 0, 255, 111, 100, 100),
            cls(554.4, 62.29, "C#₅/Db₅", 609.5, 491.8, 0, 255, 232, 255, 0, 23, 175, 100, 100),
            cls(587.3, 58.79, "D₅", 645.8, 464.2, 0, 124, 255, 255, 131, 0, 211, 100, 100),
            cls(622.2, 55.49, "D#₅/Eb₅", 684.2, 438.2, 5, 0, 255, 250, 255, 0, 241, 100, 100),
            cls(659.3, 52.38, "E₅", 724.9, 413.6, 69, 0, 234, 186, 255, 21, 258, 100, 92),
            cls(698.5, 49.44, "F₅", 768.0, 390.4, 87, 0, 158, 168, 255, 97, 273, 100, 62)
        ]

    @classmethod
    def find_by_frequency(cls, instances, frequency_hz):
        """
        Finds and returns the instance where the frequency falls within the range.
        Assumes the list is sorted by frequency_hz.
        :param frequency_hz: Frequency in Hz to match.
        :return: ColorSoundMapper instance or None if no match is found.
        """
        for i in range(len(instances) - 1):
            if instances[i].frequency_hz <= frequency_hz < instances[i + 1].frequency_hz:
                return instances[i]
        # If it matches the last instance's frequency
        if instances and frequency_hz >= instances[-1].frequency_hz:
            return instances[-1]
        return None

# Example usage:
# color_sound_instances = ColorSoundMapper.create_instances()
# for instance in color_sound_instances:
#     print(instance.__dict__)
# 
# match = ColorSoundMapper.find_by_frequency(440.0)
# if match:
#     print(match.__dict__)
