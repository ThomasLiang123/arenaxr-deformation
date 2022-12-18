from arena import *
import math
import random

# number of vertices in each dimension of the cloth
CLOTH_WIDTH = 8
CLOTH_HEIGHT = 14

# wind variables
wind_y = 3.0
wind_z = 0.0
force_set = 1
force_offset = 0

# locations of vertices and their respective morph targets
locations = []
morphs = []

scene = Scene(host="mqtt.arenaxr.org", scene="cloth-deformation")

# is the user moving the wind
# 0 - not moving
# 1 - left
# 2 - right
# 3 - down
# 4 - up
moving = 0

# is the user changing the force
# -1, 0, 1 (back, still, forward)
force_change = 0

# click handlers
def click_left(scene, evt, msg):
    global moving

    if evt.type == "mousedown":
        moving = 1
    elif evt.type == "mouseup":
        moving = 0

def click_right(scene, evt, msg):
    global moving

    if evt.type == "mousedown":
        moving = 2
    elif evt.type == "mouseup":
        moving = 0

def click_up(scene, evt, msg):
    global moving

    if evt.type == "mousedown":
        moving = 3
    elif evt.type == "mouseup":
        moving = 0

def click_down(scene, evt, msg):
    global moving

    if evt.type == "mousedown":
        moving = 4
    elif evt.type == "mouseup":
        moving = 0

def click_forward(scene, evt, msg):
    global force_change

    if evt.type == "mousedown":
        force_change = 1
    elif evt.type == "mouseup":
        force_change = 0

def click_backward(scene, evt, msg):
    global force_change

    if evt.type == "mousedown":
        force_change = -1
    elif evt.type == "mouseup":
        force_change = 0

# object creation
@scene.run_once
def make_scene():
    global cloth
    global wind_cone
    global morphs
    global locations

    # make cloth object
    cloth = GLTF(
        object_id="cloth",
        position=(0, 0, 0),
        scale=(1, 1, 1),
        action="create",
        url="store/users/thomasliang/cloth4morph.glb",
    )

    # for each vertex in the cloth, add location and respective morph
    for i in range(CLOTH_HEIGHT):
        for j in range(CLOTH_WIDTH+1):
            # each vertex is separated by 0.5 units - so i and j / 2
            locations.append((0,float(i)/2,float(j)/2))

            # morph name format: "m" + y location * 10 + ":" + z location * 10
            y = i * 5
            z = -j * 5
            morphs.append(Morph(morphtarget="m"+str(y)+":"+str(z), value=0.0))

    cloth.update_morph(morphs)
    scene.add_object(cloth)

    # wind location indicator cone
    wind_cone = Cone(
        object_id="wind_cone",
        position=(5, 0.5+wind_z, -wind_y),
        scale=(0.2, 1, 0.2),
        rotation=(90,0,90),
        color=(10, 70, 200),
    )
    scene.add_object(wind_cone)

    # wind control UI
    panel = Box(
        object_id="panel",
        position=(8, 1.5, 3),
        scale=(0.2, 3, 2),
        color=(100, 100, 100),
    )
    scene.add_object(panel)

    paneltext = Text(
        object_id="panel_text",
        text="wind control",
        align="center",
        position=(8.2, 2.75, 3),
        rotation=(0,90,0),
        scale=(1, 1, 1),
        color=(0,0,0)
    )
    scene.add_object(paneltext)

    left_button = Box(
        object_id="left_button",
        position=(8.1, 1.75, 3.75),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_left,
        color=(255, 0, 0),
    )
    scene.add_object(left_button)

    lefttext = Text(
        object_id="left_text",
        text="left",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 1.75, 3.75),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(lefttext)

    right_button = Box(
        object_id="right_button",
        position=(8.1, 1.75, 3),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_right,
        color=(255, 0, 0),
    )
    scene.add_object(right_button)

    righttext = Text(
        object_id="right_text",
        text="right",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 1.75, 3),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(righttext)

    up_button = Box(
        object_id="up_button",
        position=(8.1, 2.125, 3.3775),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_up,
        color=(255, 0, 0),
    )
    scene.add_object(up_button)

    uptext = Text(
        object_id="up_text",
        text="up",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 2.125, 3.3775),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(uptext)

    down_button = Box(
        object_id="down_button",
        position=(8.1, 1.375, 3.3775),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_down,
        color=(255, 0, 0),
    )
    scene.add_object(down_button)

    downtext = Text(
        object_id="down_text",
        text="down",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 1.375, 3.3775),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(downtext)

    forward_button = Box(
        object_id="forward_button",
        position=(8.1, 2.125, 2.5),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_forward,
        color=(0, 0, 255),
    )
    scene.add_object(forward_button)

    forwardtext = Text(
        object_id="forward_text",
        text="faster",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 2.125, 2.5),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(forwardtext)

    backward_button = Box(
        object_id="backward_button",
        position=(8.1, 1.375, 2.5),
        scale=(0.3, 0.3, 0.3),
        clickable=True,
        evt_handler=click_backward,
        color=(0, 0, 255),
    )
    scene.add_object(backward_button)

    backwardtext = Text(
        object_id="backward_text",
        text="slower",
        align="center",
        rotation=(0,90,0),
        position=(8.25, 1.375, 2.5),
        scale=(0.4, 0.4, 0.4),
        color=(0,0,0)
    )
    scene.add_object(backwardtext)

    deform()

# 3D distance calculator
def distance(x, y):
    return math.sqrt(math.pow(y[0] - x[0], 2) + math.pow((y[1] - x[1]) * 0.1, 2) + math.pow(y[2] - x[2], 2))

# get deformation magnitude based on distance
# formula is magnitude = force / (dist^2)
def deform_magnitude(dist):
    wind_force = force_set + force_offset

    # prevent magnitude from being too high (or infinity)
    if dist == 0 or wind_force / ((dist*2)) > wind_force:
        return wind_force

    return wind_force / ((dist*2))

# deform all vertices of cloth
def deform():
    global cloth
    global morphs

    # for each vertex in the cloth, change morph value (deform)
    for i in range((CLOTH_HEIGHT) * (CLOTH_WIDTH+1)):
        loc = locations[i]
        dist = distance(loc, (0, wind_z, wind_y))
        
        # deform higher vertices less (to actually make it look like a cloth)
        height_dist = CLOTH_HEIGHT - loc[1]
        morphs[i].value = deform_magnitude(dist) * float(height_dist) / CLOTH_HEIGHT;

    cloth.update_morph(morphs)
    scene.update_object(cloth)

@scene.run_forever(interval_ms=200)
def wind_change():
    global force_change
    global force_set
    global force_offset
    global wind_y
    global wind_z
    global wind_cone

    # change force of wind if user wants
    force_set += force_change * 0.1
    if force_set > 2:
        force_set = 2
    elif force_set < 0:
        force_set = 0

    # change location of wind if user wants
    if moving == 1:
        if wind_y > 0:
            wind_y -= 0.1
    elif moving == 2:
        if wind_y < (CLOTH_WIDTH-1)/2:
            wind_y += 0.1
    elif moving == 3:
        if wind_z < (CLOTH_HEIGHT-2)/2:
            wind_z += 0.1
    elif moving == 4:
        if wind_z > 0:
            wind_z -= 0.1

    # move cone
    if moving > 0:
        wind_cone.update_attributes(position = (5, 0.5+wind_z, -wind_y))
        scene.update_object(wind_cone)

    # randomly make slight changes to wind to simulate real wind
    force_offset += float(random.randrange(-10,10)) / 100.0
    if force_offset > 0.5 * force_set:
        force_offset = 0.5 * force_set
    elif force_offset < -0.5 * force_set:
        force_offset = -0.5 * force_set
    deform()

scene.run_tasks()
