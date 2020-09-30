import pyglet
from pymunk.pyglet_util import DrawOptions
from pyglet.window import mouse, key
from pyglet.gl import *
import pymunk.autogeometry
from population import Population
from track_builder import TrackBuilder, Circle
from car import draw_batch
import config as cfg
from config import TrackSettings


class SimulationWindow(pyglet.window.Window):
    # Environment Variables
    TRACK_MSG = "Press 'left' mouse button to create a mid_track vertices and 'right' button to apply. Vertices: {0}"
    TRACK_EXISTING_MSG = "There is a saved track. Press 's' key to load it or 'r' to create a new one."
    EPOCH_MSG = 'Generation:{0} | Timestep:{1}'
    COUNTER_MSG = 'Time:{0}'
    REMAIN_CARS = 'Time:{0} | Remain {1} from {2} cars | Last Best car ({3} score:{4}) in generation {5} |'
    CURRENT_BEST_CAR = 'Current Best: ({0} score:{1})'
    SCREEN_TITLE = "DeepGA Self Driving Car"

    SCREEN_HEIGHT = cfg.SCREEN_HEIGHT
    SCREEN_WIDTH = cfg.SCREEN_WIDTH
    TRACK_THICKNESS = cfg.TRACK_THICKNESS
    TRACK_VERTEX_RADIUS = cfg.TRACK_VERTEX_RADIUS
    FPS = cfg.FPS  # Frames Per Second (FPS)

    TRACK_READY = False
    EXIST_LAST_TRACK = False
    PAUSE = False
    LOAD_EXISTING_TRACK = False
    PRESSED_RIGHT_BUTTON = False

    EXIST_BEST_MODEL = False
    BEST_MODEL_PATH = None

    # Deep Learning - Genetic Algorithm
    POPULATION_SIZE = cfg.POPULATION_SIZE
    STROKE = cfg.STROKE
    collision_types = {"mid_track": 1, "car": 2}
    track = []
    deep_ga = None
    cars = []
    collided = []
    last_best_car_scores = [None, 0, 0.0]
    best_reward = last_best_car_scores
    time_counter = 0
    time_step_increment = 5
    time_step = time_step_increment * 2  # Seconds
    epoch = 1
    track_background = None

    def __init__(self, width=800, height=600, *args, **kwargs):
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.SCREEN_TITLE, resizable=False, fullscreen=False, *args, **kwargs)
        self.x, self.y = 0, 0

        # Pyglet   #style=pyglet.window.Window.WINDOW_STYLE_TOOL style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.options = DrawOptions()
        # Pymunk
        self.space = pymunk.Space()

        # type float in the range [0.0, 1.0], corresponding to the RGBA sequence (red, green, blue, and alpha).
        self.background_color = (.1, .5, .1, 1)  # green grass
        self.background_color2 = (.2, .75, .5, 1)  # light green grass
        # sets the background color
        glClearColor(*self.background_color)

        # Instances of classes
        self.population = Population()
        self.track_builder = TrackBuilder()
        self.track_settings = TrackSettings()

        self.track_creation_label = pyglet.text.Label(
            self.TRACK_MSG.format(len(self.track)),
            font_name='Times New Roman',
            font_size=20,
            x=self.SCREEN_WIDTH // 2,
            y=self.SCREEN_HEIGHT - 20,
            color=(255, 255, 0, 255),
            anchor_x='center', anchor_y='center')

        self.epoch_label = pyglet.text.Label(
            self.EPOCH_MSG.format(self.epoch, self.time_step),
            font_name='Times New Roman',
            font_size=16,
            x=0.8 * self.SCREEN_WIDTH // 10,
            y=self.SCREEN_HEIGHT - 20,
            color=(255, 255, 255, 255),
            anchor_x='center', anchor_y='center')

        self.best_car_info_label = pyglet.text.Label(
            self.COUNTER_MSG.format(self.time_counter),
            font_name='Times New Roman',
            font_size=16,
            x=4.4 * self.SCREEN_WIDTH // 10,
            y=self.SCREEN_HEIGHT - 20,
            color=(255, 255, 0, 255),
            anchor_x='center', anchor_y='center')

        self.current_best_car_info_label = pyglet.text.Label(
            self.CURRENT_BEST_CAR.format("None", "0"),
            font_name='Times New Roman',
            font_size=16,
            x=8.3 * self.SCREEN_WIDTH // 10,
            y=self.SCREEN_HEIGHT - 20,
            color=(255, 255, 0, 255),
            anchor_x='center', anchor_y='center')

    # Window Events
    def on_draw(self):
        self.clear()
        self.space.debug_draw(self.options)
        draw_batch()

        if self.TRACK_READY:
            if self.epoch_label is not None:
                self.epoch_label.draw()

            if self.best_car_info_label is not None:
                self.best_car_info_label.draw()

            if self.current_best_car_info_label is not None:
                self.current_best_car_info_label.draw()

            if self.track_background is not None:
                self.track_background.draw()
        else:
            if self.PRESSED_RIGHT_BUTTON:
                self.PRESSED_RIGHT_BUTTON = False

            r, g, b = cfg.spring_green
            for i in range(len(self.track)):
                p = self.track[i]
                c = Circle(self.TRACK_VERTEX_RADIUS, r, g, b, p[0], p[1])
                c.draw()

            if self.track_creation_label is not None:
                self.track_creation_label.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()

        if self.EXIST_LAST_TRACK and not self.TRACK_READY:
            if symbol == key.S:
                print('Load existing track')
                self.track.clear()
                self.LOAD_EXISTING_TRACK = True
                self.TRACK_READY = self.load_existing_track()
            elif symbol == key.R:
                print('Create a new  track')
                self.track.clear()
                self.LOAD_EXISTING_TRACK = False
                self.EXIST_LAST_TRACK = False

        if self.TRACK_READY:
            if symbol == pyglet.window.key.SPACE:  # press the SPACE key to pause/start the scheduled function
                if not self.PAUSE:
                    print('Pause the process')
                    pyglet.clock.unschedule(self.update)
                else:
                    print('Restart the process')
                    pyglet.clock.schedule(self.update)

                self.PAUSE = not self.PAUSE

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.TRACK_READY and not self.LOAD_EXISTING_TRACK and not self.EXIST_LAST_TRACK:
            if button == mouse.LEFT:
                x = int(x)
                y = int(y)
                self.track.append([x, y])
            elif button == mouse.RIGHT:
                try:
                    self.deep_ga, self.cars = self.generate_track_and_population(
                        self.track,
                        self.TRACK_VERTEX_RADIUS,
                        self.POPULATION_SIZE,
                        self.collision_types["mid_track"],
                        is_new_track=True)
                    self.PRESSED_RIGHT_BUTTON = True
                    self.TRACK_READY = True
                except Exception as e:
                    print('Exception', e)

    def generate_track_and_population(self, track, radius, population_size, collision_type, is_new_track):
        final_track, first_vertex, max_reward = self.track_builder.generate_closed_track(self.space, track, radius,
                                                                                         collision_type, is_new_track)
        exist_best_model, best_model_path, start_rng, other_rng = self.verify_best_model_path()
        return self.population.generate_population(self.space, final_track, first_vertex, population_size,
                                                   collision_type,
                                                   start_rng,
                                                   other_rng,
                                                   best_model_path=best_model_path)

    def verify_existing_track(self):
        existing_track = None
        if not self.TRACK_READY and not self.EXIST_LAST_TRACK:
            existing_track = self.track_builder.check_track_exists()

        if existing_track is None or not existing_track:
            self.EXIST_LAST_TRACK = False
        else:
            self.EXIST_LAST_TRACK = True

    def verify_best_model_path(self):
        exist_best_model = False
        start_rng, other_rng = None, None
        model_path = self.track_settings.load_best_model_path()

        if model_path is not None:
            start_rng, other_rng = self.track_settings.load_compress_model_data()
            exist_best_model = True

        return exist_best_model, model_path, start_rng, other_rng

    def load_existing_track(self):
        is_loaded = False
        existing_track = self.track_builder.create_track_if_exists()

        if existing_track is not None:
            is_loaded = True
            self.deep_ga, self.cars = self.generate_track_and_population(existing_track, self.TRACK_VERTEX_RADIUS,
                                                                         self.POPULATION_SIZE,
                                                                         self.collision_types["mid_track"],
                                                                         is_new_track=False)
        return is_loaded

    def verify_collided_cars(self, collided_cars, cars_list):
        for i in range(len(cars_list)):
            if cars_list[i].car_collided is False:
                cars_list[i].drive()
            elif i not in collided_cars:
                collided_cars.append(i)

    def process_cars(self, dt):
        self.time_counter += 1
        self.space.step(dt)

        self.verify_collided_cars(self.collided, self.cars)

        time_step_limit = self.FPS * self.time_step
        remain_cars = self.POPULATION_SIZE - len(self.collided)

        if self.time_counter >= time_step_limit or remain_cars == 0:
            if self.epoch % self.time_step_increment == 0:
                self.time_step += self.time_step_increment

            truncation = len(self.cars)
            if truncation > 1:
                truncation = int(truncation * 0.25)

            scores, best_car, best_model_path, best_model = self.deep_ga.evolve_population(
                self.cars,
                truncation=truncation,
                best_model_path=(cfg.BEST_MODEL_REPO, self.epoch))
            epoch_best_score = scores[2]
            epoch_best_car_scores = [best_car.name, self.epoch, epoch_best_score]

            score_txt = "{0:0.2f}".format(epoch_best_score) if epoch_best_score is not None else "0"
            print("\n=============================================================================")
            print("Generation:", self.epoch, ", Best car:", best_car.name, " with the reward score:" + score_txt)

            self.population.move_cars(self.cars, self.deep_ga, None, None, None)
            self.population.reset_cars(self.cars)

            self.time_counter = 0
            self.collided = []
            self.epoch += 1
            self.epoch_label.text = self.EPOCH_MSG.format(self.epoch, self.time_step)
            self.last_best_car_scores = epoch_best_car_scores

            if epoch_best_car_scores[0] is not None and epoch_best_car_scores[2] > self.best_reward[2]:
                self.best_reward = epoch_best_car_scores
                if best_model_path is not None:
                    self.track_settings.save_best_model_path(best_model_path, self.best_reward[0], self.best_reward[2], best_model)

            last_score_txt = "{0:0.2f}".format(self.last_best_car_scores[2]) if self.last_best_car_scores[2] is not None else "0"
            car_name = self.last_best_car_scores[0]
        else:
            scored_models, best_score, best_model, best_car = self.deep_ga.select_best_models(self.cars)
            # print("best_score=", best_score, ", car=", best_car.name)
            last_score_txt = "{0:0.2f}".format(best_score) if best_score is not None else "0"
            car_name = best_car.name

        score_txt = "{0:0.2f}".format(self.best_reward[2]) if self.best_reward[2] is not None else "0"
        self.best_car_info_label.text = self.REMAIN_CARS.format(str(self.time_counter // self.FPS + 1),
                                                                remain_cars,
                                                                self.POPULATION_SIZE,
                                                                self.best_reward[0],
                                                                score_txt,
                                                                self.best_reward[1])

        self.current_best_car_info_label.text = self.CURRENT_BEST_CAR.format(car_name, last_score_txt)

    # Update Function
    def update(self, dt):
        if not self.TRACK_READY and self.EXIST_LAST_TRACK and not self.LOAD_EXISTING_TRACK:
            self.track_creation_label.text = self.TRACK_EXISTING_MSG
            return

        if self.TRACK_READY:
            self.process_cars(dt)
        else:
            self.track_creation_label.text = self.TRACK_MSG.format(len(self.track))


# Main function
if __name__ == '__main__':
    win = SimulationWindow()
    win.verify_existing_track()

    # schedule: change the background color every 1 second
    pyglet.clock.schedule_interval(win.update, 1.0 / win.FPS)
    #pyglet.clock.unschedule(win.update)
    pyglet.app.run()
