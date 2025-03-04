import math
import sys
try:
    import tkinter as tk
except ImportError:
    sys.exit("Tkinter not found")

#parameter validation
def validate_initialized():
    global opened
    if not opened:
        raise Exception("ezdrawing is not initialized. Call init() to initialize")

def validate_integer_in_range(integer, integer_name = "integer", low = None, high = None):
    if type(integer) != int:
        raise Exception(f"{integer_name} is not an integer (it is {type(integer)})")
    if low != None and high != None:
        if integer < low or integer > high:
            raise Exception(f"{integer_name} is outside the range {low}-{high} (it is {integer})")
    elif low != None:
        if integer < low:
            raise Exception(f"{integer_name} is less than {low} (it is {integer})")
    elif high != None:
        if integer > high:
            raise Exception(f"{integer_name} is more than {high} (it is {integer})")

def validate_color(color, name = "color"):
    if type(color) != tuple:
        raise Exception(f"{name} is not a tuple (it is {type(color)})")
    if len(color) != 3:
        raise Exception(f"{name} is not a tuple of 3 values (has {len(color)} values)")
    for i in range(3):
        validate_integer_in_range(color[i], f"{name}[{i}]", 0, 255)

def validate_2_tuple_of_ints(pos, name = "pos"):
    if type(pos) != tuple:
        raise Exception(f"{name} is not a tuple (it is {type(pos)})")
    if len(pos) != 2:
        raise Exception(f"{pos} is not a tuple of 2 values (has {len(pos)} values)")
    for i in range(2):
        validate_integer_in_range(pos[i], f"{name}[{i}]")

def validate_rect(top_left, bottom_right, top_left_name = "top_left", bottom_right_name = "bottom_right"):
    validate_2_tuple_of_ints(top_left, top_left_name)
    validate_2_tuple_of_ints(bottom_right, bottom_right_name)
    if(top_left[0] > bottom_right[0]):
        raise Exception(f"{top_left_name} is to the right of {bottom_right_name} (x={top_left[0]} vs x={bottom_right[0]})")
    if(top_left[1] > bottom_right[1]):
        raise Exception(f"{top_left_name} is below of {bottom_right_name} (y={top_left[1]} vs y={bottom_right[1]})")

def validate_string(string, name = "string"):
    if type(string) != str:
        raise Exception(f"{name} is not a string (it is {type(string)})")

#utility
def to_color_string(color, validate = True):
    if validate:
        validate_color(color)

    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

#undo stuff
objects = []
canvas = None
def undo():
    global objects
    if len(objects) == 0:
        return
    todelete = objects.pop()
    if type(todelete) == int:
        canvas.delete(todelete)
    else: #tuple of ints
        for id in todelete:
            canvas.delete(id)

#drawing stuff
def draw_rect(color, top_left, bottom_right, validate = True):
    global canvas, objects
    if validate:
        validate_color(color)
        validate_rect(top_left, bottom_right)
    
    id = canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1], fill=to_color_string(color, False), width=0)
    objects.append(id)

def draw_ellipse(color, top_left, bottom_right, validate = True, undoable = True):
    global canvas, objects
    if validate:
        validate_color(color)
        validate_rect(top_left, bottom_right)
    
    id = canvas.create_oval(top_left[0], top_left[1], bottom_right[0], bottom_right[1], fill=to_color_string(color, False), width=0)
    objects.append(id)
    
def draw_line(color, point_a, point_b, width, validate = True, undoable = True):
    global canvas, objects
    if validate:
        validate_color(color)
        validate_2_tuple_of_ints(point_a, "point_a")
        validate_2_tuple_of_ints(point_b, "point_b")
        validate_integer_in_range(width, "width", 0)

    id = canvas.create_line(point_a[0], point_a[1], point_b[0], point_b[1], fill=to_color_string(color, False), width=width)
    objects.append(id)
    
    
def draw_capped_line(color, point_a, point_b, width, validate = True, undoable = True):
    global canvas, objects
    if validate:
        validate_color(color)
        validate_2_tuple_of_ints(point_a, "point_a")
        validate_2_tuple_of_ints(point_b, "point_b")
        validate_integer_in_range(width, "width", 0)
    
    id1 = canvas.create_line(point_a[0], point_a[1], point_b[0], point_b[1], fill=to_color_string(color, False), width=width)
    
    if width <= 1: #drawing the cap ellipses makes the line look thicker than it should
        return
    half_width = math.floor(width / 2)
    id2 = canvas.create_oval(point_a[0] - half_width, point_a[1] - half_width, point_a[0] + half_width, point_a[1] + half_width, fill=to_color_string(color, False), width=0)
    id3 = canvas.create_oval(point_b[0] - half_width, point_b[1] - half_width, point_b[0] + half_width, point_b[1] + half_width, fill=to_color_string(color, False), width=0)
    objects.append((id1, id2, id3))

def should_quit():
    global window
    try:
        return not window.state() == "normal"
    except: #window is closed already
        return True

pressed_keys = []
def handle_key_press(event):
    global pressed_keys
    i = 0
    while i < len(pressed_keys):
        if event.char == pressed_keys[i]:
            pressed_keys.pop(i)
            i -= 1
        i += 1
    pressed_keys.append(event.char)

def handle_key_release(event):
    global pressed_keys
    i = 0
    while i < len(pressed_keys):
        if event.char == pressed_keys[i]:
            pressed_keys.pop(i)
            i -= 1
        i += 1

def get_pressed_keys():
    global pressed_keys
    return pressed_keys

mouse_pos = (0, 0)
def handle_mouse_motion(event):
    global mouse_pos
    mouse_pos = (event.x, event.y)

def get_mouse_pos():
    global mouse_pos
    return mouse_pos

pressed_mouse_buttons = []
def handle_mouse_button_press(num):
    global pressed_mouse_buttons
    i = 0
    while i < len(pressed_mouse_buttons):
        if num == pressed_mouse_buttons[i]:
            pressed_mouse_buttons.pop(i)
            i -= 1
        i += 1
    pressed_mouse_buttons.append(num)

def handle_mouse_button_release(num):
    global pressed_mouse_buttons
    i = 0
    while i < len(pressed_mouse_buttons):
        if num == pressed_mouse_buttons[i]:
            pressed_mouse_buttons.pop(i)
            i -= 1
        i += 1

def get_pressed_mouse_buttons():
    global pressed_mouse_buttons
    return pressed_mouse_buttons

valid_extensions = [".bmp", ".jpg", ".png"]
def validate_image_extension(path, name = "path"):
    global valid_extensions
    if type(path) != str:
        raise Exception(f"{name} is not a string (it is {type(path)})")
    
    try:
        extensionIndex = path.rindex(".")
    except:
        raise Exception(f"{name} does not have a file extension")
    extension = path[extensionIndex:].lower()
    if not extension in valid_extensions:
        raise Exception(f"{name} does not have a valid file extension (extension is {extension}). Valid extensions are {valid_extensions.join(', ')}")

#initialization stuff
window = None
canvas = None
objects = []
opened = False
def open_window(window_size, title = "My Ezdrawing Window"):
    global window, canvas, opened
    validate_2_tuple_of_ints(window_size, "window_size")
    for i in range(2):
        validate_integer_in_range(window_size[i], f"window_size[{i}]", 1)
    validate_string(title, "title")
    
    window = tk.Tk()
    window.geometry(f"{window_size[0]}x{window_size[1]}")
    window.title(title)
    
    canvas = tk.Canvas(window, width=window_size[0], height=window_size[1])
    canvas.configure(bg="white")
    canvas.pack()
    
    window.bind("<Key>", handle_key_press)
    window.bind("<KeyRelease>", handle_key_release)
    window.bind("<Motion>", handle_mouse_motion)
    window.bind("<Button-1>", lambda __: handle_mouse_button_press(1))
    window.bind("<ButtonRelease-1>", lambda __: handle_mouse_button_release(1))
    window.bind("<Button-2>", lambda __: handle_mouse_button_press(2))
    window.bind("<ButtonRelease-2>", lambda __: handle_mouse_button_release(2))
    window.bind("<Button-3>", lambda __: handle_mouse_button_press(3))
    window.bind("<ButtonRelease-3>", lambda __: handle_mouse_button_release(3))
    
    opened = True

def update():
    global window
    window.update()

def quit():
    pass #does nothing, but is here for consistency. tkinter window quits automatically after the mainloop is broken