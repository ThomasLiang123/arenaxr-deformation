from arena import *
import math

scene = Scene(host="mqtt.arenaxr.org", scene="grid-deformation")

# grid dimensions (number of objects)
GRID_WIDTH = 40
GRID_LENGTH = 40
ITEM_SIZE = 0.2

DEFORM_RADIUS = 2
MAX_DEFORM = 0.5

lasti = 0
lastj = 0

curr_user = None

# change current user to newest joining user
def user_join_callback(scene, cam, msg):
    global curr_user
    curr_user = cam

# change morphs for one cube
def setMorphs(i, j, m1, m2, m3, m4):
    global grid
    global morphs

    if (i < 0 or j < 0 or i >= GRID_LENGTH or j >= GRID_WIDTH):
        return

    g = grid[i*GRID_WIDTH + j]
    morphs[0].value = m1
    morphs[1].value = m2
    morphs[2].value = m3
    morphs[3].value = m4
    g.update_morph(morphs)
    scene.update_object(g)

# reset morphs for all cubes within deform radius of one point
def reset_at(i, j):
    global grid
    global morphs

    changing = []
    for ii in range(i-DEFORM_RADIUS, i+DEFORM_RADIUS+1):
        for jj in range(j-DEFORM_RADIUS, j+DEFORM_RADIUS+1):
            if (ii < 0 or jj < 0 or ii > GRID_WIDTH or jj > GRID_LENGTH):
                continue

            setMorphs(ii,jj,0,0,0,0)

# get deformation value
def deform_func(x):
    return MAX_DEFORM / (1 + math.exp((8*MAX_DEFORM)*x - (4*MAX_DEFORM)))

# deform all cubes within deform radius of one point
def deform_grid(i, j):
    global grid
    global morphs

    changing = []
    for ii in range(i-DEFORM_RADIUS, i+DEFORM_RADIUS+1):
        for jj in range(j-DEFORM_RADIUS, j+DEFORM_RADIUS+1):
            if (ii < 0 or jj < 0 or ii > GRID_WIDTH or jj > GRID_LENGTH):
                continue

            # get x and y distances
            idiff = float(ii - i)
            jdiff = float(jj - j)

            # deformation values for the 4 top edges of the cube
            ideflarge, idefsmall, jdeflarge, jdefsmall = 0.0,0.0,0.0,0.0

            # if the cube location is smaller than the center, deform the larger edge more, and vice versa
            # deform more by deforming it to the value of the next cube closer to the center (so that edge connects with it)
            if idiff < 0:
                ideflarge = deform_func(abs(idiff)-1)
             idefsmall = deform_func(abs(idiff))
            elif idiff > 0:
             idefsmall = deform_func(abs(idiff)-1)
                ideflarge = deform_func(abs(idiff))
            else:
                ideflarge = deform_func(abs(idiff))
             idefsmall = deform_func(abs(idiff))

            if jdiff < 0:
                jdeflarge = deform_func(abs(jdiff)-1)
                jdefsmall = deform_func(abs(jdiff))
            elif jdiff > 0:
                jdefsmall = deform_func(abs(jdiff)-1)
                jdeflarge = deform_func(abs(jdiff))
            else:
                jdeflarge = deform_func(abs(jdiff))
                jdefsmall = deform_func(abs(jdiff))

            # calculate corner deformations from edges
            corner1 = ideflarge+jdeflarge
            corner2 = ideflarge+jdefsmall
            corner3 = idefsmall+jdeflarge
            corner4 = idefsmall+jdefsmall

            if idiff == -DEFORM_RADIUS:
                corner3 = 0
                corner4 = 0
            elif idiff == DEFORM_RADIUS:
                corner1 = 0
                corner2 = 0

            if jdiff == -DEFORM_RADIUS:
                corner2 = 0
                corner4 = 0
            elif jdiff == DEFORM_RADIUS:
                corner1 = 0
                corner3 = 0

            setMorphs(ii,jj,corner1,corner2,corner3,corner4)

# click handler - not currently used
def click(scene, evt, msg):
    global lasti
    global lastj

    if (evt.type == "mousedown"):
        strs = evt.object_id.split('-')
        i = int(strs[2])
        j = int(strs[3])

        reset_at(lasti, lastj)
        deform_grid(i, j)
        lasti = i
        lastj = j
    elif (evt.type == "mouseup"):
        reset_at(lasti, lastj)

# make grid
@scene.run_once
def make_grid():
    global grid
    global morphs
    grid = []

    # same morphs for every cube
    morphs = [Morph(morphtarget="corner1", value=0.0),
              Morph(morphtarget="corner2", value=0.0),
              Morph(morphtarget="corner3", value=0.0),
              Morph(morphtarget="corner4", value=0.0)]

    for i in range(GRID_LENGTH):
        row = []
        for j in range(GRID_WIDTH):
            item = GLTF(
                object_id="deform-cube-"+str(i)+"-"+str(j),
                position=(i*ITEM_SIZE,ITEM_SIZE/2,j*ITEM_SIZE),
                scale=(ITEM_SIZE/2,ITEM_SIZE/2,ITEM_SIZE/2),
                action="create",
                persist=True,
                #clickable=True,
                #evt_handler=click,
                url="store/users/thomasliang/griditem.glb",
            )
            item.update_morph(morphs)
            scene.add_object(item)
            grid.append(item)

@scene.run_forever(interval_ms=200)
def line_follow():
    global curr_user
    global lasti
    global lastj

    if curr_user:
        # get user position and update dormation with it
        pos = curr_user.data.position
        if 0 <= pos.x < ITEM_SIZE * GRID_WIDTH and 0 <= pos.z < ITEM_SIZE * GRID_LENGTH:
            i = int(pos.x / ITEM_SIZE)
            j = int(pos.z / ITEM_SIZE)

            if lasti != i and lastj != j:
                reset_at(lasti, lastj)
                deform_grid(i, j)
                lasti = i
                lastj = j

scene.user_join_callback = user_join_callback
scene.run_tasks()