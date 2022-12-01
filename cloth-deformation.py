from arena import *
import math
import random

# z positions - 0, 3, 4.5, 6 - offset = -1
# y positions - 0, 3 - offset = -1

CLOTH_WIDTH = 4
CLOTH_HEIGHT = 7

wind_y = 3.0
wind_z = 0.0
force_set = 1
force_offset = 0

locations = []
morphs = []

scene = Scene(host="mqtt.arenaxr.org", scene="cloth-deformation")

moving = 0
force_change = 0

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

@scene.run_once
def make_cloth():
    global cloth
    global wind_cone
    global morphs
    global locations

    cloth = GLTF(
        object_id="cloth",
        position=(0, 0, 0),
        scale=(1, 1, 1),
        action="create",
        url="store/users/thomasliang/cloth2.glb",
    )

    for i in range(CLOTH_HEIGHT-1):
        for j in range(CLOTH_WIDTH):
            locations.append((0,i,j))
            morphs.append(Morph(morphtarget=str(i)+"-"+str(j), value=0.0))

    cloth.update_morph(morphs)
    scene.add_object(cloth)

    wind_cone = Cone(
        object_id="wind_cone",
        position=(5, 0.5+wind_z, -wind_y),
        scale=(0.2, 1, 0.2),
        rotation=(90,0,90),
        color=(10, 70, 200),
    )
    scene.add_object(wind_cone)

    left_button = Box(
        object_id="left_button",
        position=(8, 0, 0),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_left,
        color=(255, 0, 0),
    )
    scene.add_object(left_button)

    right_button = Box(
        object_id="right_button",
        position=(8, 0, -3),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_right,
        color=(255, 0, 0),
    )
    scene.add_object(right_button)

    up_button = Box(
        object_id="up_button",
        position=(6.5, 0, -1.5),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_up,
        color=(255, 0, 0),
    )
    scene.add_object(up_button)

    down_button = Box(
        object_id="down_button",
        position=(9.5, 0, -1.5),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_down,
        color=(255, 0, 0),
    )
    scene.add_object(down_button)

    forward_button = Box(
        object_id="forward_button",
        position=(6.5, 0, -4),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_forward,
        color=(0, 0, 255),
    )
    scene.add_object(forward_button)

    backward_button = Box(
        object_id="backward_button",
        position=(9.5, 0, -4),
        scale=(1, 1, 1),
        clickable=True,
        evt_handler=click_backward,
        color=(0, 0, 255),
    )
    scene.add_object(backward_button)

    deform()

def distance(x, y):
    return math.sqrt(math.pow(y[0] - x[0], 2) + math.pow((y[1] - x[1]) * 0.1, 2) + math.pow(y[2] - x[2], 2))

def deform_magnitude(dist):
    wind_force = force_set + force_offset
    if dist == 0 or wind_force / dist > 1:
        return wind_force

    return wind_force / dist

def deform():
    global cloth
    global morphs

    for i in range((CLOTH_HEIGHT-1) * CLOTH_WIDTH):
        loc = locations[i]
        dist = distance(loc, (0, wind_z, wind_y))
        height_dist = CLOTH_HEIGHT - loc[1]

        morphs[i].value = deform_magnitude(dist) * float(height_dist) / CLOTH_HEIGHT;

    cloth.update_morph(morphs)
    scene.update_object(cloth)

@scene.run_forever(interval_ms=100)
def wind_change():
    global force_change
    global force_set
    global force_offset
    global wind_y
    global wind_z
    global wind_cone

    force_set += force_change * 0.1
    if force_set > 2:
        force_set = 2
    elif force_set < 0:
        force_set = 0

    if moving == 1:
        if wind_y > 0:
            wind_y -= 0.1
    elif moving == 2:
        if wind_y < CLOTH_WIDTH-1:
            wind_y += 0.1
    elif moving == 3:
        if wind_z < CLOTH_HEIGHT-2:
            wind_z += 0.1
    elif moving == 4:
        if wind_z > 0:
            wind_z -= 0.1

    if moving > 0:
        wind_cone.update_attributes(position = (5, 0.5+wind_z, -wind_y))
        scene.update_object(wind_cone)

    force_offset += float(random.randrange(-10,10)) / 100.0
    if force_offset > 0.5 * force_set:
        force_offset = 0.5 * force_set
    elif force_offset < -0.5 * force_set:
        force_offset = -0.5 * force_set
    deform()

scene.run_tasks()
