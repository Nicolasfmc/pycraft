from ursina import Ursina, Entity, Button, Sprite, Sky, color, window, camera, scene, mouse, destroy
from ursina.prefabs.first_person_controller import FirstPersonController
from pathlib import Path
from menu import GameMenu

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
for i in range(40):
    for j in range(40):
        box = Entity(
            parent=scene,
            model='cube',
            position=(j, 0, i),
            texture=f'{texture_path}/grass_carried.png',
            origin_y=0.5,
            collider='box',
            color=color.white
        )
        boxes.append(box)

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

app.run()
