import pymunk
from pymunk import Vec2d
from math import cos, sin, radians
from shapely.geometry.polygon import LinearRing
from pyglet.gl import *
import pymunk.autogeometry
from config import *
from file_manager import FileManager, PointConverter

class TrackBuilder:
    def __init__(self):
        self.converter = PointConverter()
        self.file_manager = FileManager()
        self.cfg = TrackSettings()

    def prepare_segments(self, track):
        points = []
        if len(track) > 1:
            for i in range(len(track)):
                point = track[i]
                points.append(point)
        return points

    def add_segments(self, space, points, stroke, collision_type):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        environment = []

        if len(points) > 1:
            for i in range(len(points)):
                point = points[i]
                segment = pymunk.Segment(body, point[0], point[1], stroke)
                segment.collision_type = collision_type
                environment.append(segment)

            space.add(body, environment)

        return environment

    def create_track_segments(self, space, internal_track, offset_track, collision_type):
        internal = self.create_segments(space, internal_track, collision_type)
        external = self.create_segments(space, offset_track, collision_type)
        closed_track = [*internal, *external]
        return closed_track

    def generate_offset_track(self, mid_track, thickness):
        poly_line = LinearRing(mid_track)
        poly_line_offset_left = poly_line.parallel_offset(thickness, side="left", resolution=16, join_style=2, mitre_limit=2)
        poly_line_offset_right = poly_line.parallel_offset(thickness, side="right", resolution=16, join_style=2, mitre_limit=2)

        offset_left_track = []
        for coord in poly_line_offset_left.coords:
            p = [coord[0], coord[1]]
            offset_left_track.append(p)
        offset_left_track.append(offset_left_track[0])

        offset_right_track = []
        for coord in poly_line_offset_right.coords:
            p = [coord[0], coord[1]]
            offset_right_track.append(p)
        offset_right_track.append(offset_right_track[0])

        return offset_left_track, offset_right_track

    def generate_closed_track(self, space, mid_track, radius, collision_type, is_new_track):
        first_vertex = mid_track[0]

        if is_new_track:
            # To close the polygon ths represents the internal mid_track
            mid_track.append(first_vertex)
            self.cfg.save_track(mid_track)

        offset_left_track, offset_right_track = self.generate_offset_track(mid_track, radius)
        final_track = self.create_track_segments(space, offset_right_track, offset_left_track, collision_type)

        # Calculate the distance of the middle track
        max_dist = self.average_track_distance(mid_track)

        return final_track, first_vertex, max_dist

    def create_segments(self, space, track, collision_type):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        track_segments = []

        if len(track) > 1:
            color = dark_orange

            for i in range(len(track) - 1):
                p1 = track[i]
                p2 = track[i+1]
                segment = pymunk.Segment(body, p1, p2, 0.0)
                segment.collision_type = collision_type
                segment.color = color
                track_segments.append(segment)

            space.add(body, track_segments)

        return track_segments

    def average_track_distance(self, mid_track):
        dist = 0

        if len(mid_track) > 1:
            for i in range(len(mid_track) - 1):
                p1 = mid_track[i]
                p2 = mid_track[i + 1]
                current_pos = Vec2d(p1)
                initial_pos = Vec2d(p2)
                dist += (current_pos - initial_pos).length

        return dist

    def load_from_file(self, filename):
        ''' Load Track from file '''
        track = []
        lines = self.file_manager.track_from_file(filename)

        # Steps in loop below are similar to steps above.
        for line in lines:
            # Convert to list of floats
            vertex = self.converter.string_to_float(line)

            track.append(vertex)

    def save_to_file(self, filename, track):
        ''' Save a Track to a file  '''
        self.file_manager.clear_file(filename)

        for point in track:
            str_pt = self.converter.integer_to_string(point)
            self.file_manager.add_point_to_track(str_pt, filename)

    def create_track_if_exists(self):
        if self.cfg.exist_track():
            mid_track = self.cfg.load_track()
            if mid_track is not None:
                return mid_track
        return None

    def check_track_exists(self):
        return self.cfg.exist_track()

    def rotate_point_around_other(self, x_1, y_1, x_2, y_2, angle_radians, h):
        # Rotate the point2 by angle in radians around the point1
        x_change = (x_2 - x_1) * cos(angle_radians) + (y_2 - y_1) * sin(angle_radians)
        y_change = (y_1 - y_2) * cos(angle_radians) - (x_1 - x_2) * sin(angle_radians)
        rotated_x = x_change + x_1
        rotated_y = h - (y_change + y_1)

        return int(rotated_x), int(rotated_y)

    def line_intersection(self, line1, line2):
        x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(x_diff, y_diff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, x_diff) / div
        y = det(d, y_diff) / div

        return Vec2d(x, y)

class Track:
    def __init__(self, track, r, g, b, thickness=50, x=0, y=0):
        self.r = r/255
        self.g = g/255
        self.b = b/255
        self.x = x
        self.y = y
        self.thickness = thickness

        size = len(track)
        verts = []
        for point in track:
            verts.append(point[0])
            verts.append(point[1])

        print(verts)
        self.vlist = pyglet.graphics.vertex_list(size, ('v2f', verts))

    def draw(self):
        glColor3f(self.r, self.g, self.b)
        #pyglet.gl.glLineWidth(self.thickness)
        self.vlist.draw(pyglet.gl.GL_LINE_LOOP)

class Circle:
    def __init__(self, radius, r, g, b, x=0, y=0):
        self.r = r/255
        self.g = g/255
        self.b = b/255
        self.x = x
        self.y = y
        self.size = 1
        verts = [0, 0]

        for angle in range(0, 370, 10):
            x = int(radius * cos(radians(angle)))
            y = int(radius * sin(radians(angle)))
            verts = verts + [x, y]

        self.vlist = pyglet.graphics.vertex_list(int(len(verts) / 2), ('v2f', verts))

    def draw(self):
        glColor3f(self.r, self.g, self.b)
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScalef(self.size, self.size, self.size)
        self.vlist.draw(GL_TRIANGLE_FAN)
        glPopMatrix()

