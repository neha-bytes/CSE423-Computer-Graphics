from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math 
import random


INITIAL_PLAYER_LIFE = 5
MAX_MISSED_BULLETS = 15
NUM_ENEMIES = 5
ENEMY_HIT_RADIUS = 45.0  
PLAYER_HIT_RADIUS = 30.0 
BULLET_SIZE = 15.0
ENEMY_BASE_RADIUS = 60.0  
ENEMY_HEAD_RADIUS = 30.0  
ENEMY_SCALE_SPEED = 0.00025 
ENEMY_SCALE_MIN = 0.8
ENEMY_SCALE_MAX = 1.2
CHEAT_FIRE_COOLDOWN = 80

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800 
PLAYER_SPEED = 10.0 
BULLET_SPEED = 0.6 
ENEMY_SPEED = 0.015 
GUN_ROTATION_SPEED = 0.125 
CAMERA_ROTATION_SPEED = 0.3 
CAMERA_MOVE_SPEED = 2.0 

#Camera-related
camera_position = (0, 500, 500)
field_of_view = 120
grid_size = 600
random_value = 423

class GameWorld:
    def __init__(self):
        self.main_player = PlayerCharacter()
        self.enemy_list = []
        self.bullet_list = []
        self.points = 0
        self.is_game_over = False
        self.cheat_c_active = False
        self.cheat_v_active = False
        self.camera_first_person = False
        
        for _ in range(5):
            self.enemy_list.append(EnemyCreature())
    
    def game_tick(self):
        if self.is_game_over:
            return
            
        for projectile in self.bullet_list[:]:
            projectile.move()
            if projectile.is_off_screen():
                self.bullet_list.remove(projectile)
                self.main_player.missed_shots += 1
                
        for attack in self.enemy_list:
            attack.move_toward(self.main_player.location)
            
            #Collision with player
            if self.main_player.hits(attack):
                self.main_player.health -= 1
                attack.reposition()
                
        for projectile in self.bullet_list[:]:
            for attack in self.enemy_list[:]:
                if projectile.hits(attack):
                    self.points += 1
                    if projectile in self.bullet_list:
                        self.bullet_list.remove(projectile)
                    attack.reposition()
                    break
                    
        #Game end conditions
        if self.main_player.health <= 0 or self.main_player.missed_shots >= 10:
            self.is_game_over = True
            
        # Cheat mode
        if self.cheat_c_active:
            self.main_player.weapon_rotation += 0.125

class PlayerCharacter:
    def __init__(self):
        self.location = [0, 0, 15]
        self.weapon_rotation = 0
        self.health = 5
        self.missed_shots = 0
        
    def change_position(self, movement_direction):
        movement_speed = 10.0
        if movement_direction == "ahead":
            self.location[0] -= movement_speed * math.sin(math.radians(-self.weapon_rotation))
            self.location[1] -= movement_speed * math.cos(math.radians(self.weapon_rotation))
        elif movement_direction == "behind":
            self.location[0] += movement_speed * math.sin(math.radians(-self.weapon_rotation))
            self.location[1] += movement_speed * math.cos(math.radians(self.weapon_rotation))
            
        # Constrain to play area
        edge_buffer = 10
        self.location[0] = max(-grid_size + edge_buffer, min(grid_size - edge_buffer, self.location[0]))
        self.location[1] = max(-grid_size + edge_buffer, min(grid_size - edge_buffer, self.location[1]))
    
    def adjust_weapon(self, rotation_direction):
        if rotation_direction == "counter_clockwise":
            self.weapon_rotation += 2.5
        elif rotation_direction == "clockwise":
            self.weapon_rotation -= 2.5
        self.weapon_rotation %= 360
    
    def shoot(self):
        angle_radians = math.radians(self.weapon_rotation - 90)
        bullet_position = [
            self.location[0] + 85 * math.cos(angle_radians),
            self.location[1] + 85 * math.sin(angle_radians),
            self.location[2] + 80
        ]
        bullet_direction = [math.cos(angle_radians), math.sin(angle_radians)]
        return Projectile(bullet_position, bullet_direction)
    
    def hits(self, enemy):
        x_diff = self.location[0] - enemy.position[0]
        y_diff = self.location[1] - enemy.position[1]
        distance = math.sqrt(x_diff*x_diff + y_diff*y_diff)
        return distance < (30 + 40 * enemy.size_factor)
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])
        glRotatef(self.weapon_rotation, 0, 0, 1)
        
        #player body
        glColor3f(0.0, 0.0, 1.0)
        glPushMatrix()
        glTranslatef(15, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-15, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 0, 70)
        glColor3f(85/255, 108/255, 47/255)
        glutSolidCube(40)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 0, 110)
        glColor3f(0.0, 0.0, 0.0)
        gluSphere(gluNewQuadric(), 20, 10, 10)
        glPopMatrix()
        
        #weapon
        glPushMatrix()
        glTranslatef(20, -40, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(192/255, 192/255, 192/255)
        gluCylinder(gluNewQuadric(), 1, 10, 80, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

class EnemyCreature:
    def __init__(self):
        self.position = [0, 0, 40]
        self.size_factor = 1.0
        self.scaling_direction = 1
        self.reposition()
        
    def reposition(self):
        self.position = [
            random.uniform(-grid_size * 0.9, grid_size * 0.9),
            random.uniform(-grid_size * 0.9, grid_size * 0.9),
            40
        ]
        
    def move_toward(self, target_position):
        # Move towards target
        x_diff = target_position[0] - self.position[0]
        y_diff = target_position[1] - self.position[1]
        distance = math.sqrt(x_diff*x_diff + y_diff*y_diff)
        if distance > 0:
            self.position[0] += (x_diff / distance) * 0.015
            self.position[1] += (y_diff / distance) * 0.015
            
        #size effect
        self.size_factor += self.scaling_direction * 0.00025
        if self.size_factor > 1.2:
            self.size_factor = 1.2
            self.scaling_direction = -1
        elif self.size_factor < 0.8:
            self.size_factor = 0.8
            self.scaling_direction = 1
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glScalef(self.size_factor, self.size_factor, self.size_factor)
        
        #enemy base
        glColor3f(1.0, 0.0, 0.0)
        gluSphere(gluNewQuadric(), 40, 12, 12)
        
        #enemy top
        glPushMatrix()
        glTranslatef(0, 0, 52)
        glColor3f(0, 0, 0)
        gluSphere(gluNewQuadric(), 20, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

class Projectile:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.velocity = 0.6
        
    def move(self):
        self.position[0] += self.direction[0] * self.velocity
        self.position[1] += self.direction[1] * self.velocity
        
    def is_off_screen(self):
        return (abs(self.position[0]) > grid_size or 
                abs(self.position[1]) > grid_size)
                
    def hits(self, enemy):
        x_diff = self.position[0] - enemy.position[0]
        y_diff = self.position[1] - enemy.position[1]
        distance = math.sqrt(x_diff*x_diff + y_diff*y_diff)
        return distance < (5 + 40 * enemy.size_factor)
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(1.0, 1.0, 1.0)
        glutSolidCube(10)
        glPopMatrix()

game_world = GameWorld()

def render_text(x, y, text_string, font_style=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    #Orthographic projection matching window dimensions
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Render text at screen coordinates
    glRasterPos2f(x, y)
    for character in text_string:
        glutBitmapCharacter(font_style, ord(character))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_play_area():
    glBegin(GL_QUADS)
    for x_coord in range(-grid_size, grid_size + 1, 100):
        for y_coord in range(-grid_size, grid_size + 1, 100):
            if (x_coord + y_coord) % 200 == 0:
                glColor3f(1, 1, 1)  
            else:
                glColor3f(0.7, 0.5, 0.95)  
            
            glVertex3f(x_coord, y_coord, 0)                 
            glVertex3f(x_coord + 100, y_coord, 0)           
            glVertex3f(x_coord + 100, y_coord + 100, 0)     
            glVertex3f(x_coord, y_coord + 100, 0)           

    #boundary walls
    glColor3f(0.0, 1.0, 0.0)  
    glVertex3f(-grid_size, -grid_size, 0)           
    glVertex3f(-grid_size, grid_size + 100, 0)      
    glVertex3f(-grid_size, grid_size + 100, 100)    
    glVertex3f(-grid_size, -grid_size, 100)         

    glColor3f(0.0, 0.0, 1.0)  
    glVertex3f(grid_size + 100, -grid_size, 0)      
    glVertex3f(grid_size + 100, grid_size + 100, 0) 
    glVertex3f(grid_size + 100, grid_size + 100, 100) 
    glVertex3f(grid_size + 100, -grid_size, 100)    

    glColor3f(0.0, 1.0, 1.0)  
    glVertex3f(-grid_size, -grid_size, 0)           
    glVertex3f(grid_size + 100, -grid_size, 0)      
    glVertex3f(grid_size + 100, -grid_size, 100)    
    glVertex3f(-grid_size, -grid_size, 100)         
 
    glColor3f(1.0, 1.0, 1.0)  
    glVertex3f(-grid_size, grid_size + 100, 0)      
    glVertex3f(grid_size + 100, grid_size + 100, 0) 
    glVertex3f(grid_size + 100, grid_size + 100, 100) 
    glVertex3f(-grid_size, grid_size + 100, 100)    

    glEnd()


def handle_keyboard(key, x, y):
   
    global game_world
    
    #Move forward (E)
    if key == b'e' or key == b'E':  
        game_world.main_player.change_position("ahead")
    
    #Move backward (D)
    if key == b'd' or key == b'D':
        game_world.main_player.change_position("behind")
    
    #Rotate weapon left (S)
    if key == b's' or key == b'S':
        game_world.main_player.adjust_weapon("counter clockwise")
    
    #Rotate weapon right (F)
    if key == b'f' or key == b'F':
        game_world.main_player.adjust_weapon("clockwise")
    
    #Toggle cheat mode (C)
    if key == b'c' or key == b'C':
        game_world.cheat_c_active = not game_world.cheat_c_active
        print(f"Cheat mode C: {game_world.cheat_c_active}")
    
    #Toggle cheat vision (V)
    if key == b'v' or key == b'V':
        if game_world.cheat_c_active and game_world.camera_first_person:
            game_world.cheat_v_active = not game_world.cheat_v_active
            print(f"Cheat mode V: {game_world.cheat_v_active}")
    
    #Reset game (R)
    if key == b'r' or key == b'R':
        if game_world.is_game_over:
            game_world = GameWorld()
            print("Game reset")


def handle_special_keys(key, x, y): #Processes special key inputs for camera adjustment

    global camera_position
    x, y, z = camera_position
    
    #Move camera up (UP arrow)
    if key == GLUT_KEY_UP:
        z += 2.0

    #Move camera down (DOWN arrow)
    if key == GLUT_KEY_DOWN:
        z -= 2.0
        z = max(10, z)  # Prevent going below ground

    #Rotate camera left (LEFT arrow)
    if key == GLUT_KEY_LEFT:
        x -= 1

    #Rotate camera right (RIGHT arrow)
    if key == GLUT_KEY_RIGHT:
        x += 1

    camera_position = (x, y, z)

def handle_mouse(button, state, x, y):    #Processes mouse inputs for shooting and camera mode toggling

    global game_world
    
    #Left mouse button shoots
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_world.cheat_c_active and not game_world.is_game_over:
            new_bullet = game_world.main_player.shoot()
            game_world.bullet_list.append(new_bullet)

    #Right mouse button toggles camera mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game_world.camera_first_person = not game_world.camera_first_person
        print(f"First person mode: {game_world.camera_first_person}")


def configure_camera():  #Sets up the camera's projection and view parameters

    global camera_position, game_world
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Set up perspective projection
    gluPerspective(field_of_view, 1.25, 0.1, 1500)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Extract camera position
    x, y, z = camera_position
    
    if game_world.camera_first_person:
        # First-person camera from player's viewpoint
        player_x, player_y, player_z = game_world.main_player.location
        eye_x = player_x
        eye_y = player_y
        eye_z = player_z + 140  # Eye level
        
        # Look in weapon direction
        angle_rad = math.radians(-game_world.main_player.weapon_rotation)
        center_x = eye_x - math.sin(angle_rad) * 100
        center_y = eye_y - math.cos(angle_rad) * 100
        center_z = eye_z
        
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)
    else:
        # Third-person camera
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)


def idle_processing(): #Continuous processing function for game updates and rendering
    game_world.game_tick()
    glutPostRedisplay()


def display_scene():

    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    configure_camera()

    #game elements
    draw_play_area()
    game_world.main_player.render()
    for enemy in game_world.enemy_list:
        enemy.render()
    for bullet in game_world.bullet_list:
        bullet.render()
    
    #display game information
    render_text(10, 770, f"Score: {game_world.points}")
    render_text(10, 740, f"Health: {game_world.main_player.health}")
    render_text(10, 710, f"Missed Shots: {game_world.main_player.missed_shots}")
    
    if game_world.is_game_over:
        render_text(400, 400, "GAME OVER - Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24)

    # Swap buffers
    glutSwapBuffers()


# Main application entry point
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow(b"3D OpenGL Game")
    glutDisplayFunc(display_scene)
    glutKeyboardFunc(handle_keyboard)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse)
    glutIdleFunc(idle_processing)
    glutMainLoop()

if __name__ == "__main__":
    main()