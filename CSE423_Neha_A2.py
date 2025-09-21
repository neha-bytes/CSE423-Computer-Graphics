from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

class GameWindow:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.title = "Diamond Collector"
        self.init_window()

    def init_window(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(self.title.encode())
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

class LineDrawer:
    @staticmethod
    def get_zone(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) >= abs(dy):
            if dx >= 0 and dy >= 0: return 0
            if dx >= 0 and dy < 0: return 7
            if dx < 0 and dy >= 0: return 3
            return 4
        else:
            if dx >= 0 and dy >= 0: return 1
            if dx >= 0 and dy < 0: return 6
            if dx < 0 and dy >= 0: return 2
            return 5

    @staticmethod
    def to_zone0(x, y, zone):
        if zone == 0: return x, y
        if zone == 1: return y, x
        if zone == 2: return y, -x
        if zone == 3: return -x, y
        if zone == 4: return -x, -y
        if zone == 5: return -y, -x
        if zone == 6: return -y, x
        return x, -y

    @staticmethod
    def from_zone0(x, y, zone):
        if zone == 0: return x, y
        if zone == 1: return y, x
        if zone == 2: return -y, x
        if zone == 3: return -x, y
        if zone == 4: return -x, -y
        if zone == 5: return -y, -x
        if zone == 6: return y, -x
        return x, -y

    @staticmethod
    def draw_zone0_line(x1, y1, x2, y2, zone):
        dx = x2 - x1
        dy = y2 - y1
        d = 2 * dy - dx
        inc_e = 2 * dy
        inc_ne = 2 * (dy - dx)
        
        x, y = x1, y1
        while x <= x2:
            px, py = LineDrawer.from_zone0(x, y, zone)
            LineDrawer.plot_point(px, py)
            if d <= 0:
                d += inc_e
            else:
                d += inc_ne
                y += 1
            x += 1

    @staticmethod
    def plot_point(x, y):
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()

    @staticmethod
    def draw(x1, y1, x2, y2):
        zone = LineDrawer.get_zone(x1, y1, x2, y2)
        x1z, y1z = LineDrawer.to_zone0(x1, y1, zone)
        x2z, y2z = LineDrawer.to_zone0(x2, y2, zone)

        if x1z > x2z:
            x1z, x2z = x2z, x1z
            y1z, y2z = y2z, y1z
        LineDrawer.draw_zone0_line(x1z, y1z, x2z, y2z, zone)

class Diamond:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.color = (random.random(), random.random(), random.random())
    
    def get_edges(self):
        half = self.size / 2
        return [(self.x, self.y + half),  # Top
            (self.x + half, self.y),     # Right
            (self.x, self.y - half),     # Bottom
            (self.x - half, self.y)]      # Left
    
    def move(self, speed, dt):
        self.y -= speed * dt
    
    def is_out(self):
        return self.y + self.size/2 < 0
    
    def draw(self):
        edges = self.get_edges()
        for i in range(4):
            x1, y1 = edges[i]
            x2, y2 = edges[(i+1)%4]
            glColor3f(*self.color)
            LineDrawer.draw(x1, y1, x2, y2)

class Catcher:
    def __init__(self, x, y, width, height, slope):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.slope = slope
        self.color = (1.0, 1.0, 1.0)
    
    def get_corners(self):
        return [(self.x - self.width/2, self.y),                     # Bottom-left
            (self.x - self.width/2 + self.slope, self.y + self.height), # Top-left
            (self.x + self.width/2 + self.slope, self.y + self.height), # Top-right
            (self.x + self.width/2, self.y)]                      # Bottom-right 
    
    def move(self, direction, speed, dt, window_width):
        move_dist = speed * dt * direction
        new_x = self.x + move_dist
        
        min_x = self.width/2
        max_x = window_width - self.width/2 - self.slope
        
        if min_x <= new_x <= max_x:
            self.x = new_x
    
    def draw(self):
        corners = self.get_corners()
        glColor3f(*self.color)
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i+1)%4]
            LineDrawer.draw(x1, y1, x2, y2)

class GameButton:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
    
    def contains(self, px, py):
        return (self.x <= px <= self.x + self.size and 
                self.y <= py <= self.y + self.size)

class RestartButton(GameButton):
    def draw(self):
        glColor3f(*self.color)
        # Draw triangle arrow
        LineDrawer.draw(self.x, self.y + self.size/2, 
                        self.x + self.size, self.y + self.size)
        LineDrawer.draw(self.x + self.size, self.y + self.size,
                        self.x + self.size, self.y)
        LineDrawer.draw(self.x + self.size, self.y,
                        self.x, self.y + self.size/2)

class PlayPauseButton(GameButton):
    def draw(self, is_paused):
        glColor3f(*self.color)
        if is_paused:
            # Play triangle
            LineDrawer.draw(self.x, self.y,
                           self.x, self.y + self.size)
            LineDrawer.draw(self.x, self.y + self.size,
                           self.x + self.size, self.y + self.size/2)
            LineDrawer.draw(self.x + self.size, self.y + self.size/2,
                           self.x, self.y)
        else:
            # Pause bars
            bar_width = self.size / 4
            left = self.x + bar_width
            right = self.x + 3 * bar_width
            LineDrawer.draw(left, self.y, left, self.y + self.size)
            LineDrawer.draw(right, self.y, right, self.y + self.size)

class QuitButton(GameButton):
    def draw(self):
        glColor3f(*self.color)
        LineDrawer.draw(self.x, self.y, self.x + self.size, self.y + self.size)
        LineDrawer.draw(self.x, self.y + self.size, self.x + self.size, self.y)

class DiamondGame:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.window = GameWindow(self.width, self.height)
        
        # Game objects
        catcher_width = 120
        catcher_height = 25
        self.catcher = Catcher(
            x=self.width//2,
            y=20,
            width=catcher_width,
            height=catcher_height,
            slope=20
        )
        
        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.diamond_speed = 100
        self.speed_increase = 10
        self.catcher_speed = 300
        self.diamond = None
        
        # Buttons
        btn_size = 30
        btn_margin = 10
        self.restart_btn = RestartButton(
            btn_margin, self.height - btn_margin - btn_size, 
            btn_size, (0.0, 1.0, 1.0)
        )
        self.play_pause_btn = PlayPauseButton(
            self.width//2 - btn_size//2, self.height - btn_margin - btn_size,
            btn_size, (1.0, 0.75, 0.0)
        )
        self.quit_btn = QuitButton(
            self.width - btn_margin - btn_size, self.height - btn_margin - btn_size,
            btn_size, (1.0, 0.0, 0.0)
        )
        
        # Input handling
        self.key_state = {'left': False, 'right': False}
        self.last_time = time.time()
        
        self.spawn_diamond()
        self.setup_callbacks()
    
    
    def spawn_diamond(self):
        size = 30
        self.diamond = Diamond(
            x=random.randint(size, self.width - size),
            y=self.height - size,
            size=size
        )
    
    def handle_collision(self):
        if not self.diamond:
            return False
            
        diamond_edges = self.diamond.get_edges()
        catcher_edges = self.catcher.get_corners()
        
        # Simple AABB collision check
        diamond_min_x = min(p[0] for p in diamond_edges)
        diamond_max_x = max(p[0] for p in diamond_edges)
        diamond_min_y = min(p[1] for p in diamond_edges)
        
        catcher_min_x = min(p[0] for p in catcher_edges)
        catcher_max_x = max(p[0] for p in catcher_edges)
        catcher_max_y = max(p[1] for p in catcher_edges)
        
        return (diamond_max_x >= catcher_min_x and
                diamond_min_x <= catcher_max_x and
                diamond_min_y <= catcher_max_y)
    
    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        if self.paused or self.game_over:
            return
        
        # Move catcher
        direction = 0
        if self.key_state['left']: direction = -1
        if self.key_state['right']: direction = 1
        self.catcher.move(direction, self.catcher_speed, delta_time, self.width)
        
        # Move diamond
        if self.diamond:
            self.diamond.move(self.diamond_speed, delta_time)
            
            if self.handle_collision():
                self.score += 1
                print(f"Caught! Score: {self.score}")
                self.diamond_speed += self.speed_increase
                self.spawn_diamond()
            elif self.diamond.is_out():
                self.game_over = True
                print(f"Game Over! Final Score: {self.score}")
                self.diamond = None
        else:
            self.spawn_diamond()
        
        glutPostRedisplay()
    
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw buttons
        self.restart_btn.draw()
        self.play_pause_btn.draw(self.paused)
        self.quit_btn.draw()
        
        # Draw game objects
        if self.diamond:
            self.diamond.draw()
        self.catcher.draw()
        
        glutSwapBuffers()
    
    def keyboard(self, key, x, y):
        if key == b' ':
            self.paused = not self.paused
    
    def special_keys(self, key, x, y):
        if key == GLUT_KEY_LEFT:
            self.key_state['left'] = True
        elif key == GLUT_KEY_RIGHT:
            self.key_state['right'] = True
    
    def special_keys_up(self, key, x, y):
        if key == GLUT_KEY_LEFT:
            self.key_state['left'] = False
        elif key == GLUT_KEY_RIGHT:
            self.key_state['right'] = False
    
    def mouse_click(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            ogl_y = self.height - y
            if self.restart_btn.contains(x, ogl_y):
                self.restart_game()
            elif self.play_pause_btn.contains(x, ogl_y):
                self.paused = not self.paused
            elif self.quit_btn.contains(x, ogl_y):
                print("Thanks for playing!")
                glutLeaveMainLoop()
    
    def restart_game(self):
        self.score = 0
        self.diamond_speed = 100
        self.game_over = False
        self.paused = False
        self.catcher.x = self.width // 2
        self.spawn_diamond()
        print("Game restarted")

    def setup_callbacks(self):
        glutDisplayFunc(self.display)
        glutIdleFunc(self.update)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special_keys)
        glutSpecialUpFunc(self.special_keys_up)
        glutMouseFunc(self.mouse_click)

def main():
    game = DiamondGame()
    glutMainLoop()

if __name__ == "__main__":
    main()
