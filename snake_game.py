import pygame
import sys
import random
import math

# --- Initialization ---
pygame.init()

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
HEADER_HEIGHT = 60

# --- Modern Neon Color Palette ---
COLOR_BG = (10, 10, 20)           # Deep Space Blue
COLOR_GRID = (20, 20, 40)         # Faint Grid
COLOR_SNAKE = (0, 255, 128)       # Spring Green
COLOR_SNAKE_HEAD = (200, 255, 200)# Pale Green
COLOR_FOOD = (255, 0, 100)        # Hot Pink
COLOR_PARTICLE = (255, 255, 0)    # Gold Sparks
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (0, 180, 255)      # Cyan UI
COLOR_DANGER = (255, 50, 50)      # Red for Quit/Back

# --- Fonts ---
font_title = pygame.font.SysFont("impact", 70)
font_ui = pygame.font.SysFont("arial", 22, bold=True)
font_score = pygame.font.SysFont("consolas", 30, bold=True)
font_big = pygame.font.SysFont("arial", 80, bold=True)

# --- Setup Display ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake Ultra")
clock = pygame.time.Clock()

# --- Classes ---

class Particle:
    """ Creates a small explosion effect """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # Random velocity for explosion
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(15, 25) # Frames to live
        self.color = color
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.2) # Shrink over time

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class Button:
    def __init__(self, text, x, y, w, h, color, hover_color, action_id=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.action_id = action_id

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        current_color = self.hover_color if is_hovered else self.color
        
        # Draw Glow if hovered
        if is_hovered:
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, (current_color[0], current_color[1], current_color[2]), glow_rect, border_radius=15)

        # Draw Shadow
        pygame.draw.rect(surface, (0,0,0), (self.rect.x+3, self.rect.y+3, self.rect.w, self.rect.h), border_radius=12)
        # Draw Body
        pygame.draw.rect(surface, current_color, self.rect, border_radius=12)
        # Draw Text
        text_surf = font_ui.render(self.text, True, (255,255,255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

# --- Helper Functions ---

def draw_grid():
    # Draw faint grid lines
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, HEADER_HEIGHT), (x, HEIGHT))
    for y in range(HEADER_HEIGHT, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (WIDTH, y))

def draw_text_centered(text, font, color, y_offset=0):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    # Drop shadow
    shadow = font.render(text, True, (0,0,0))
    shadow_rect = shadow.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 + y_offset + 3))
    screen.blit(shadow, shadow_rect)
    screen.blit(surf, rect)

def countdown():
    """ Plays a 3, 2, 1 animation """
    for i in range(3, 0, -1):
        screen.fill(COLOR_BG)
        draw_text_centered(str(i), font_big, COLOR_ACCENT)
        pygame.display.update()
        pygame.time.wait(800)
    
    screen.fill(COLOR_BG)
    draw_text_centered("GO!", font_big, COLOR_SNAKE)
    pygame.display.update()
    pygame.time.wait(500)

# --- Main Game Loop ---

def game_loop(fps):
    # Setup Variables
    snake_x, snake_y = WIDTH // 2, HEIGHT // 2
    snake_x_change, snake_y_change = 0, 0
    snake_body = []
    snake_length = 1
    direction = "STOP"
    
    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(HEADER_HEIGHT, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    
    game_over = False
    paused = False
    
    particles = []

    # UI Buttons for Game Loop
    btn_back = Button("MENU", 10, 10, 80, 40, (100, 50, 50), COLOR_DANGER)

    # Start Animation
    countdown()

    while not game_over:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Button Click Check
            if btn_back.is_clicked(event):
                return "MENU" # Special signal to go back

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                
                if not paused:
                    if event.key == pygame.K_LEFT and direction != "RIGHT":
                        snake_x_change = -BLOCK_SIZE
                        snake_y_change = 0
                        direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and direction != "LEFT":
                        snake_x_change = BLOCK_SIZE
                        snake_y_change = 0
                        direction = "RIGHT"
                    elif event.key == pygame.K_UP and direction != "DOWN":
                        snake_y_change = -BLOCK_SIZE
                        snake_x_change = 0
                        direction = "UP"
                    elif event.key == pygame.K_DOWN and direction != "UP":
                        snake_y_change = BLOCK_SIZE
                        snake_x_change = 0
                        direction = "DOWN"

        # 2. Logic Update
        if not paused:
            snake_x += snake_x_change
            snake_y += snake_y_change

            # Boundary Check
            if snake_x >= WIDTH or snake_x < 0 or snake_y >= HEIGHT or snake_y < HEADER_HEIGHT:
                return snake_length - 1 

            # Move Particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # Snake Body Logic
            snake_head = [snake_x, snake_y]
            snake_body.append(snake_head)
            if len(snake_body) > snake_length:
                del snake_body[0]

            # Self Collision
            for x in snake_body[:-1]:
                if x == snake_head:
                    return snake_length - 1

            # Eat Food
            if snake_x == food_x and snake_y == food_y:
                # Spawn Particles
                for _ in range(15):
                    particles.append(Particle(food_x + BLOCK_SIZE//2, food_y + BLOCK_SIZE//2, list(random.choice([COLOR_FOOD, (255,255,255), (255,200,0)]))))
                
                food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                food_y = round(random.randrange(HEADER_HEIGHT, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                snake_length += 1

        # 3. Drawing Phase
        screen.fill(COLOR_BG)
        draw_grid()

        # Draw Food (Pulsing Effect)
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 2
        pygame.draw.rect(screen, COLOR_FOOD, (food_x - pulse, food_y - pulse, BLOCK_SIZE + pulse*2, BLOCK_SIZE + pulse*2), border_radius=8)

        # Draw Particles
        for p in particles:
            p.draw(screen)

        # Draw Snake
        for i, segment in enumerate(snake_body):
            is_head = (i == len(snake_body) - 1)
            color = COLOR_SNAKE_HEAD if is_head else COLOR_SNAKE
            
            # Snake Glow
            if is_head:
                glow_surf = pygame.Surface((BLOCK_SIZE*2, BLOCK_SIZE*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 255, 128, 50), (BLOCK_SIZE, BLOCK_SIZE), BLOCK_SIZE)
                screen.blit(glow_surf, (segment[0] - BLOCK_SIZE//2, segment[1] - BLOCK_SIZE//2))

            pygame.draw.rect(screen, color, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE), border_radius=5)

        # Draw Header Background
        pygame.draw.rect(screen, (15, 15, 25), (0, 0, WIDTH, HEADER_HEIGHT))
        pygame.draw.line(screen, COLOR_ACCENT, (0, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT), 2)
        
        # Draw Score
        score_text = font_score.render(f"SCORE: {snake_length - 1}", True, COLOR_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 15))

        # Draw Back Button
        btn_back.draw(screen)

        # Pause Overlay
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text_centered("PAUSED", font_title, COLOR_TEXT)
            draw_text_centered("Press SPACE to Resume", font_ui, COLOR_ACCENT, 50)

        pygame.display.update()
        clock.tick(fps)

# --- Screens ---

def main_menu():
    # UPDATED SPEEDS HERE: Easy=5, Normal=10, Hard=15
    btn_easy = Button("EASY", WIDTH//2 - 100, 250, 200, 50, (0, 100, 0), (0, 150, 0), 5)
    btn_med = Button("NORMAL", WIDTH//2 - 100, 320, 200, 50, (150, 100, 0), (200, 150, 0), 10)
    btn_hard = Button("HARD", WIDTH//2 - 100, 390, 200, 50, (150, 0, 0), (200, 0, 0), 15)
    btn_quit = Button("EXIT", WIDTH//2 - 100, 480, 200, 50, (50, 50, 50), (100, 100, 100), "EXIT")
    
    buttons = [btn_easy, btn_med, btn_hard, btn_quit]

    while True:
        screen.fill(COLOR_BG)
        
        # Animated Background
        time_val = pygame.time.get_ticks() / 1000
        pygame.draw.circle(screen, (20, 20, 50), (int(WIDTH/2 + math.sin(time_val)*100), int(HEIGHT/2 + math.cos(time_val)*100)), 150)

        draw_text_centered("NEON SNAKE", font_title, COLOR_SNAKE, -150)
        draw_text_centered("Select Your Speed", font_ui, COLOR_TEXT, -90)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for btn in buttons:
                if btn.is_clicked(event):
                    return btn.action_id

        for btn in buttons:
            btn.draw(screen)

        pygame.display.update()

def game_over_screen(score):
    btn_retry = Button("RETRY", WIDTH//2 - 110, 320, 220, 60, COLOR_ACCENT, (50, 200, 255), True)
    btn_menu = Button("MENU", WIDTH//2 - 110, 400, 220, 60, (100, 100, 100), (150, 150, 150), False)

    while True:
        screen.fill(COLOR_BG)
        
        draw_text_centered("GAME OVER", font_title, COLOR_FOOD, -100)
        draw_text_centered(f"Final Score: {score}", font_score, COLOR_TEXT, -30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if btn_retry.is_clicked(event):
                return "RETRY"
            if btn_menu.is_clicked(event):
                return "MENU"

        btn_retry.draw(screen)
        btn_menu.draw(screen)

        pygame.display.update()

# --- Entry Point ---
if __name__ == "__main__":
    current_state = "MENU"
    chosen_speed = 10
    last_score = 0
    
    while True:
        if current_state == "MENU":
            result = main_menu()
            if result == "EXIT":
                pygame.quit()
                sys.exit()
            else:
                chosen_speed = result
                current_state = "GAME"
                
        elif current_state == "GAME":
            result = game_loop(chosen_speed)
            if result == "MENU":
                current_state = "MENU"
            else:
                last_score = result
                current_state = "GAMEOVER"
                
        elif current_state == "GAMEOVER":
            result = game_over_screen(last_score)
            if result == "RETRY":
                current_state = "GAME"
            elif result == "MENU":
                current_state = "MENU"