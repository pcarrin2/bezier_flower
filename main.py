import cairo
import math
from sys import argv
from PIL import Image
import bezier
import numpy as np
from apng import APNG
import random

print("Processing constant parameters...")
# global params, edit these
num_points = int(argv[1]) # number of symmetric nodes to create around a circle
radius_min = 100 # pixels, inner radius
radius_max = 500 # pixels, outer radius
steps = 400 # number of steps between inner and outer radius
margin = 100 # pixels around border
opacity = 20 # out of 255
rendering_passes = [(0.1, (1, 0, 0)), (0.5, (0, 1, 0)), (0.2, (0, 0, 1)), (0.0, (1, 1, 1))] # (noise as stdev of bezier param, (R, G, B))
time_steps = 100 # time steps in animation
ndots = 50 # number of dots created during a single pass while rasterizing a single bezier curve

# geometry of canvas
side_length = 2*(radius_max+margin)
center = (radius_max+margin, radius_max+margin)

print("Creating arrays for bezier curves...")

print("-> Radii")
radii = [radius_max - i * (radius_max-radius_min)/steps for i in range(steps)] 

print("-> Endpoints")
endpoints_start = [(center[0] + radius_max*math.cos(i*(2*math.pi/num_points)), center[1] + radius_max*math.sin(i*(2*math.pi/num_points))) for i in range(num_points)]
endpoints_end = [(center[0] + radius_min*math.cos(i*(2*math.pi/num_points)), center[1] + radius_min*math.sin(i*(2*math.pi/num_points))) for i in range(num_points)]
endpoints = np.linspace(endpoints_start, endpoints_end, num=steps)

print("-> Control Angles")
#control_angles_start = [i*(2*math.pi/num_points) + math.pi*random.random()/2 for i in range(num_points)]
control_angles_start = [2*math.pi*random.random() for i in range(num_points)]
#control_angles_end = [i*(2*math.pi/num_points) + math.pi*random.random()/2 for i in range(num_points)]
control_angles_end = [i*(2*math.pi/num_points) + math.pi/2 for i in range(num_points)]

control_angles = np.empty((time_steps, steps, num_points))
control_angles[0] = np.linspace(control_angles_start, control_angles_end, num=steps)
control_angles_time_inc = np.linspace(0.0, 2*math.pi, num=time_steps, endpoint=False)
for i in range(time_steps):
    control_angles[i] = control_angles[0] + control_angles_time_inc[i]

print("-> Control Points")
first_control_points = np.empty((time_steps, steps, num_points, 2))
second_control_points = np.empty((time_steps, steps, num_points, 2))

def find_control_radius(radius, num_points):
    return radius * math.sin(2*math.pi/num_points)

for time_step in range(time_steps):
    for step in range(steps):
        control_radius = find_control_radius(radii[step], num_points)
        first_control_points[time_step][step] = [
                [endpoints[step][i][0] - control_radius*math.cos(control_angles[time_step][step][i]),
                 endpoints[step][i][1] - control_radius*math.sin(control_angles[time_step][step][i])]
                for i in range(num_points)
                ]
        second_control_points[time_step][step] = [
                [endpoints[step][i][0] + control_radius*math.cos(control_angles[time_step][step][i]),
                 endpoints[step][i][1] + control_radius*math.sin(control_angles[time_step][step][i])]
                for i in range(num_points)
                ]

print("Restructuring data...")
bezier_curves_per_frame = np.empty((time_steps, steps*num_points, 2, 4))

# shitty way which i will make fast
for time_step in range(time_steps):
    for step in range(steps):
        for i in range(num_points):
            first_endpoint = endpoints[step][i-1]
            first_control = second_control_points[time_step][step][i-1]
            second_control = first_control_points[time_step][step][i]
            second_endpoint = endpoints[step][i]
            bezier_curves_per_frame[time_step][step*num_points+i] = np.transpose([first_endpoint, first_control, second_control, second_endpoint])

print("Constructing image frames...")

# fixing colors: multiplying by opacity
rendering_passes = [(p[0], (int(opacity*p[1][0]), int(opacity*p[1][1]), int(opacity*p[1][2]))) for p in rendering_passes]
bezier_param_values = np.arange(0, 1, 1.0/ndots)

def draw_curve(pixels, nodes, rendering_passes, bezier_param_values):
    curve = bezier.Curve(nodes, degree=3)
    for p in rendering_passes:
        noise = p[0]
        color = p[1]
        noise = np.random.normal(0, noise, len(bezier_param_values))
        bezier_param_with_noise = bezier_param_values + noise
        bezier_pixels = curve.evaluate_multi(bezier_param_with_noise)
        for px in np.transpose(bezier_pixels):
            x = int(px[0])
            y = int(px[1])
            try:
                current_px = pixels[x,y]
                pixels[x,y] = (current_px[0]+color[0], current_px[1]+color[1], current_px[2]+color[2])
            except IndexError:
                pass

for time_step in range(time_steps):
    print(f"-> Frame {time_step}")
    # set up bitmap to write to
    im = Image.new(mode="RGB", size=(side_length, side_length))
    px = im.load()

    for curve in bezier_curves_per_frame[time_step]:
        draw_curve(px, curve, rendering_passes, bezier_param_values)

    im.save(f"out_{time_step}.png")

print("Combining into animated PNG...")
files = [(f"out_{time_step}.png", 20) for time_step in range(time_steps)]
im = APNG()
for file, delay in files:
    im.append_file(file, delay=delay)

print("Done!")
im.save("out_animated.png")
