import numpy as np


class Cyclist:
    g = 9.81  # gravitational acceleration in m/s^2
    
    def __init__(
            self, 
            power_output=150, 
            weight=70, 
            bike_weight=10, 
            drive_train_loss=0.02,
            area=0.509,
            air_density=1.22601,
            cda=0.4,
            coef_rolling_resistance=0.005,
            max_speed=45,
            min_speed=10,
            corner_time_penalty=5,
            corner_coef_a=5,
            corner_coef_b=2.5 * np.pi
            ):
        self.power_output = power_output  # in watts
        self.weight = weight  # in kg
        self.bike_weight = bike_weight  # in kg

        self.drive_train_loss = drive_train_loss
        self.area = area
        self.air_density = air_density
        self.cda = cda
        self.coef_rolling_resistance = coef_rolling_resistance
        self.max_speed = max_speed / 3.6
        self.min_speed = min_speed / 3.6
        self.corner_time_penalty = corner_time_penalty
        self.corner_coef_a = corner_coef_a
        self.corner_coef_b = corner_coef_b

    @property
    def total_weight(self):
        return self.weight + self.bike_weight

    @property
    def lat_ix(self):
        return 1

    @property
    def lon_ix(self):
        return 0
    
    @property
    def ele_ix(self):
        return 2

    def distance_from_xy(self, p1, p2):
        # distance in meters between two points in xy coordinates
        return np.linalg.norm(p2[..., :-1] - p1[..., :-1], axis=-1)
    

    def approximate_distance_from_latlon(self, p1, p2):
        # approximate distance in meters between two lat/lon points
        # using equirectangular approximation, which is ok for short distances (>1% for NZ under 10km)

        R = 6371000  # radius of Earth in meters
        x = np.radians(p2[..., self.lon_ix] - p1[..., self.lon_ix]) * np.cos(np.radians((p1[..., self.lat_ix] + p2[..., self.lat_ix]) / 2))
        y = np.radians(p2[..., self.lat_ix] - p1[..., self.lat_ix])
        return R * np.sqrt(x**2 + y**2)

    def angle_from_latlon(self, p1, p2):
        # angle in radians from p1 to p2
        dx = np.radians(p2[..., self.lon_ix] - p1[..., self.lon_ix]) * np.cos(np.radians((p1[..., self.lat_ix] + p2[..., self.lat_ix]) / 2))
        dy = np.radians(p2[..., self.lat_ix] - p1[..., self.lat_ix])
        return np.arctan2(dy, dx)

    def wind_relative_to_road(self, p1, p2, wind_speed, wind_direction):
        wind_direction = 3 * np.pi / 2 - np.radians(wind_direction)
        if wind_direction < 0:
            wind_direction += 2 * np.pi

        # Use arctan2 for correct quadrant handling and vectorization
        road_direction = self.angle_from_latlon(p1, p2)

        return - wind_speed * np.cos(np.abs(road_direction - wind_direction))


    def gravity_force(self, p1, p2, xy_coords=False):

        if xy_coords:
            road_len = self.distance_from_xy(p1, p2)
        else:
            road_len = self.approximate_distance_from_latlon(p1, p2)

        # avoid division by zero for zero-length segments
        gradient = (p2[..., self.ele_ix] - p1[..., self.ele_ix]) / np.where(road_len == 0, np.inf, road_len)

        return self.total_weight * self.g * np.sin(np.arctan(gradient))


    def rolling_resistance_force(self, p1, p2, xy_coords=False):

        if xy_coords:
            road_len = self.distance_from_xy(p1, p2)
        else:
            road_len = self.approximate_distance_from_latlon(p1, p2)
        gradient = (p2[..., self.ele_ix] - p1[..., self.ele_ix]) / np.where(road_len == 0, np.inf, road_len)

        return self.coef_rolling_resistance * self.total_weight * self.g * np.cos(np.arctan(gradient))

    def cornering_time(self, p1, p2, xy_coords=False):
        # Penalty for corners, which reduces speed. This is a very rough approximation.
        # This is based on the sharpness of the corner

        # Take triplets, where the middle point defines the corner
        if xy_coords:
            theta_seg1 = np.arctan2(p2[:-1, self.lat_ix] - p1[:-1, self.lat_ix], p2[:-1, self.lon_ix] - p1[:-1, self.lon_ix])
            theta_seg2 = np.arctan2(p2[1:, self.lat_ix] - p1[1:, self.lat_ix], p2[1:, self.lon_ix] - p1[1:, self.lon_ix])
        else:
            theta_seg1 = self.angle_from_latlon(p1[:-1, :-1], p2[:-1, :-1])
            theta_seg2 = self.angle_from_latlon(p1[1:, :-1], p2[1:, :-1])

        # Calculate the angle between the two segments
        corner_angle = np.abs(theta_seg2 - theta_seg1)
        time_penalty_mult = np.zeros_like(corner_angle)

        # If the corner is sharper than 45 degrees, apply a penalty that increases with sharpness
        mask = corner_angle > np.pi / 4
        time_penalty_mult[mask] = 1 / (1 + np.exp(-(self.corner_coef_a * corner_angle[mask] - self.corner_coef_b)))  # sigmoid penalty

        return time_penalty_mult * self.corner_time_penalty

    def calculate_speed(self, p1, p2, wind_speed=0, wind_direction=0, xy_coords=False):
        # From: https://www.gribble.org/cycling/power_v_speed.html
        # return speed in m/s given power output and wind
        
        # Solve cubic a v**3 + b v**2 + c v + d = 0

        hw = self.wind_relative_to_road(p1, p2, wind_speed=wind_speed, wind_direction=wind_direction)

        a = 0.5 * self.cda * self.area * self.air_density
        b = hw * self.cda * self.area * self.air_density
        c = (self.gravity_force(p1, p2, xy_coords=xy_coords) + self.rolling_resistance_force(p1, p2, xy_coords=xy_coords)) \
            + (0.5 * self.cda * self.area * self.air_density * hw**2)
        d = - (1 - self.drive_train_loss) * self.power_output

        # compute cubic solution in a vectorized manner
        Q = (3 * a * c - b**2) / (9 * a ** 2)
        R = (9 * a * b * c - 27 * a**2 * d - 2 * b**3) / (54 * a**3)

        discr = Q**3 + R**2
        # if this is neg then check if case makes sence.
        # One cause for negative solution is that cyclist is going downhill
        nan_mask = discr < 0
        if np.sum(nan_mask) > 0:
            if np.all(self.gravity_force(p1[nan_mask], p2[nan_mask], xy_coords=xy_coords) < 0):
                pass
            else:
                raise ValueError("Negative discriminant in cubic solution, but cyclist is not going downhill. Check inputs.")

        sqrt_term = np.sqrt(discr)

        S = np.cbrt(R + sqrt_term)
        T = np.cbrt(R - sqrt_term)

        speed = np.array(S + T - b / (3 * a))
        speed[nan_mask] = self.max_speed
        return np.maximum(self.min_speed, np.minimum(speed, self.max_speed))
    
    
    def time_to_travel(self, p1, p2, wind_speed=0, wind_direction=0, xy_coords=False):
        # time in seconds to travel from p1 to p2

        if xy_coords:
            road_len = self.distance_from_xy(p1, p2)
        else:
            road_len = self.approximate_distance_from_latlon(p1, p2)

        speed = self.calculate_speed(p1, p2, wind_speed=wind_speed, wind_direction=wind_direction, xy_coords=xy_coords)

        return road_len / speed
