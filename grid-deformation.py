from arena import *
import math

scene = Scene(host="mqtt.arenaxr.org", scene="grid-deformation")

GRID_WIDTH = 20
GRID_LENGTH = 20

DEFORM_RADIUS = 2
MAX_DEFORM = 0.5

lasti = 0
lastj = 0

def setMorphs(i, j, m1, m2, m3, m4):
    global grid
    global morphs

    if (i < 0 or j < 0 or i >= GRID_LENGTH or j >= GRID_WIDTH):
        return

    g = grid[i][j]
    morphs[0].value = m1
    morphs[1].value = m2
    morphs[2].value = m3
    morphs[3].value = m4
    g.update_morph(morphs)
    scene.update_object(g)

def reset_at(i, j):
    global grid
    global morphs

    for ii in range(i-DEFORM_RADIUS, i+DEFORM_RADIUS+1):
        for jj in range(j-DEFORM_RADIUS, j+DEFORM_RADIUS+1):
            setMorphs(ii,jj,0,0,0,0)

def deform_func(x):

    return MAX_DEFORM / (1 + math.exp((8*MAX_DEFORM)*x - (4*MAX_DEFORM)))

def deform_grid(i, j):
    global grid
    global morphs

    for ii in range(i-DEFORM_RADIUS, i+DEFORM_RADIUS+1):
        for jj in range(j-DEFORM_RADIUS, j+DEFORM_RADIUS+1):
            idiff = float(ii - i)
            jdiff = float(jj - j)

            idefclose, ideffar, jdefclose, jdeffar = 0.0,0.0,0.0,0.0

            if idiff < 0:
                idefclose = deform_func(abs(idiff)-1)
                ideffar = deform_func(abs(idiff))
            elif idiff > 0:
                ideffar = deform_func(abs(idiff)-1)
                idefclose = deform_func(abs(idiff))
            else:
                idefclose = deform_func(abs(idiff))
                ideffar = deform_func(abs(idiff))

            if jdiff < 0:
                jdefclose = deform_func(abs(jdiff)-1)
                jdeffar = deform_func(abs(jdiff))
            elif jdiff > 0:
                jdeffar = deform_func(abs(jdiff)-1)
                jdefclose = deform_func(abs(jdiff))
            else:
                jdefclose = deform_func(abs(jdiff))
                jdeffar = deform_func(abs(jdiff))

            corner1 = idefclose+jdefclose
            corner2 = idefclose+jdeffar
            corner3 = ideffar+jdefclose
            corner4 = ideffar+jdeffar

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

    # setMorphs(i,j,0.5,0.5,0.5,0.5)
    # setMorphs(i-1,j,0.5,0.5,0,0)
    # setMorphs(i+1,j,0,0,0.5,0.5)
    # setMorphs(i,j-1,0.5,0,0.5,0)
    # setMorphs(i,j+1,0,0.5,0,0.5)
    # setMorphs(i-1,j-1,0.5,0,0,0)
    # setMorphs(i-1,j+1,0,0.5,0,0)
    # setMorphs(i+1,j-1,0,0,0.5,0)
    # setMorphs(i+1,j+1,0,0,0,0.5)

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

@scene.run_once
def make_grid():
    global grid
    global morphs
    grid = []

    morphs = [Morph(morphtarget="corner1", value=0.0),
              Morph(morphtarget="corner2", value=0.0),
              Morph(morphtarget="corner3", value=0.0),
              Morph(morphtarget="corner4", value=0.0)]

    for i in range(GRID_WIDTH):
        row = []
        for j in range(GRID_LENGTH):
            item = GLTF(
                object_id="deform-cube-"+str(i)+"-"+str(j),
                position=(i,0.5,j),
                scale=(0.5,0.5,0.5),
                action="create",
                persist=True,
                clickable=True,
                evt_handler=click,
                url="store/users/thomasliang/griditem.glb",
            )
            item.update_morph(morphs)
            scene.add_object(item)
            row.append(item)

        grid.append(row)

scene.run_tasks()