from arena import *
import time

scene = Scene(host="mqtt.arenaxr.org", scene="deformation")

x = 0

def click(scene, evt, msg):
    print("clicked")

@scene.run_once
def make_xr_logo():
    global deformcube
    deformcube = GLTF(
        object_id="deform-cube",
        position=(0,3,-3),
        scale=(1.2,1.2,1.2),
        click_listener=True,
        evt_handler=click,
        action="create",
        url="store/users/thomasliang/cubedeform.glb",
    )

    scene.add_object(deformcube)

@scene.run_forever(interval_ms=1000)
def periodic():
    global x
    global deformcube

    morphs = [Morph(morphtarget="F1", value=0.0),
              Morph(morphtarget="F2", value=0.0),
              Morph(morphtarget="F3", value=0.0),
              Morph(morphtarget="F4", value=0.0),
              Morph(morphtarget="F5", value=0.0),
              Morph(morphtarget="F6", value=0.0)]

    morphs[x].value = 1.0

    deformcube.update_morph(morphs)
    scene.update_object(deformcube)

    x += 1
    x %= 6



scene.run_tasks()