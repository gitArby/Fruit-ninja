import pygame
import random
import time

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = pygame.display.get_surface().get_size()
pygame.display.set_caption("LIDL FRUIT NINJA")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

apple_img = pygame.image.load("apple.png")
banana_img = pygame.image.load("banana.png")
bomb_img = pygame.image.load("bomb.png")
background_img = pygame.image.load("background.jpg")
katana_cursor_img = pygame.image.load("katana.png")

destruction_images = []
for i in range(1, 2):
    img = pygame.image.load(f"destruction{i}.png")
    destruction_images.append(pygame.transform.scale(img, (100, 100)))

font = pygame.font.Font(None, 36)
combo_font = pygame.font.Font(None, 48)

running = True

fruits = []
last_hit_time = 0
remaining_lives = 3  # Přidání proměnné pro sledování počtu zbývajících životů

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

class Fruit:
    def __init__(self, is_bomb=False):
        if is_bomb:
            self.image = bomb_img
        else:
            self.image = random.choice([apple_img, banana_img])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.choice([-self.rect.height, height])
        self.speed_x = random.randint(-5, 5)
        self.speed_y = random.randint(2, 5) * random.choice([-1, 1])

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left > width or self.rect.right < 0:
            self.rect.x = random.randint(0, width - self.rect.width)
            self.speed_x = random.randint(-5, 5)
        if self.rect.top > height or self.rect.bottom < 0:
            self.rect.y = random.randint(0, height - self.rect.height)
            self.speed_y = random.randint(2, 5) * random.choice([-1, 1])

def reset_game():
    global score, time_remaining, game_over, combo, last_hit_time, remaining_lives
    fruits.clear()
    score = 0
    time_remaining = 120
    game_over = False
    combo = 0
    last_hit_time = 0
    remaining_lives = 3  # Resetování počtu životů na začátku hry

def increase_combo():
    global combo
    combo += 1

def run_game(difficulty):
    global running, score, time_remaining, combo, start_time, fruits, last_hit_time, remaining_lives
    reset_game()
    start_time = time.time()
    if difficulty == "easy":
        fruit_spawn_rate = 0.02
        bomb_spawn_rate = 0.1
        fruit_speed_range = (-3, 3)
    elif difficulty == "medium":
        fruit_spawn_rate = 0.03
        bomb_spawn_rate = 0.15
        fruit_speed_range = (-5, 5)
    elif difficulty == "hard":
        fruit_spawn_rate = 0.04
        bomb_spawn_rate = 0.2
        fruit_speed_range = (-7, 7)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return

        screen.blit(background_img, (0, 0))

        if time_remaining > 0:
            if random.random() < fruit_spawn_rate:
                if random.random() < bomb_spawn_rate:
                    new_fruit = Fruit(is_bomb=True)
                else:
                    new_fruit = Fruit()
                fruits.append(new_fruit)

            for fruit in fruits:
                fruit.move()
                screen.blit(fruit.image, fruit.rect)

                katana_rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                if katana_rect.colliderect(fruit.rect):
                    if isinstance(fruit, Fruit) and fruit.image == bomb_img:
                        # Odečtení 5 bodů a života při zásahu bomby
                        score -= 5
                        remaining_lives -= 1
                        if remaining_lives <= 0:  # Konec hry, pokud hráč ztratil všechny životy
                            running = False
                        fruits.remove(fruit)
                    else:
                        for img in destruction_images:
                            screen.blit(img, fruit.rect)
                            pygame.display.flip()
                            clock.tick(30)
                        fruits.remove(fruit)
                        score += 1 + combo
                        increase_combo()
                        last_hit_time = time.time()

            draw_text(f"Score: {score}", font, BLACK, 10, 10)
            draw_text(f"Combo: {combo}", combo_font, BLACK, 10, 50)

            elapsed_time = time.time() - start_time
            time_remaining = max(0, 120 - int(elapsed_time))
            draw_text(f"Time: {time_remaining}", font, BLACK, width - 150, 10)

            draw_text(f"Lives: {remaining_lives}", font, BLACK, width - 150, 50)  # Vykreslení zbývajících životů

            if time.time() - last_hit_time > 1:
                combo = 0

        else:
            running = False

        pygame.mouse.set_visible(False)
        screen.blit(katana_cursor_img, pygame.mouse.get_pos())

        pygame.display.flip()

        clock.tick(60)

def main_menu():
    global running
    menu_font = pygame.font.Font(None, 48)
    menu_text = ["LIDL FRUIT NINJA", "Select Difficulty:", "1. Easy", "2. Medium", "3. Hard"]

    selected_difficulty = None

    while not selected_difficulty:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_difficulty = "easy"
                elif event.key == pygame.K_2:
                    selected_difficulty = "medium"
                elif event.key == pygame.K_3:
                    selected_difficulty = "hard"
                elif event.key == pygame.K_q:
                    if running:
                        running = False
                    else:
                        pygame.quit()
                        quit()

        screen.fill(WHITE)
        for i, line in enumerate(menu_text):
            text = menu_font.render(line, True, BLACK)
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 100 + i * 50))

        pygame.display.flip()

    return selected_difficulty

while True:
    difficulty = main_menu()
    if not running:
        break
    if difficulty:
        score = 0
        combo = 0
        run_game(difficulty)
        running = True
