from arena import *
import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

scene = Scene(host="mqtt.arenaxr.org", scene="deformation")

@scene.run_once
def make_xr_logo():
    xr_logo = GLTF(
        object_id="xr-logo",
        position=(0,0,-3),
        scale=(1.2,1.2,1.2),
        url="store/users/wiselab/models/XR-logo.glb",
    )
    scene.add_object(xr_logo)
    list_files("store")



scene.run_tasks()