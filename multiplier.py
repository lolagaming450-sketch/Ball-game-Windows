import sys
import random
import array
import math

# --- 1. Initialize Pygame (AUDIO ONLY) ---
import pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

def generate_bounce_sound():
    duration = 0.05  
    frequency = 500 
    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    max_amplitude = 32767
    audio_data = array.array('h')
    
    for i in range(total_samples):
        decay = 1.0 - (i / total_samples)
        sample = int(max_amplitude * math.sin(2.0 * math.pi * frequency * i / sample_rate) * decay)
        audio_data.append(sample)
        
    return pygame.mixer.Sound(buffer=audio_data)

bounce_sound = generate_bounce_sound()

# --- 2. Initialize PyQt6 (WINDOWS GRAPHICS) ---
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush

BALL_SIZE = 80
SLOWER_SPEED = 3

class Ball:
    def __init__(self, x, y, dx, dy, color_hex):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = QColor(color_hex)
        self.flash_frames = 0  

class TransparentDesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- WINDOWS TRANSPARENCY & TOP LAYER FLAGS ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        # Windows requires a solid background color that we turn 100% transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: black;")
        
        # Lock window to exact screen size
        screen_geometry = QApplication.primaryScreen().geometry()
        self.WIDTH = screen_geometry.width()
        self.HEIGHT = screen_geometry.height()
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)
        
        self.colors = ["#FF007F", "#00F0FF", "#FFDD00", "#00FF66", "#FF5E00", "#9D00FF"]
        start_x = (self.WIDTH / 2) - (BALL_SIZE / 2)
        start_y = (self.HEIGHT / 2) - (BALL_SIZE / 2)
        self.balls = [Ball(start_x, start_y, SLOWER_SPEED, SLOWER_SPEED, random.choice(self.colors))]
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_physics)
        self.timer.start(16)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            pygame.mixer.stop()
            QApplication.quit()

    def update_physics(self):
        self.raise_()
        new_balls = []
        any_bounced = False

        for ball in self.balls:
            ball.x += ball.dx
            ball.y += ball.dy
            
            if ball.flash_frames > 0:
                ball.flash_frames -= 1

            bounced = False
            push_x = 0
            push_y = 0

            if ball.x <= 0 and ball.dx < 0:
                ball.dx *= -1; bounced = True; push_x = 5
            elif ball.x + BALL_SIZE >= self.WIDTH and ball.dx > 0:
                ball.dx *= -1; bounced = True; push_x = -5

            if ball.y <= 0 and ball.dy < 0:
                ball.dy *= -1; bounced = True; push_y = 5
            elif ball.y + BALL_SIZE >= self.HEIGHT and ball.dy > 0:
                ball.dy *= -1; bounced = True; push_y = -5

            if bounced:
                any_bounced = True
                ball.flash_frames = 3 

                for i in range(2):
                    spawn_dx = ball.dx + random.choice([-1, 1, 2])
                    spawn_dy = ball.dy + random.choice([-1, 1, -2])
                    
                    if spawn_dx == 0: spawn_dx = SLOWER_SPEED
                    if spawn_dy == 0: spawn_dy = -SLOWER_SPEED
                    
                    safe_x = ball.x + (push_x * (i + 1))
                    safe_y = ball.y + (push_y * (i + 1))
                    
                    new_balls.append(Ball(safe_x, safe_y, spawn_dx, spawn_dy, random.choice(self.colors)))

        self.balls.extend(new_balls)

        if any_bounced:
            bounce_sound.play()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        painter.setPen(Qt.PenStyle.NoPen) 

        # Clear the background frame before drawing
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        for ball in self.balls:
            if ball.flash_frames > 0:
                painter.setBrush(QBrush(QColor("#FFFFFF")))
            else:
                painter.setBrush(QBrush(ball.color))
            
            painter.drawEllipse(QRectF(ball.x, ball.y, BALL_SIZE, BALL_SIZE))

app = QApplication(sys.argv)
window = TransparentDesktopApp()
window.show()
sys.exit(app.exec())