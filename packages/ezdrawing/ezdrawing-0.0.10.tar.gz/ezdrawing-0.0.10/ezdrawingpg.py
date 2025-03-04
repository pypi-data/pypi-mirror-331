import math
import pygame

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

def validate_font(font_name, name = "font_name"):
    validate_string(font_name, name)
    if not font_name in pygame.font.get_fonts():
        raise Exception(f"{name} ({font_name}) was not found in the system fonts. Valid fonts can be found with getFonts()")

def validate_image_extension(path, name = "path"):
    if type(path) != str:
        raise Exception(f"{name} is not a string (it is {type(path)})")
    
    try:
        extensionIndex = path.rindex(".")
    except:
        raise Exception(f"{name} does not have a file extension")
    extension = path[extensionIndex:].lower()
    if not extension in [".bmp", ".tga", ".jpeg", ".png"]:
        raise Exception(f"{name} does not have a valid file extension (extension is {extension}). Valid extensions are .bmp, .tga, .jpeg, .png")

#undo/update stuff
can_undo_ = False
def can_undo():
    global can_undo_
    return can_undo_

def update_old_window():
    global can_undo_, window, window_surface_old
    window_surface_old.blit(window, (0, 0))
    can_undo_ = True
    
def undo():
    global can_undo_
    global window, window_surface_old
    window.blit(window_surface_old, (0, 0))
    can_undo_ = False

def update():
    pygame.display.flip()

#drawing stuff
def draw_rect(color, top_left, bottom_right, validate = True, undoable = True):
    global window
    if validate:
        validate_color(color)
        validate_rect(top_left, bottom_right)
    
    if undoable:
        update_old_window()
    
    pygame.draw.rect(window, color, (*top_left, bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))

def draw_ellipse(color, top_left, bottom_right, validate = True, undoable = True):
    global window
    if validate:
        validate_color(color)
        validate_rect(top_left, bottom_right)
    
    if undoable:
        update_old_window()
    
    big = pygame.Surface(((bottom_right[0] - top_left[0]) * 4, (bottom_right[1] - top_left[1]) * 4), pygame.SRCALPHA)
    pygame.draw.ellipse(big, color, (0, 0, (bottom_right[0] - top_left[0]) * 4, (bottom_right[1] - top_left[1]) * 4))
    small = pygame.transform.smoothscale(big, (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))
    window.blit(small, top_left, special_flags=pygame.BLEND_PREMULTIPLIED)
    
def draw_line(color, point_a, point_b, width, validate = True, undoable = True):
    global window
    if validate:
        validate_color(color)
        validate_2_tuple_of_ints(point_a, "point_a")
        validate_2_tuple_of_ints(point_b, "point_b")
        validate_integer_in_range(width, "width", 0)
    
    if undoable:
        update_old_window()
    
    if point_a == point_b: #avoid division by 0 by just not drawing anything
        return

    #this is going to be drawn to a 4x supersampled surface, so make everything big
    offset = (point_b[0] - point_a[0], point_b[1] - point_a[1]) #vector from pointA to pointB
    offset = (-offset[1], offset[0]) #rotate 90 degrees
    len = (offset[0] ** 2 + offset[1] ** 2) ** 0.5
    offset = ((offset[0] * width * 2) / len, 
            (offset[1] * width * 2) / len) #normalize and multiply by 4 * width / 2
    offset = (round(offset[0]), round(offset[1])) #round
    
    point_vec = ((point_b[0] - point_a[0]) * 4, (point_b[1] - point_a[1]) * 4) #vector from pointA to pointB but big
    points = [(offset[0], offset[1]), (-offset[0], -offset[1]), #the points, but with some negative coordinates
              (point_vec[0] - offset[0], point_vec[1] - offset[1]),
              (point_vec[0] + offset[0], point_vec[1] + offset[1])]
    min_point = (min([i[0] for i in points]), min([i[1] for i in points]))
    points_moved = [(i[0] - min_point[0], i[1] - min_point[1]) for i in points] #now all have positive coordinates
    bigSurfaceSize = (max([i[0] for i in points_moved]), max([i[1] for i in points_moved])) #the size that the big surface has to be
    big = pygame.Surface(bigSurfaceSize, pygame.SRCALPHA)
    pygame.draw.polygon(big, color, points_moved) #draw the line to the big surface
    small = pygame.transform.smoothscale(big, (round(bigSurfaceSize[0] / 4), round(bigSurfaceSize[1] / 4))) #scale it down
    blit_offset = (round(min_point[0] / 4), round(min_point[1] / 4)) #because all the point coords had to be positive, when blitting the points need to be offset
    window.blit(small, (point_a[0] + blit_offset[0], point_a[1] + blit_offset[1]), special_flags=pygame.BLEND_PREMULTIPLIED) #blit
    
    
def draw_capped_line(color, point_a, point_b, width, validate = True, undoable = True):
    if validate:
        validate_color(color)
        validate_2_tuple_of_ints(point_a, "point_a")
        validate_2_tuple_of_ints(point_b, "point_b")
        validate_integer_in_range(width, "width", 0)
    
    if undoable:
        update_old_window()
    
    draw_line(color, point_a, point_b, width, False, False)
    if width <= 1: #drawing the cap ellipses makes the line look thicker than it should
        return
    half_width = math.floor(width / 2)
    draw_ellipse(color, (point_a[0] - half_width, point_a[1] - half_width),
                        (point_a[0] + half_width, point_a[1] + half_width), False, False)
    draw_ellipse(color, (point_b[0] - half_width, point_b[1] - half_width),
                        (point_b[0] + half_width, point_b[1] + half_width), False, False)

def draw_text(color, position, text, font_name, size):
    global window
    validate_string(text, "text")
    validate_font(font_name, "font_name")
    validate_integer_in_range(size, "size", 1)
    validate_2_tuple_of_ints(position, "position")
    validate_color(color, "color")
    
    update_old_window()
    
    font = pygame.font.SysFont(font_name, size)
    surface = font.render(text, False, color)
    window.blit(surface, position)  

def get_fonts():
    return pygame.font.get_fonts()

#input/event handling stuff
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            handle_quit_event(event)
        elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            handle_key_button_event(event)
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event)
        elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            handle_mouse_button_event(event)

should_quit_ = False
def handle_quit_event(event):
    global should_quit_
    should_quit_ = True

def should_quit():
    global should_quit_
    handle_events()
    return should_quit_

pressed_key_events = []
def handle_key_button_event(event):
    global pressed_key_events
    i = 0
    while i < len(pressed_key_events):
        if event.key == pressed_key_events[i].key:
            pressed_key_events.pop(i)
            i -= 1
        i += 1
    if event.type == pygame.KEYDOWN:
        pressed_key_events.append(event) #add it so it's the latest (as it should be)

def get_pressed_keys():
    global pressed_key_events
    handle_events()
    key_strings = []
    for event in pressed_key_events:
        key_strings.append(pygame.key.name(event.key))
    return key_strings

def get_possible_keys():
    possible_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, 
                     pygame.K_AC_BACK, pygame.K_AMPERSAND, pygame.K_ASTERISK, pygame.K_AT, 
                     pygame.K_BACKQUOTE, pygame.K_BACKSLASH, pygame.K_BACKSPACE, pygame.K_BREAK, 
                     pygame.K_CAPSLOCK, pygame.K_CARET, pygame.K_CLEAR, pygame.K_COLON, 
                     pygame.K_COMMA, pygame.K_CURRENCYSUBUNIT, pygame.K_CURRENCYUNIT, 
                     pygame.K_DELETE, pygame.K_DOLLAR, pygame.K_DOWN, pygame.K_END, 
                     pygame.K_EQUALS, pygame.K_ESCAPE, pygame.K_EURO, pygame.K_EXCLAIM, 
                     pygame.K_F1, pygame.K_F10, pygame.K_F11, pygame.K_F12, pygame.K_F13, 
                     pygame.K_F14, pygame.K_F15, pygame.K_F2, pygame.K_F3, pygame.K_F4, 
                     pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9, 
                     pygame.K_GREATER, pygame.K_HASH, pygame.K_HELP, pygame.K_HOME, 
                     pygame.K_INSERT, pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, 
                     pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, 
                     pygame.K_KP9, pygame.K_KP_0, pygame.K_KP_1, pygame.K_KP_2, pygame.K_KP_3, 
                     pygame.K_KP_4, pygame.K_KP_5, pygame.K_KP_6, pygame.K_KP_7, pygame.K_KP_8, 
                     pygame.K_KP_9, pygame.K_KP_DIVIDE, pygame.K_KP_ENTER, pygame.K_KP_EQUALS, 
                     pygame.K_KP_MINUS, pygame.K_KP_MULTIPLY, pygame.K_KP_PERIOD, pygame.K_KP_PLUS, 
                     pygame.K_LALT, pygame.K_LCTRL, pygame.K_LEFT, pygame.K_LEFTBRACKET, 
                     pygame.K_LEFTPAREN, pygame.K_LESS, pygame.K_LGUI, pygame.K_LMETA, 
                     pygame.K_LSHIFT, pygame.K_LSUPER, pygame.K_MENU, pygame.K_MINUS, 
                     pygame.K_MODE, pygame.K_NUMLOCK, pygame.K_NUMLOCKCLEAR, pygame.K_PAGEDOWN, 
                     pygame.K_PAGEUP, pygame.K_PAUSE, pygame.K_PERCENT, pygame.K_PERIOD, 
                     pygame.K_PLUS, pygame.K_POWER, pygame.K_PRINT, pygame.K_PRINTSCREEN, 
                     pygame.K_QUESTION, pygame.K_QUOTE, pygame.K_QUOTEDBL, pygame.K_RALT, 
                     pygame.K_RCTRL, pygame.K_RETURN, pygame.K_RGUI, pygame.K_RIGHT, 
                     pygame.K_RIGHTBRACKET, pygame.K_RIGHTPAREN, pygame.K_RMETA, pygame.K_RSHIFT, 
                     pygame.K_RSUPER, pygame.K_SCROLLLOCK, pygame.K_SCROLLOCK, pygame.K_SEMICOLON, 
                     pygame.K_SLASH, pygame.K_SPACE, pygame.K_SYSREQ, pygame.K_TAB, pygame.K_UNDERSCORE, 
                     pygame.K_UNKNOWN, pygame.K_UP, pygame.K_a, pygame.K_b, pygame.K_c, 
                     pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, 
                     pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, 
                     pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, 
                     pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, 
                     pygame.K_x, pygame.K_y, pygame.K_z]
    return [pygame.key.name(key) for key in possible_keys]

mouse_pos = (0, 0)
def handle_mouse_motion(event):
    global mouse_pos
    mouse_pos = (int(event.pos[0]), int(event.pos[1]))

def get_mouse_pos():
    global mouse_pos
    handle_events()
    return mouse_pos

pressed_mouse_button_events = []
def handle_mouse_button_event(event):
    global pressed_mouse_button_events
    i = 0
    while i < len(pressed_mouse_button_events):
        if event.button == pressed_mouse_button_events[i].button:
            pressed_mouse_button_events.pop(i)
            i -= 1
        i += 1
    if event.type == pygame.MOUSEBUTTONDOWN:
        pressed_mouse_button_events.append(event) #add it so it's the latest (as it should be)

def get_pressed_mouse_buttons():
    global pressed_mouse_button_events
    handle_events()
    buttons = []
    for event in pressed_mouse_button_events:
        buttons.append(event.button)
    return buttons

#saving
def save(path):
    global window
    
    validate_image_extension(path)
    
    pygame.image.save(window, path)

#initialization stuff
window = None
window_surface_old = None
opened = False
def open_window(window_size, title = "My Ezdrawing Window"):
    global window, window_surface_old, opened
    validate_2_tuple_of_ints(window_size, "window_size")
    for i in range(2):
        validate_integer_in_range(window_size[i], f"window_size[{i}]", 1)
    validate_string(title, "title")
    
    pygame.init()

    window = pygame.display.set_mode(window_size)
    window.fill((255, 255, 255))
    pygame.display.set_caption(title)

    window_surface_old = pygame.Surface(window_size)
    update_old_window()

    pygame.display.flip()
    
    opened = True

def quit():
    pygame.quit()