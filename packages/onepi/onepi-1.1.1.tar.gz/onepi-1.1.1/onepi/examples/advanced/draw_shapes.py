# @author botnroll.com

import time
import signal
from onepi.utils.shape_generator import ShapeGenerator
from onepi.one import BnrOneAPlus

# Depends on the surface
# wood: 1.0
# vynil: 0.985
# carpet: 0.985

SLIP_FACTOR = 0.94

one = BnrOneAPlus()
one_draw = ShapeGenerator(one, SLIP_FACTOR)


def my_shape():
    # angle_deg, speed, radius_of_curvature_mm
    speed = 200
    one_draw.rotate_angle_deg_at_speed(180, speed, 100)
    one_draw.rotate_angle_deg_at_speed(-180, speed, 60)
    one_draw.rotate_angle_deg_at_speed(360, 70, 150)
    one_draw.rotate_angle_deg_at_speed(-180, speed, 60)
    one_draw.rotate_angle_deg_at_speed(180, speed, 100)


def mickey_mouse():
    # angle_deg, speed, radius_of_curvature_mm
    speed = 200
    one_draw.rotate_angle_deg_at_speed(140, speed, 150)
    one_draw.rotate_angle_deg_at_speed(-155, speed, 0)
    one_draw.rotate_angle_deg_at_speed(320, speed, 80)
    one_draw.rotate_angle_deg_at_speed(-155, speed, 0)
    one_draw.rotate_angle_deg_at_speed(60, speed, 150)
    one_draw.rotate_angle_deg_at_speed(-155, speed, 0)
    one_draw.rotate_angle_deg_at_speed(320, speed, 80)
    one_draw.rotate_angle_deg_at_speed(-155, speed, 0)
    one_draw.rotate_angle_deg_at_speed(140, speed, 150)


def house():
    """
    example on how to set a motion with the shape of a house
    """
    speed = 200
    one_draw.move_straight_at_speed(200, speed)
    one_draw.rotate_angle_deg_at_speed(90, speed, 0)
    one_draw.move_straight_at_speed(200, speed)
    one_draw.rotate_angle_deg_at_speed(90, speed)
    one_draw.move_straight_at_speed(200, speed)
    one_draw.rotate_angle_deg_at_speed(-135, speed)
    one_draw.move_straight_at_speed(144, speed)
    one_draw.rotate_angle_deg_at_speed(-90, speed)
    one_draw.move_straight_at_speed(144, speed)
    one_draw.rotate_angle_deg_at_speed(-90, speed)
    one_draw.move_straight_at_speed(282, speed)
    one_draw.rotate_angle_deg_at_speed(-135, speed)
    one_draw.move_straight_at_speed(200, speed)
    one_draw.rotate_angle_deg_at_speed(-135, speed)
    one_draw.move_straight_at_speed(282, speed)


def draw_shapes():
    speed = 200
    # one_draw.move_straight_at_speed(800, speed, 200)
    # one_draw.rotate_angle_deg_at_speed(360, speed, 100, 60)
    # one_draw.rotate_angle_deg_at_speed(720, speed, 0, 360)
    # one_draw.rotate_angle_deg_at_speed(720, speed, 80, 0)
    # one_draw.rounded_polygon(150, 4, speed)
    # one_draw.square(300, 200) # slip 0.93
    # one_draw.polygon(200, 4, speed)
    # one_draw.circle(150) # slip 0.94
    # one_draw.mickey_mouse()
    # one_draw.house()
    # one_draw.heart()
    # one_draw.triangle(300)
    # one_draw.polygon(300, 5)
    # one_draw.polygon(300, 6)
    # one_draw.polygon(300, 7)
    # one_draw.polygon(220, 10)

    # one_draw.fibonacci_spiral(50, 7)
    # one_draw.archimedean_spiral(0.3, 360 * 3)
    # one_draw.snake(800, 5, speed, 90)
    # one_draw.snake(800, 12, speed, 30)
    # one_draw.snake(800, 2, speed, 45, 0)
    # one_draw.snake(800, 4, speed, 180, 0)
    # one_draw.snake(1000, 14, speed, 60, 30)
    one_draw.snake(1200, 8, speed, 270, 45)
    # one_draw.snake(400, 4, speed, 300, 90)
    # one_draw.snake(400, 6, speed, 300, 120)
    # one_draw.snake(600, 16, speed, 320, 155)


def setup():
    print("Get ready")
    time.sleep(3)
    print("Go")
    draw_shapes()
    exit(0)


def loop():
    pass


def main():

    # function to stop the robot on exiting with CTRL+C
    def stop_and_exit(sig, frame):
        one.stop()
        time.sleep(0.1)
        exit(0)

    signal.signal(signal.SIGINT, stop_and_exit)

    setup()
    while True:
        loop()


if __name__ == "__main__":
    main()
