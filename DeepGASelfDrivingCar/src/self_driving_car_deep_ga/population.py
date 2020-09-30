import copy
import pyglet
from deep_ga import DeepGA
from car import Car
from config import VEHICLE_FILE_NAMES, IMAGE_REPO
import random

# Resource paths
pyglet.resource.path = [IMAGE_REPO]
pyglet.resource.reindex()

class Population:
    def __init__(self):
        self.VEHICLE_FILE_NAMES = VEHICLE_FILE_NAMES
        random.shuffle(self.VEHICLE_FILE_NAMES)
        self.VEHICLE_IMAGES = []
        self.VEHICLE_NAMES = []

    def center_image(self, image):
        """Sets an image's anchor point to its center"""
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2

    def load_vehicle_images(self, population_size, vehicle_file_names):
        vehicle_names = []
        vehicle_images = []

        for file_name in vehicle_file_names:
            # get images
            img = pyglet.resource.image(file_name)
            self.center_image(img)
            self.VEHICLE_IMAGES.append(img)
            name = file_name.split('.')
            vehicle_names.append(name[0])
            vehicle_images.append(img)

            if len(vehicle_names) == population_size:
                break;

        return vehicle_images, vehicle_names

    def suit_car_image_quantity(self, population_size, vehicle_file_names):
        vehicle_images, vehicle_names = self.load_vehicle_images(population_size, vehicle_file_names)
        number_of_images = len(vehicle_images)
        loop = True
        max_index = len(vehicle_file_names)

        # In case of the number of images be smaller than the population size
        if population_size > number_of_images:
            while loop:
                index = 0

                for img in self.VEHICLE_IMAGES:
                    vehicle_images.append(img)
                    name = vehicle_names[index]
                    vehicle_names.append(name)

                    index += 1
                    if max_index == index:
                        index = 0

                    if population_size == len(vehicle_images):
                        loop = False
                        break

        return vehicle_images, vehicle_names

    def generate_population(self, space, final_track, first_vertex, population_size, track_collision_type, start_rng, other_rng, best_model_path=None):
        # Adapt the number of car images according to the population size
        vehicle_images, vehicle_names = self.suit_car_image_quantity(population_size, self.VEHICLE_FILE_NAMES)
        # Create a instance of GA with model defaults
        deep_ga = DeepGA(population_size)

        # Create the car population with the own model for each one
        cars = [Car(space,
                    first_vertex[0],
                    first_vertex[1],
                    i + 10,
                    track_collision_type,
                    final_track,
                    vehicle_images[i],
                    vehicle_names[i],
                    i) for i in range(population_size)]

        self.move_cars(cars, deep_ga, start_rng, other_rng, best_model_path)
        return deep_ga, cars

    def move_cars(self, cars, deep_ga, start_rng, other_rng, best_model_path):
        best_model = None
        if best_model_path is not None:
            best_model = deep_ga.load_model(best_model_path)

        #random.shuffle(cars)
        for i, (car, model) in enumerate(zip(cars, deep_ga.models)):
            #print("Move car=", car.name, ", index=", car.index)
            if best_model is None:
                unc_model = model.uncompress_model()
            else:
                unc_model = model.recover_model(best_model, start_rng, other_rng, i)

            car.update_brain(unc_model)

    def reset_cars(self, cars):
        for car in cars:
            car.reset()
