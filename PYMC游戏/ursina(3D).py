from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import os

MAX_DIST = 5
FILE1 = "level1.txt"
FILE2 = "level2.txt"
USER_FILE = "user.txt"
POS_FILE = "level.txt"
SIZE = 50

app = Ursina()
window.title = "MC"

block_map = {}
user_blocks = set()
generated_set = set()

if not os.path.exists(USER_FILE):
    open(USER_FILE, "w", encoding="utf8").close()

cross_h = Entity(parent=camera.ui, model='quad', color=color.white, scale=(0.002,0.025))
cross_v = Entity(parent=camera.ui, model='quad', color=color.white, scale=(0.025,0.002))

def load_level_dict(filename):
    d = {}
    if not os.path.exists(filename):
        return d
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            coord, v = line.split(":")
            x,z = coord.split(",")
            d[(int(x), int(z))] = int(v)
            generated_set.add((int(x), int(z)))
    return d

def save_level_dict(filename, d):
    with open(filename, "w", encoding="utf8") as f:
        for ((x,z), val) in d.items():
            f.write(f"{x},{z}:{val}\n")

world0 = load_level_dict(FILE1)
world_1 = load_level_dict(FILE2)

def load_user():
    s = set()
    if not os.path.exists(USER_FILE):
        return s
    with open(USER_FILE,"r",encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x,y,z = map(int, line.split())
            s.add((x,y,z))
    return s

def save_user():
    with open(USER_FILE,"w",encoding="utf8") as f:
        for x,y,z in sorted(user_blocks):
            f.write(f"{x} {y} {z}\n")

def generate_square(center_x, center_z):
    cx = int(center_x)
    cz = int(center_z)
    half = SIZE // 2
    for ox in range(-half, half):
        for oz in range(-half, half):
            x = cx + ox
            z = cz + oz
            if (x,z) not in generated_set:
                world0[(x,z)] = 1
                world_1[(x,z)] = 1
                generated_set.add((x,z))
    save_level_dict(FILE1, world0)
    save_level_dict(FILE2, world_1)

def render_all():
    for k in list(block_map.keys()):
        destroy(block_map[k])
    block_map.clear()
    for ((x,z), v) in world0.items():
        if v == 1:
            e = Entity(position=(x, 0, z), model="cube", origin_y=0.5, collider="box", texture="white_cube")
            block_map[(x,0,z)] = e
    for ((x,z), v) in world_1.items():
        if v == 1:
            e = Entity(position=(x, -1, z), model="cube", origin_y=0.5, collider="box", texture="white_cube")
            block_map[(x,-1,z)] = e
    for (x,y,z) in user_blocks:
        e = Entity(position=(x,y,z), model="cube", origin_y=0.5, collider="box", texture="white_cube")
        block_map[(x,y,z)] = e

user_blocks = load_user()
render_all()

def load_pos():
    if not os.path.exists(POS_FILE):
        return (0, 12, 0)
    with open(POS_FILE, "r", encoding="utf8") as f:
        a,b,c = map(float, f.readline().split())
    return (a,b,c)

def save_pos(x,y,z):
    with open(POS_FILE, "w", encoding="utf8") as f:
        f.write(f"{x} {y} {z}")

start_x, start_y, start_z = load_pos()
player = FirstPersonController(position=(start_x, start_y, start_z))
player.cursor.enabled = False
mouse.locked = True
mouse.visible = False

def input(key):
    if key == "escape":
        application.quit()

last_center = None
left_click = False
right_click = False
def update():
    global left_click, right_click, last_center
    save_pos(player.x, player.y, player.z)
    px = int(player.x)
    pz = int(player.z)
    if last_center is None:
        generate_square(px, pz)
        last_center = (px, pz)
        render_all()
    else:
        dx = abs(px - last_center[0])
        dz = abs(pz - last_center[1])
        if dx >= SIZE//3 or dz >= SIZE//3:
            generate_square(px, pz)
            last_center = (px, pz)
            render_all()
    hit = raycast(camera.world_position, camera.forward, distance=MAX_DIST)
    if hit.hit:
        p = hit.entity.position
        nx, ny, nz = round(hit.normal.x), round(hit.normal.y), round(hit.normal.z)
        x0, y0, z0 = round(p.x), round(p.y), round(p.z)
        if mouse.right and not right_click:
            right_click = True
            key = (x0,y0,z0)
            if y0 == 0 and world0.get((x0,z0),0) == 1:
                world0[(x0,z0)] = 0
                save_level_dict(FILE1, world0)
                render_all()
            elif y0 == -1 and world_1.get((x0,z0),0) == 1:
                world_1[(x0,z0)] = 0
                save_level_dict(FILE2, world_1)
                render_all()
            elif key in user_blocks:
                user_blocks.remove(key)
                save_user()
                render_all()
        if mouse.left and not left_click:
            left_click = True
            nx2, ny2, nz2 = x0+nx, y0+ny, z0+nz
            user_blocks.add((nx2, ny2, nz2))
            save_user()
            render_all()
    if not mouse.right:
        right_click = False
    if not mouse.left:
        left_click = False

app.run()
