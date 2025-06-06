from ursina import Ursina, Entity, Button, Sprite, Sky, color, window, camera, scene, mouse, destroy
from ursina.prefabs.first_person_controller import FirstPersonController
from pathlib import Path
import math
from menu import GameMenu
from ursina import invoke, Audio, time, application

app = Ursina()

fullscreen_state = [False]

def toggle_fullscreen():
    window.fullscreen = not window.fullscreen
    fullscreen_state[0] = window.fullscreen

texture_path = Path('textures/blocks/').as_posix()

block_types = [
    ('Grama', 'grass_carried.png'),
    ('Tábua de Madeira', 'planks_birch.png'),
    ('Pedra', 'stone.png'),
    ('Terra', 'dirt.png'),
]

selected_block_index = 0

def get_current_block_texture():
    return f'{texture_path}/{block_types[selected_block_index][1]}'

Sky()

boxes = []
occupied_positions = set()
for i in range(40):
    for j in range(40):
        pos = (j, 0, i)
        box = Entity(
            parent=scene,
            model='cube',
            position=pos,
            texture=f'{texture_path}/grass_carried.png',
            origin_y=0.5,
            collider='box',
            color=color.white
        )
        boxes.append(box)
        occupied_positions.add(pos)

highlighted_box = [None]
def highlight_box(box):
    if highlighted_box[0] and highlighted_box[0] != box:
        highlighted_box[0].color = color.white
    box.color = color.rgba(255,255,255,255)
    highlighted_box[0] = box

def unhighlight_box(box):
    box.color = color.white
    if highlighted_box[0] == box:
        highlighted_box[0] = None

player = FirstPersonController()
spawn_point = (player.x, player.y, player.z)

menu = None

def on_menu_toggle(state):
    pass

menu = GameMenu(player, on_menu_toggle, toggle_fullscreen)

hotbar_bg = Entity(
    parent=camera.ui,
    position=(0, -0.4)
)

hotbar_slots = []

def create_hotbar_ui():
    """Cria slots (transparentes) e ícones para exibir o hotbar na tela."""
    spacing = 0.18
    start_x = -(len(block_types)-1) * spacing / 2
    
    for i, (block_name, block_texture) in enumerate(block_types):
        slot = Button(
            parent=hotbar_bg,
            text='',
            scale=(0.12, 0.12),
            position=(start_x + i*spacing, 0),
            highlight_color=color.clear,
            pressed_color=color.clear
        )
        Sprite(
            parent=slot,
            texture=f'{texture_path}/{block_texture}',
            scale=0.8,
            position=(0, 0, -0.1)
        )
        hotbar_slots.append(slot)

def update_hotbar_ui():
    """Destaca o slot selecionado (opcional)."""
    for i, slot in enumerate(hotbar_slots):
        if i == selected_block_index:
            slot.color = color.rgba(255,255,255,80)
        else:
            slot.color = color.clear

create_hotbar_ui()
update_hotbar_ui()

flash = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(255,255,255,0),
    scale=(2,2),
    z=-100,
    enabled=True
)

def respawn_flash():
    flash.color = color.rgba(255,255,255,180)
    Audio('sounds/damage.mp3', autoplay=True)
    invoke(lambda *_: setattr(flash, 'color', color.rgba(255,255,255,0)), 0.25)

walk_audio = Audio('sounds/walk-sound.mp3', loop=False, autoplay=False)
walk_cooldown = [0.0]

def input(key):
    global selected_block_index

    if key == 'escape':
        if menu:
            menu.toggle_menu(not menu.menu_open)
        return

    if menu and not menu.menu_open:
        if key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < len(block_types):
                selected_block_index = idx
                update_hotbar_ui()

        if key == 'scroll up':
            selected_block_index = (selected_block_index + 1) % len(block_types)
            update_hotbar_ui()
        elif key == 'scroll down':
            selected_block_index = (selected_block_index - 1) % len(block_types)
            update_hotbar_ui()

        for box in boxes:
            if box.hovered:
                highlight_box(box)
                if key == 'right mouse down':
                    new_block = Entity(
                        parent=scene,
                        model='cube',
                        position=box.position + mouse.normal,
                        texture=get_current_block_texture(),
                        origin_y=0.5,
                        collider='box',
                        color=color.white
                    )
                    boxes.append(new_block)
                if key == 'left mouse down':
                    boxes.remove(box)
                    destroy(box)
            else:
                unhighlight_box(box)

def generate_blocks_around_player(radius=5):
    px, py, pz = int(round(player.x)), int(round(player.y)), int(round(player.z))
    for dx in range(-radius, radius+1):
        for dz in range(-radius, radius+1):
            x, z = px+dx, pz+dz
            pos = (x, 0, z)
            if pos not in occupied_positions:
                box = Entity(
                    parent=scene,
                    model='cube',
                    position=pos,
                    texture=f'{texture_path}/grass_carried.png',
                    origin_y=0.5,
                    collider='box',
                    color=color.white
                )
                boxes.append(box)
                occupied_positions.add(pos)

def update():
    if player.y < spawn_point[1] - 64:
        player.position = spawn_point
        respawn_flash()
    generate_blocks_around_player(radius=5)
    moving = False
    if hasattr(player, 'input_direction'):
        moving = player.input_direction.magnitude() > 0.1
    on_ground = player.grounded if hasattr(player, 'grounded') else player.y <= 1
    dt = 1/60 
    if player.enabled and moving and on_ground:
        walk_cooldown[0] -= dt
        if walk_cooldown[0] <= 0:
            walk_audio.play()
            walk_cooldown[0] = 0.45
    else:
        walk_cooldown[0] = 0.0
        walk_audio.stop()

app.run()
