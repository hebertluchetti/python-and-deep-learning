import pymunk
from pymunk import Vec2d
import torch
import pyglet
from math import pi, degrees
from pyglet.sprite import Sprite
from config import color, yellow, cyan

sensor_color = yellow
sensor_collision_types = {"sensorLeft": 3, "sensorLeftMid": 4, "sensorFront": 5, "sensorRightMid": 6, "sensorRight": 7}
batch = pyglet.graphics.Batch()

def draw_batch():
    batch.draw()

class Car:
    def __init__(self, space, x, y, body_number, track_collision_type, track, vehicle_img, name, index):
        self.name = name + str(index + 1)
        self.index = index
        self.track_collision_type = track_collision_type

        # Space
        self.space = space
        self.track = track
        self.vehicle_img = vehicle_img

        # Car Properties
        self.init_position = x, y
        self.init_angle = 0
        self.car_size = 8
        self.car_dimension = 40, 18
        self.car_color = color[0]
        self.car_elasticity = 0
        self.car_sonar_size = self.car_size / 2

        # Car sensors
        self.sensors = []
        self.sensor_range = 100
        self.sensor_distance = [self.sensor_range for _ in range(5)]
        self.sensor_angles = [0, pi / 6, -pi / 6, pi / 3, -pi / 3]
        self.sensor_visible = True

        # Reward properties
        self.reward_val = 0

        # Total coverd distance
        self.distance = 0
        self.last_pos = self.init_position

        # Collision properties
        self.body_collision_type = body_number
        self.car_collided = False
        self.sensor_collision_types = [sensor_collision_types["sensorLeft"],
                                       sensor_collision_types["sensorLeftMid"],
                                       sensor_collision_types["sensorFront"],
                                       sensor_collision_types["sensorRightMid"],
                                       sensor_collision_types["sensorRight"]
                                       ]

        # Create
        self.create()

        for distance, angle, collision_type in zip(self.sensor_distance, self.sensor_angles, self.sensor_collision_types):
            self.create_sensor(distance, angle, collision_type)

        self.create_sonar()
        self.add_body_collision_handler()
        self.sensor_collision_detection()

        # Brain brain
        self.brain = None

    def draw_car_sprite(self):
        self.car_sprite.draw()

    def create_car_sprite(self, body, shape, img, x, y, batch, scale=0.25):
        # Car image
        self.car_sprite = Sprite(img=img, x=x, y=y, batch=batch)
        self.car_sprite.shape = shape
        self.car_sprite.body = body
        self.car_sprite.scale = scale
        self.car_sprite.rotation = degrees(-self.car_sprite.body.angle) + 90

    def update_car_sprite(self, angle, max_angle=pi / 36):
        self.car_sprite.rotation = degrees(-self.car_sprite.body.angle) + min(angle, max_angle) + 90
        self.car_sprite.x = self.car_body.position.x
        self.car_sprite.y = self.car_body.position.y

    def reset_car_sprite(self, x, y):
        self.car_sprite.x = x
        self.car_sprite.y = y
        self.car_sprite.rotation = degrees(pi)

    def create(self):
        inertia = pymunk.moment_for_box(self.car_size, self.car_dimension)
        self.car_body = pymunk.Body(self.car_size, inertia, body_type=pymunk.Body.KINEMATIC)
        self.car_body.position = self.init_position
        self.car_shape = pymunk.Poly.create_box(self.car_body, self.car_dimension)

        self.car_shape.collision_type = self.body_collision_type
        self.car_shape.color = self.car_color
        self.car_shape.elasticity = self.car_elasticity
        self.car_body.angle = self.init_angle

        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse_at_local_point(driving_direction)

        self.space.add(self.car_body, self.car_shape)

        self.create_car_sprite(self.car_body,
                               self.car_shape,
                               self.vehicle_img,
                               self.car_body.position.x,
                               self.car_body.position.y,
                               batch)

    def move(self, force, max_force=5):
        direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.position += min(force, max_force) * direction
        self.update_sensor()
        self.update_sonar()

    def rotate(self, angle, max_angle=pi / 36):
        self.car_body.angle += min(angle, max_angle)
        self.update_sensor()
        self.update_sonar()

    def get_car_contour_vertices(self):
        vertices = []
        for v in self.car_shape.get_vertices():
            vertex = v.rotated(self.car_body.angle) + self.car_body.position
            vertices.append(vertex)
        return vertices

    def create_sensor(self, distance, angle, collision_type):
        sensor_direction = Vec2d(1, 0).rotated(self.car_body.angle + angle)
        sensor_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        vertices = self.get_car_contour_vertices()
        sensor_body.position = (vertices[1] + vertices[0]) / 2
        start_point = (0, 0)
        end_point = distance * sensor_direction

        if self.sensor_visible is True:
            sensor_shape = pymunk.Segment(sensor_body, start_point, end_point, 0.0)
            sensor_shape.collision_type = collision_type
            sensor_shape.color = sensor_color
            self.space.add(sensor_body, sensor_shape)
            self.sensors.append([sensor_body, sensor_shape])
        else:
            self.space.add(sensor_body)
            self.sensors.append([sensor_body, None])

    def update_sensor(self):
        self.sensor_collision_detection()

        for i in range(len(self.sensors)):
            vertex = self.get_car_contour_vertices()
            self.sensors[i][0].position = (vertex[1] + vertex[0]) / 2
            sensor_direction = Vec2d(1, 0).rotated(self.car_body.angle + self.sensor_angles[i])

            if self.sensor_visible is True:
                self.sensors[i][1].unsafe_set_endpoints((0, 0), self.sensor_distance[i] * sensor_direction)

    def create_sonar(self):
        self.sonar_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        vertex = self.get_car_contour_vertices()
        offset = Vec2d(5, 0).rotated(self.car_body.angle)
        self.sonar_body.position = (vertex[1] + vertex[0]) / 2 - offset

        self.sonar_shape = pymunk.Circle(self.sonar_body, self.car_sonar_size)
        self.sonar_shape.collision_type = self.body_collision_type
        self.sonar_shape.color = cyan

        self.space.add(self.sonar_shape, self.sonar_body)

    def update_sonar(self):
        vertex = self.get_car_contour_vertices()
        offset = Vec2d(5, 0).rotated(self.car_body.angle)
        self.sonar_body.position = (vertex[1] + vertex[0]) / 2 - offset

    def add_body_collision_handler(self):
        self.body_handler = self.space.add_collision_handler(self.track_collision_type, self.body_collision_type)
        self.body_handler.data["car_collision"] = self.set_car_collision
        self.body_handler.begin = self.begin_body_collision

    def set_car_collision(self):
        self.car_collided = True

    def begin_body_collision(self, arbiter, space, data):
        data["car_collision"]()
        return True

    def sensor_collision_detection(self):
        for i, sensor in enumerate(self.sensors):
            if i != -1:
                sensor_is_touching = False
                vertex = self.get_car_contour_vertices()
                sensor_origin = (vertex[1] + vertex[0]) / 2
                sensor_direction = Vec2d(1, 0).rotated(self.car_body.angle + self.sensor_angles[i])
                sensor_end_point = self.sensor_range * sensor_direction

                for segments in self.track:
                    sensor_contact = segments.segment_query(sensor_origin, sensor_end_point + sensor[0].position)

                    if sensor_contact.shape is not None:
                        self.set_sensor_distance(i, min((sensor_origin - sensor_contact.point).length, self.sensor_range))
                        sensor_is_touching = True

                if sensor_is_touching is False:
                    self.set_sensor_distance(i, self.sensor_range)

    def set_sensor_distance(self, index, distance):
        self.sensor_distance[index] = distance

    def update_brain(self, model):
        self.brain = model

    def drive(self):
        force, angle = self.brain(torch.Tensor(self.sensor_distance))
        self.move(force.item() * 5)
        self.rotate(angle.item() / 5)
        self.update_reward()
        self.update_car_sprite(angle.item() / 5)

    # def reward(self):
    #     current_pos = Vec2d(self.car_body.position)
    #     initial_pos = Vec2d(self.init_position)
    #     #rewards = (current_pos - initial_pos).length
    #     rewards = current_pos.get_dist_sqrd(initial_pos)
    #     return rewards

    def reward(self):
        current_pos = Vec2d(self.car_body.position)
        last_pos = Vec2d(self.last_pos)
        distance = current_pos.get_dist_sqrd(last_pos)

        if distance > 0.0:
            self.distance = self.distance + distance
            self.last_pos = self.car_body.position
        #     print("Car:", self.name, "distance=", distance, " self.distance=", self.distance)
        # else:
        #     print("Car:", self.name, "Parado", " self.distance=", self.distance)

        return self.distance

    def reset(self):
        self.car_body.position = self.init_position
        self.last_pos = self.init_position
        self.distance = 0
        self.car_body.angle = 0
        vertex = self.get_car_contour_vertices()
        self.car_collided = False
        offset = Vec2d(5, 0).rotated(self.car_body.angle)
        self.sonar_body.position = (vertex[1] + vertex[0]) / 2 - offset
        self.sensor_distance = [self.sensor_range for _ in range(5)]

        self.reset_car_sprite(self.car_body.position.x, self.car_body.position.y)

        for i in range(len(self.sensors)):
            self.sensors[i][0].position = (vertex[1] + vertex[0]) / 2
            sensor_direction = Vec2d(1, 0).rotated(self.car_body.angle + self.sensor_angles[i])

            if self.sensor_visible is True:
                self.sensors[i][1].unsafe_set_endpoints((0, 0), self.sensor_distance[i] * sensor_direction)

    def update_reward(self):
        reward = self.reward()
        if reward > self.reward_val:
            self.reward_val = reward

