from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
player = FirstPersonController()
Sky()

boxes = []
menu_open = False

for i in range(40):
  for j in range(40):
    box = Button(color=color.white, model='cube', position=(j, 0, i),
                 texture='grass.png', parent=scene, origin_y=0.5)
    boxes.append(box)

    menu_bg = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 180),
                     scale=(0.5, 0.4), enabled=False)

    btn_continue = Button(text='Continuar', color=color.azure, scale=(0.4, 0.1),
                          position=(0, 0.05), parent=menu_bg,
                          on_click=lambda: toggle_menu(False))
    btn_exit = Button(text='Sair', color=color.red, scale=(0.4, 0.1),
                      position=(0, -0.1), parent=menu_bg,
                      on_click=application.quit)

def toggle_menu(state):
  global menu_open
  menu_open = state
  menu_bg.enabled = state
  mouse.locked = not state
  player.enabled = not state

def input(key):
  if key == 'escape':
  toggle_menu(not menu_open)

if not menu_open:
    for box in boxes:
        if box.hovered:
            if key == 'right mouse down':
                new = Button(color=color.white, model='cube', position=box.position + mouse.normal,
                             texture='grass.png', parent=scene, origin_y=0.5)
                boxes.append(new)
            if key == 'left mouse down':
                boxes.remove(box)
                destroy(box)

app.run()