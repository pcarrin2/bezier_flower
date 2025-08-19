import cairo
import math
import random

# aww hell yeah we got globals :(
radius = 150
margin = 200
num_points = 10

ctrl_radius = radius * math.sin(2 * math.pi/num_points)
side_length = 2*(radius+margin)

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
        print(p)
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
        print(p)
        context.arc(*p, 5, 0, 2*math.pi)
        context.fill()

    # draw bounding boxes in transparent grey
    for i in range(num_points):
        context.set_source_rgba(0,0,0,0.2)
        context.move_to(*points[i-1])
        context.line_to(*ctrl_pts[2*i])
        context.line_to(*points[i])
        context.line_to(*ctrl_pts[2*i+1])
        context.line_to(*points[i-1])
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

    #draw_annotations(context, points, ctrl_pts)



# printing message when file is saved
print("File Saved")

