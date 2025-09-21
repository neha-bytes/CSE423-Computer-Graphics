#TASK 01
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

w_width, w_height = 500, 450
raindrops = []
num_raindrops = 200
house_c = [0.8, 0.6, 0.1]  
roof_c = [0.8, 0.3, 0.2]   
ground_c = [0.3, 0.9, 0.3]  
door_c = [0.4, 0.2, 0.1]    
window_c = [0.6, 0.3, 0.1]  
rain_angle = 0 
rain_speed = 5
bg_c = [0.0, 0.0, 0.1]  
day_night_factor = 0.0  

RAINDROP_X = 0
RAINDROP_Y = 1
RAINDROP_SPEED = 2
def init():
    glClearColor(bg_c[0], bg_c[1], bg_c[2], 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-w_width/2, w_width/2, -w_height/2, w_height/2)
    initialize_raindrops()
def initialize_raindrops():
    for _ in range(num_raindrops):
        raindrops.append([
            random.uniform(-w_width/2, w_width/2),    #X
            random.uniform(-w_height/2, w_height/2),   #Y
            random.uniform(3, 7)
        ])
def draw_house():
    draw_roof()
    draw_house_base()
    draw_door()
    draw_windows()
    

def draw_windows():
    glColor3f(*window_c)
    draw_left_window()
    draw_right_window()

def draw_left_window():
    glBegin(GL_TRIANGLES)
    glVertex2f(-65, -45)
    glVertex2f(-35, -45)
    glVertex2f(-35, -15)
    glVertex2f(-65, -45)
    glVertex2f(-65, -15)
    glVertex2f(-35, -15)
    glEnd()
def draw_right_window():
    glBegin(GL_TRIANGLES)
    glVertex2f(40, -45)
    glVertex2f(70, -45)
    glVertex2f(70, -15)
    glVertex2f(40, -45)
    glVertex2f(40, -15)
    glVertex2f(70, -15)
    glEnd()

def draw_door():
    glColor3f(*door_c)
    glBegin(GL_TRIANGLES)
    glVertex2f(-30, -100)
    glVertex2f(30, -100)
    glVertex2f(30, 0)
    glVertex2f(-30, -100)
    glVertex2f(-30, 0)
    glVertex2f(30, 0)
    glEnd()

def draw_roof():
    glBegin(GL_TRIANGLES)
    glColor3f(*roof_c)
    glVertex2f(-120, 50)
    glVertex2f(0, 120)
    glVertex2f(120, 50)
    glEnd()

def draw_house_base():
    glBegin(GL_TRIANGLES)
    glColor3f(*house_c)
    glVertex2f(-100, -100)
    glVertex2f(100, -100)
    glVertex2f(100, 50)
    glVertex2f(-100, -100)
    glVertex2f(-100, 50)
    glVertex2f(100, 50)
    glEnd()

def draw_door():
    glColor3f(*door_c)
    glBegin(GL_TRIANGLES)
    glVertex2f(-20, -90)
    glVertex2f(20, -90)
    glVertex2f(20, -10)
    glVertex2f(-20, -90)
    glVertex2f(-20, -10)
    glVertex2f(20, -10)
    glEnd()

def draw_ground():
    glColor3f(*ground_c)
    glBegin(GL_TRIANGLES)
    glVertex2f(-w_width/2, -w_height/2)
    glVertex2f(w_width/2, -w_height/2)
    glVertex2f(w_width/2, -100) 
    glVertex2f(-w_width/2, -w_height/2)
    glVertex2f(-w_width/2, -100)
    glVertex2f(w_width/2, -100)
    glEnd()

def draw_rain():
    rain_color = get_rain_color()
    glColor3f(*rain_color)
    glBegin(GL_LINES)
    for raindrop in raindrops:
        draw_raindrop(raindrop)
    glEnd()

def get_rain_color():
    base_c = [0.7, 0.7, 1.0]  #light blue
    if day_night_factor < 0.6:
        return [0.9, 0.9, 1.0]   #brighter at night
    return base_c

def draw_raindrop(raindrop):
    x_pos, y_pos = raindrop[RAINDROP_X], raindrop[RAINDROP_Y]
    end_x = x_pos + rain_angle * 15
    end_y = y_pos - 15
    glVertex2f(x_pos, y_pos)
    glVertex2f(end_x, end_y)

def update_rain():
    for raindrop in raindrops:
        update_raindrop_position(raindrop)
        reset_raindrop_if_offscreen(raindrop)

def update_raindrop_position(raindrop):
    raindrop[RAINDROP_Y] -= raindrop[RAINDROP_SPEED]  
    raindrop[RAINDROP_X] += rain_angle * raindrop[RAINDROP_SPEED]

def reset_raindrop_if_offscreen(raindrop):
    if raindrop[RAINDROP_Y] < -w_height/2:
        horizontal_offset = abs(rain_angle) * w_height
        raindrop[RAINDROP_Y] = w_height/2
        raindrop[RAINDROP_X] = random.uniform(-w_width/2 - horizontal_offset, w_width/2 + horizontal_offset)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  #clear screen
    glClearColor(bg_c[0], bg_c[1], bg_c[2], 1.0)      #bg screen
    draw_rain()
    draw_ground()
    draw_house()
    glutSwapBuffers()

def timer(value):
    update_rain()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  

def specialKeyListener(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT:
        adjust_rain_angle(-0.08)
        print("Rain going left")
    elif key == GLUT_KEY_RIGHT:
        adjust_rain_angle(0.08)
        print("Rain going right")
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global day_night_factor
    if key == b'd':
        adjust_day_night_factor(-0.08)
        print("Getting darker")
    elif key == b'l':
        adjust_day_night_factor(0.08)
        print("Getting lighter")
    glutPostRedisplay()
    
def adjust_rain_angle(delta):
    global rain_angle
    rain_angle += delta
    rain_angle = max(-0.8, min(0.8, rain_angle))

def adjust_day_night_factor(delta):
    global day_night_factor, bg_color
    day_night_factor += delta
    day_night_factor = max(0.0, min(1.0, day_night_factor))
    update_colors()

def update_colors():
    global bg_c
    if day_night_factor < 0.8:
        update_night_colors()
    else:
        update_day_colors()

def update_night_colors():
    global bg_c
    d_lvl = 1.0 - day_night_factor * 2
    bg_c[0] = 0.0
    bg_c[1] = 0.0
    bg_c[2] = 0.5 * (1 - d_lvl) + 0.1 * d_lvl

def update_day_colors():
    global bg_c
    b_lvl = (day_night_factor - 0.5) * 2
    bg_c[0] = 0.0 * (1 - b_lvl) + 0.5 * b_lvl
    bg_c[1] = 0.5 * (1 - b_lvl) + 0.7 * b_lvl
    bg_c[2] = 0.5 * (1 - b_lvl) + 1.0 * b_lvl

def main():
    glutInit()
    glutInitWindowSize(w_width, w_height)
    glutInitWindowPosition(100, 100)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow(b"House under the Rainfall")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutTimerFunc(16, timer, 0)
    glutMainLoop()
if __name__ == "__main__":
    main()


#TASK 02
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
from dataclasses import dataclass

w_width, w_height = 700, 700 
b_left = -w_width/2
b_right = w_width/2
b_bottom = -w_height/2
b_top = w_height/2      #boundary
dots = []  
base_vel = 1.5
vel_multiplier = 1.5
particle_size = 5.5
simulation_paused = False
blinking_enabled = False
blink_timer = 0

@dataclass
class Particle:
    x: float
    y: float
    dx: float  #direction/speed
    dy: float
    color: list
    blink: bool
    basic_color: list

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-w_width/2, w_width/2, -w_height/2, w_height/2) #2D view
    glPointSize(particle_size)

def get_particle_color(particle):
    if blinking_enabled and particle.blink:
        if blink_timer < 30:  
            return particle.color
        else:
            return [0.0, 0.0, 0.0] #invisible
    return particle.color

def draw_points():
    glBegin(GL_POINTS)
    
    for particle in dots:
        color = get_particle_color(particle)
        glColor3f(*color)
        glVertex2f(particle.x, particle.y)
    
    glEnd()

def update_blink_timer():
    global blink_timer
    blink_timer = (blink_timer + 1) % 60  

def updated_position(particle):  #new position
    new_x = particle.x + particle.dx * vel_multiplier
    new_y = particle.y + particle.dy * vel_multiplier
    return new_x, new_y

def update_particles():
    if simulation_paused:
        return   #nothing
    update_blink_timer()

    for particle in dots:
        new_x, new_y = updated_position(particle)  #boundary collision
        new_x, new_y, new_dx, new_dy = boundary_collision(particle, new_x, new_y)
        particle.x = new_x
        particle.y = new_y
        particle.dx = new_dx
        particle.dy = new_dy


def boundary_collision(particle, new_x, new_y):
    dx = particle.dx
    dy = particle.dy 
    if new_x <= b_left or new_x >= b_right:   #reverse direction hitting horizontal boundary
        dx = -dx
        new_x = particle.x + dx * vel_multiplier
    if new_y <= b_bottom or new_y >= b_top:     #reverse direction hitting horizontal boundary
        dy = -dy
        new_y = particle.y + dy * vel_multiplier
    
    return new_x, new_y, dx, dy

def display():   #callback
    glClear(GL_COLOR_BUFFER_BIT)
    draw_points()
    glutSwapBuffers()

def create_dots(x, y):
    color = random_color()
    dx, dy = random_direction(base_vel)
    new_particle = Particle(
        x=x,
        y=y,
        dx=dx,
        dy=dy,
        color=color,
        blink=True,
        basic_color=color.copy()
    )
    dots.append(new_particle)

def random_color():
    return [random.random(), random.random(), random.random()]

def random_direction(speed):
    dx = random.choice([-2, 2]) * speed
    dy = random.choice([-2, 2]) * speed
    return dx, dy

def keyboard_func(key, x, y):
    global simulation_paused
    if key == b' ': 
        simulation_paused = not simulation_paused
        print("Simulation is now", "paused" if simulation_paused else "running")

def special_keyboard_func(key, x, y):
    global vel_multiplier
    if simulation_paused:
        return   #when paused no speed change
    if key == GLUT_KEY_UP:
        vel_multiplier += 0.1
        print(f"Speed increased to {vel_multiplier:.1f}x")
    elif key == GLUT_KEY_DOWN:
        vel_multiplier -= 0.1
        if vel_multiplier < 0.1:
            vel_multiplier = 0.1
        print(f"Speed decreased to {vel_multiplier:.1f}x")

def mouse_func(button, state, x, y):
    if simulation_paused:
        return
    gl_x = x - w_width/2
    gl_y = w_height/2 - y

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        create_dots(gl_x, gl_y)

    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        global blinking_enabled
        blinking_enabled = not blinking_enabled

def timer(value):
    if not simulation_paused:
        update_particles()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  

def main():
    glutInit()
    glutInitWindowSize(w_width, w_height)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"The Amazing Box")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_func)
    glutSpecialFunc(special_keyboard_func)
    glutMouseFunc(mouse_func) 
    glutTimerFunc(16, timer, 0)
    glutMainLoop()
if __name__ == "__main__":
    main()   