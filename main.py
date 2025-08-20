import cairo
import math
import random
from sys import argv

# aww hell yeah we got globals :(
radius = 150
margin = 200
num_points = int(argv[1])

ctrl_radius = radius * math.sin(2*math.pi/num_points)
side_length = 2*(radius+margin)

# determine whether points p1 and p2 are on the same side of the segment defined by
# s1 and s2. returns True for same side, False for opposite sides.
# from https://stackoverflow.com/questions/28555246/finding-out-if-two-points-are-on-the-same-side
def same_side(s1, s2, p1, p2):
    return ((s1[1]-s2[1])*(p1[0]-s1[0])+(s2[0]-s1[0])*(p1[1]-s1[1]))*((s1[1]-s2[1])*(p2[0]-s1[0])+(s2[0]-s1[0])*(p2[1]-s1[1]))>0

def draw_annotations(context, points, ctrl_pts):
    # draw circle in grey
    context.set_source_rgb(0.5, 0.5, 0.5)
    context.set_line_width(2)
    context.set_line_join(cairo.LineJoin.ROUND)
    context.arc(*center, radius, 0, 2*math.pi)
    context.stroke()

    # draw points and control radii in red
    context.set_source_rgb(1, 0, 0)

    for p in points:
        context.arc(*p, 5, 0, 2*math.pi)
        context.fill()
        context.arc(*p, ctrl_radius, 0, 2*math.pi)
        context.stroke()

    # draw control points in green/blue
    green = True
    for p in ctrl_pts:
        if green:
            context.set_source_rgb(0,1,0)
            green = False
        else:
            context.set_source_rgb(0,0,1)
            green = True
        context.arc(*p, 5, 0, 2*math.pi)
        context.fill()

    # draw bounding boxes in transparent grey
    for i in range(num_points):
        if same_side(ctrl_pts[2*i], ctrl_pts[2*i+1], points[i-1], points[i]):
            if same_side(points[i-1], ctrl_pts[2*i], points[i], ctrl_pts[2*i+1]):
                hull_points = [points[i-1], ctrl_pts[2*i], ctrl_pts[2*i+1], points[i]] 
            else:
                hull_points = [points[i-1], ctrl_pts[2*i+1], ctrl_pts[2*i], points[i]] 
        else:
            if same_side(points[i-1], ctrl_pts[2*i+1], points[i], ctrl_pts[2*i]):
                hull_points = [points[i-1], ctrl_pts[2*i+1], points[i], ctrl_pts[2*i]] 
            else:
                hull_points = [points[i-1], ctrl_pts[2*i], points[i], ctrl_pts[2*i+1]] 

        context.set_source_rgba(0,0,0,0.2)
        context.move_to(*hull_points[-1])
        for p in hull_points:
            context.line_to(*p)
        context.fill()

# creating a SVG surface
with cairo.SVGSurface("out.svg", side_length, side_length) as surface:
    # defining points evenly spaced along circle
    center = (radius+margin, radius+margin)
    points = [(center[0] + radius*math.cos(i*(2*math.pi/num_points)), center[1] + radius*math.sin(i*(2*math.pi/num_points))) for i in range(num_points)]
    ctrl_angles = [i*(2*math.pi/num_points) - math.pi*random.random()/2 for i in range(num_points)]
    ctrl_pts = []
    for i in range(num_points):
        ctrl_pts.append(
                (points[i][0] + ctrl_radius*math.cos(ctrl_angles[i]), 
                 points[i][1] + ctrl_radius*math.sin(ctrl_angles[i])))
        ctrl_pts.append(
                (points[i][0] - ctrl_radius*math.cos(ctrl_angles[i]),
                 points[i][1] - ctrl_radius*math.sin(ctrl_angles[i])))

    context = cairo.Context(surface)
    

    context.set_source_rgb(0,0,0)
    context.set_line_width(2)
    context.set_line_join(cairo.LineJoin.ROUND)
    
    context.move_to(*points[0])
    points.append(points.pop(0))
    ctrl_pts.append(ctrl_pts.pop(0))
    # Drawing Curve
    for i in range(num_points):
        context.curve_to(*ctrl_pts[2*i], *ctrl_pts[2*i+1], *points[i])
    context.stroke()

    draw_annotations(context, points, ctrl_pts)



# printing message when file is saved
print("File Saved")

