from arena import *

scene = Scene(host="mqtt.arenaxr.org", scene="grid-deformation")

GRID_WIDTH = 5
GRID_LENGTH = 5

defidx = 0

def reset_grid():
    global grid
    global morphs

    morphs[0].value = 0
    morphs[1].value = 0
    morphs[2].value = 0
    morphs[3].value = 0

    for i in range(GRID_WIDTH):
        for j in range(GRID_LENGTH):
            g = grid[i][j]

            g.update_morph(morphs)
            scene.update_object(g)
def deform_grid(i, j):
    global grid
    global morphs

    g0 = grid[i][j]
    morphs[0].value = 0.5
    morphs[1].value = 0.5
    morphs[2].value = 0.5
    morphs[3].value = 0.5
    g0.update_morph(morphs)
    scene.update_object(g0)

    if i > 0:
        gi = grid[i-1][j]
        morphs[0].value = 0.5
        morphs[1].value = 0.5
        morphs[2].value = 0
        morphs[3].value = 0
        gi.update_morph(morphs)
        scene.update_object(gi)

    if i < GRID_WIDTH-1:
        gi = grid[i+1][j]
        morphs[0].value = 0
        morphs[1].value = 0
        morphs[2].value = 0.5
        morphs[3].value = 0.5
        gi.update_morph(morphs)
        scene.update_object(gi)

    if j > 0:
        gi = grid[i][j-1]
        morphs[0].value = 0.5
        morphs[1].value = 0
        morphs[2].value = 0.5
        morphs[3].value = 0
        gi.update_morph(morphs)
        scene.update_object(gi)

    if j < GRID_LENGTH-1:
        gi = grid[i][j+1]
        morphs[0].value = 0
        morphs[1].value = 0.5
        morphs[2].value = 0
        morphs[3].value = 0.5
        gi.update_morph(morphs)
        scene.update_object(gi)

    if i > 0 and j > 0:
        gi = grid[i-1][j-1]
        morphs[0].value = 0.5
        morphs[1].value = 0
        morphs[2].value = 0
        morphs[3].value = 0
        gi.update_morph(morphs)
        scene.update_object(gi)

    if i > 0 and j < GRID_LENGTH-1:
        gi = grid[i-1][j+1]
        morphs[0].value = 0
        morphs[1].value = 0.5
        morphs[2].value = 0
        morphs[3].value = 0
        gi.update_morph(morphs)
        scene.update_object(gi)

    if i < GRID_WIDTH-1 and j > 0:
        gi = grid[i + 1][j - 1]
        morphs[0].value = 0
        morphs[1].value = 0
        morphs[2].value = 0.5
        morphs[3].value = 0
        gi.update_morph(morphs)
        scene.update_object(gi)

    if i < GRID_WIDTH-1 and j < GRID_LENGTH - 1:
        gi = grid[i + 1][j + 1]
        morphs[0].value = 0
        morphs[1].value = 0
        morphs[2].value = 0
        morphs[3].value = 0.5
        gi.update_morph(morphs)
        scene.update_object(gi)
        

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
                object_id="deform-cube"+str(i)+str(j),
                position=(i,0.5,j),
                scale=(0.5,0.5,0.5),
                action="create",
                persist=False,
                url="store/users/thomasliang/griditem.glb",
            )
            item.update_morph(morphs)
            scene.add_object(item)
            row.append(item)

        grid.append(row)


@scene.run_forever(interval_ms=1000)
def periodic():
    global defidx

    defidx = (defidx + 1) % (GRID_WIDTH * GRID_LENGTH)
    defi = int(defidx / GRID_LENGTH)
    defj = int(defidx % GRID_LENGTH)

    reset_grid()s
    deform_grid(defi, defj)

scene.run_tasks()