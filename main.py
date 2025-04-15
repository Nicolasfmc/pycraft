from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from pathlib import Path

app = Ursina()

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

player = FirstPersonController()
Sky()

boxes = []
for i in range(40):
    for j in range(40):
        box = Button(
            color=color.white,
            model='cube',
            position=(j, 0, i),
            texture=f'{texture_path}/grass_carried.png',
            parent=scene,
            origin_y=0.5
        )
        boxes.append(box)

menu_open = False

menu_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 180),
    scale=(0.5, 0.4),
    enabled=False
)

def toggle_menu(state):
    global menu_open
    menu_open = state
    menu_bg.enabled = state
    mouse.locked = not state
    player.enabled = not state

btn_continue = Button(
    text='Continuar',
    color=color.azure,
    scale=(0.4, 0.1),
    position=(0, 0.05),
    parent=menu_bg,
    on_click=lambda: toggle_menu(False)
)

btn_exit = Button(
    text='Sair',
    color=color.red,
    scale=(0.4, 0.1),
    position=(0, -0.1),
    parent=menu_bg,
    on_click=application.quit
)

hotbar_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.clear,
    scale=(1, 1),
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
            model='quad',
            text='',
            scale=(0.12, 0.12),
            position=(start_x + i*spacing, 0),
            color=color.clear,
            highlight_color=color.clear,
            pressed_color=color.clear
        )
        
        icon = Sprite(
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
    global menu_open, selected_block_index

    if key == 'escape':
        toggle_menu(not menu_open)

    if not menu_open:
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
                if key == 'right mouse down':
                    new_block = Button(
                        color=color.white,
                        model='cube',
                        position=box.position + mouse.normal,
                        texture=get_current_block_texture(),
                        parent=scene,
                        origin_y=0.5
                    )
                    boxes.append(new_block)
                if key == 'left mouse down':
                    boxes.remove(box)
                    destroy(box)

app.run()
