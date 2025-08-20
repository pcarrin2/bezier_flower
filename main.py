import cairo
import math
import random
from sys import argv
from draw_bezier import draw_curve
from PIL import Image

# aww hell yeah we got globals :(
radius_min = 100
radius_max = 300
steps = 200

radii = [radius_max - i * (radius_max-radius_min)/steps for i in range(steps)] 

margin = 100
num_points = int(argv[1])
side_length = 2*(radius_max+margin)
center = (radius_max+margin, radius_max+margin)

#ctrl_angles_start = [i*(2*math.pi/num_points) - math.pi*random.random()/2 for i in range(num_points)]
ctrl_angles_start = [i*(2*math.pi/num_points) - 2*math.pi*random.random() for i in range(num_points)]
#ctrl_angles_finish = [i*(2*math.pi/num_points) - math.pi*random.random()/2 for i in range(num_points)]
ctrl_angles_finish = [i*(2*math.pi/num_points) - math.pi/2 for i in range(num_points)]
ctrl_angles_steps = []
for i in range(steps):
    ctrl_angles_steps.append([ctrl_angles_start[j] + i*(ctrl_angles_finish[j]-ctrl_angles_start[j])/steps for j in range(num_points)])


def ctrl_radius(radius):
    return radius * math.sin(2*math.pi/num_points)

# determine whether points p1 and p2 are on the same side of the segment defined by
# s1 and s2. returns True for same side, False for opposite sides.
# from https://stackoverflow.com/questions/28555246/finding-out-if-two-points-are-on-the-same-side
def same_side(s1, s2, p1, p2):
    return ((s1[1]-s2[1])*(p1[0]-s1[0])+(s2[0]-s1[0])*(p1[1]-s1[1]))*((s1[1]-s2[1])*(p2[0]-s1[0])+(s2[0]-s1[0])*(p2[1]-s1[1]))>0

im = Image.new(mode="RGB", size=(side_length, side_length))
px = im.load()

for step in range(steps):
    radius = radii[step] 
    ctrl_angles = ctrl_angles_steps[step]
    # points along big circle
    points = [(center[0] + radius*math.cos(i*(2*math.pi/num_points)), center[1] + radius*math.sin(i*(2*math.pi/num_points))) for i in range(num_points)]
    
    ctrl_pts = []
    for i in range(num_points):
        ctrl_pts.append(
                (points[i][0] + ctrl_radius(radius)*math.cos(ctrl_angles[i]), 
                 points[i][1] + ctrl_radius(radius)*math.sin(ctrl_angles[i])))
        ctrl_pts.append(
                (points[i][0] - ctrl_radius(radius)*math.cos(ctrl_angles[i]),
                 points[i][1] - ctrl_radius(radius)*math.sin(ctrl_angles[i])))

    ctrl_pts.append(ctrl_pts.pop(0))
    # Drawing Curve
    for i in range(num_points):
        draw_curve(px, points[i-1], points[i], [ctrl_pts[2*i], ctrl_pts[2*i+1]], 0, 20, 50)

im.save("out.png")
