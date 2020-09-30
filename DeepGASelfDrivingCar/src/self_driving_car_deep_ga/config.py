# System Modules
from backports import configparser
from file_manager import PointConverter
import os

color = [(231, 76, 60), (142, 68, 173), (52, 152, 219),
         (22, 160, 133), (241, 196, 15), (211, 84, 0),
         (81, 90, 90), (100, 30, 22), (125, 102, 8),
         (26, 82, 118)]

dark_orange = (255, 140, 0)
yellow = (0, 255, 255)
spring_green = (0, 255, 127)
cyan = (0, 255, 255)

TRACK_FILE_DIR = "." + os.sep + "track_path"
BEST_MODEL_REPO = "." + os.sep + "best_model"
IMAGE_REPO = "." + os.sep + "images"

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1600
TRACK_THICKNESS = 60
TRACK_VERTEX_RADIUS = TRACK_THICKNESS / 2
STROKE = 1
FPS = 60  #Frames Per Second (FPS)
POPULATION_SIZE = 10

VEHICLE_FILE_NAMES = ["Ambulance.png",
             "Audi.png",
             "Viper.png",
             "Dodge.png",
             "Truck.png",
             "Van.png",
             "Police.png",
             "Taxi.png",
             "Escort.png",
             "SUV.png"]

class TrackSettings:
    path_key = "path"
    best_car_key = "best_car"
    best_score_key = "best_score"
    start_rng_key = "start_rng"
    other_rng_key = "other_rng"
    enabled_key = "enabled"

    def __init__(self):
        self.TRACK_FILE_INI = "track.ini"
        self.SETTINGS_SECTION = "SETTINGS"
        self.TRACK_SECTION = "TRACK"

        self.BEST_MODEL_FILE_INI = "best_model.ini"
        self.BEST_MODEL_SECTION = "BEST_MODEL"

        self.TRACK_DATA_DIR = "track_data"
        self.TRACK_DATA_FILE_DIR = "."+os.sep+self.TRACK_DATA_DIR

        self.converter = PointConverter()

        self.ini_cfg_track = configparser.RawConfigParser()
        self.ini_track_file = self.TRACK_DATA_FILE_DIR + os.sep + self.TRACK_FILE_INI

        self.ini_cfg_best = configparser.RawConfigParser()
        self.ini_best_file = self.TRACK_DATA_FILE_DIR + os.sep + self.BEST_MODEL_FILE_INI

        self.make_dir(self.TRACK_DATA_FILE_DIR)

        if not self.exist_ini(self.ini_cfg_track, self.ini_track_file):
            self.add_settings_section(self.ini_cfg_track, self.ini_track_file)

        if not self.exist_ini(self.ini_cfg_best, self.ini_best_file):
            self.add_best_model_section(self.ini_cfg_best, self.ini_best_file)

    def make_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def exist_ini(self, config, ini_file):
        read_files = config.read(ini_file)
        return len(read_files) > 0

    def add_settings_section(self, config, ini_file):
        self.defaults(config)
        with open(ini_file, 'w') as configfile:
            config.write(configfile)

    def add_best_model_section(self, config, ini_file):
        self.best_model_defaults(config)
        with open(ini_file, 'w') as configfile:
            config.write(configfile)

    def exist_section(self, config, section):
        return config.has_section(section)

    def save_track(self, track):
        self.save_track_section(self.ini_cfg_track, track, self.ini_track_file)

    def save_track_section(self, config, track, ini_file):
        if self.exist_section(config, self.TRACK_SECTION):
            config.remove_section(self.TRACK_SECTION)

        config.add_section(self.TRACK_SECTION)

        index = 0
        for point in track:
            vertex = self.converter.integer_to_string(point)
            index += 1
            key = "vertex"+str(index)
            config.set(self.TRACK_SECTION, key, vertex)

        with open(ini_file, 'w') as configfile:
            config.write(configfile)

    def exist_track(self):
        result = False
        if self.exist_section(self.ini_cfg_track, self.TRACK_SECTION):
            vertices = self.ini_cfg_track.items(self.TRACK_SECTION)
            result = len(vertices) > 0
        return result

    def load_track_section(self, config):
        mid_track = None
        if self.exist_section(config, self.TRACK_SECTION):
            mid_track = []
            vertices = config.items(self.TRACK_SECTION)

            for item in vertices:
                vertex = self.converter.string_to_integer(item[1])
                mid_track.append(vertex)

        return mid_track

    def load_track(self):
        ''' Load Track from file '''
        return self.load_track_section(self.ini_cfg_track)

    def save_best_model_path(self, best_model_path, best_car_name, best_score, compressed_model):
        config = self.ini_cfg_best

        if not self.exist_section(config, self.BEST_MODEL_SECTION):
            config.add_section(self.BEST_MODEL_SECTION)

        str_other_rng = None
        for sigma, rng in compressed_model.other_rng:
            item = str(sigma) + "," + str(rng)

            if str_other_rng is None:
                str_other_rng = item
            else:
                str_other_rng = str_other_rng + " " + item

        config.set(self.BEST_MODEL_SECTION, self.path_key, best_model_path)
        config.set(self.BEST_MODEL_SECTION, self.start_rng_key, compressed_model.start_rng)
        config.set(self.BEST_MODEL_SECTION, self.other_rng_key, str_other_rng)
        config.set(self.BEST_MODEL_SECTION, self.best_car_key, best_car_name)
        config.set(self.BEST_MODEL_SECTION, self.best_score_key, best_score)

        config.write(open(self.ini_best_file, 'w'))

    def load_best_model_path(self):
        config = self.ini_cfg_best
        path = None

        if self.exist_section(config, self.BEST_MODEL_SECTION):
            enabled = config[self.BEST_MODEL_SECTION].getboolean(self.enabled_key, False)

            if enabled:
                model_path = config.get(self.BEST_MODEL_SECTION, self.path_key)
                model_path = model_path.strip(" ")

                if len(model_path) > 0:
                    path = model_path
        return path

    def load_compress_model_data(self):
        start_rng = None
        other_rng = None
        config = self.ini_cfg_best

        if self.exist_section(config, self.BEST_MODEL_SECTION):
            start_r = config.get(self.BEST_MODEL_SECTION, self.start_rng_key)
            other_r = config.get(self.BEST_MODEL_SECTION, self.other_rng_key)

            start_r = start_r.strip(" ")
            if len(start_r) > 0:
                start_rng = int(start_r)

            other_rng = []
            tokens = other_r.split()

            if len(tokens) > 0:
                for token in tokens:
                    items = token.split(",")

                    if len(items) > 0:
                        sigma = float(items[0])
                        reward = int(items[1])
                        other_rng.append((sigma, reward))

        return start_rng, other_rng

    def best_model_defaults(self, config):
        config.add_section(self.BEST_MODEL_SECTION)
        config.set(self.BEST_MODEL_SECTION, self.path_key, "")
        config.set(self.BEST_MODEL_SECTION, self.start_rng_key, "")
        config.set(self.BEST_MODEL_SECTION, self.other_rng_key, "")
        config.set(self.BEST_MODEL_SECTION, self.best_car_key, "")
        config.set(self.BEST_MODEL_SECTION, self.best_score_key, 0)
        config.set(self.BEST_MODEL_SECTION, self.enabled_key, True)

    def defaults(self, config):
        config.add_section(self.SETTINGS_SECTION)
        config.set(self.SETTINGS_SECTION, "thickness", str(TRACK_THICKNESS))
        config.set(self.SETTINGS_SECTION, "vertex_radius", str(TRACK_VERTEX_RADIUS))
        config.set(self.SETTINGS_SECTION, "stroke", str(STROKE))

        config.add_section("WINDOW")
        config.set("WINDOW", "width", SCREEN_WIDTH)
        config.set("WINDOW", "height", SCREEN_HEIGHT)

        config.add_section("CAMERA")
        config.set("CAMERA", "zoom", 10.0)

        config.add_section("SIMULATION")
        config.set("SIMULATION", "interval", 1 / FPS)

        config.write(open(self.ini_track_file, 'w'))
