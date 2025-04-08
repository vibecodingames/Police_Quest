import asyncio
import pygame
import math

# === Initialization ===
pygame.init()

# === Screen and Tile Settings ===
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_WIDTH = 64
TILE_HEIGHT = TILE_WIDTH // 2
GRID_SIZE = 12  # 12x12 grid

# === Derived Constants ===
GRID_OFFSET_X = SCREEN_WIDTH // 2 - (GRID_SIZE * TILE_WIDTH) // 4
GRID_OFFSET_Y = SCREEN_HEIGHT // 2 - (GRID_SIZE * TILE_HEIGHT) // 2
PLAYER_SIZE = TILE_WIDTH // 4
PLAYER_SPEED = 2

# === Colors ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # Added RED color
GRID_COLOR = (100, 149, 237)
HIGHLIGHT_COLOR = (255, 255, 0)

# === Set up the display ===
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric Grid Prototype")


# === Isometric Helper Functions ===
def cart_to_iso(x, y):
    iso_x = (x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2)
    return iso_x + GRID_OFFSET_X, iso_y + GRID_OFFSET_Y

def iso_to_cart(screen_x, screen_y):
    # Adjust coordinates to grid center
    screen_x -= GRID_OFFSET_X
    screen_y -= GRID_OFFSET_Y
    
    x = (2 * screen_y + screen_x) / (2 * TILE_HEIGHT)
    y = (2 * screen_y - screen_x) / (2 * TILE_HEIGHT)
    return int(round(x)), int(round(y))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.pixel_x, self.pixel_y = cart_to_iso(x, y)
        self.target_pixel_x, self.target_pixel_y = self.pixel_x, self.pixel_y
        self.moving = False
        self.speed = 4
        
        # Animation properties
        self.direction = 4  # Start facing South
        self.frame = 0
        self.frame_timer = 0
        self.FRAME_DURATION = 100
        self.sprites = self.load_spritesheet()

    def load_spritesheet(self):
        directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
        sprites = []
        
        for direction in directions:
            direction_sprites = []
            for frame in range(3):
                image_path = f"assets/character/cs_{direction}{frame}.png"
                try:
                    # Load and scale the sprite
                    original_sprite = pygame.image.load(image_path).convert_alpha()
                    original_size = original_sprite.get_size()
                    scaled_size = (original_size[0] // 2, original_size[1] // 2)
                    sprite = pygame.transform.scale(original_sprite, scaled_size)
                    direction_sprites.append(sprite)
                except pygame.error:
                    print(f"Warning: Could not load {image_path}")
                    if frame > 0 and direction_sprites:
                        direction_sprites.append(direction_sprites[0])
            sprites.append(direction_sprites)
        return sprites

    def move_to_tile(self, tile_x, tile_y):
        if 0 <= tile_x < GRID_SIZE and 0 <= tile_y < GRID_SIZE:
            if (tile_x, tile_y) != (self.target_x, self.target_y):
                dx = tile_x - self.x
                dy = tile_y - self.y
                self.direction = get_direction(dx, dy)
                self.frame = 0  # Reset animation
                self.target_x = tile_x
                self.target_y = tile_y
                self.target_pixel_x, self.target_pixel_y = cart_to_iso(tile_x, tile_y)
                self.moving = True

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.moving:
            dx = self.target_pixel_x - self.pixel_x
            dy = self.target_pixel_y - self.pixel_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if current_time - self.frame_timer > self.FRAME_DURATION:
                self.frame = (self.frame + 1) % len(self.sprites[self.direction])
                self.frame_timer = current_time
            
            if distance < self.speed:
                self.pixel_x = self.target_pixel_x
                self.pixel_y = self.target_pixel_y
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
            else:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                self.pixel_x += dx
                self.pixel_y += dy

    def draw(self, surface):
        # Calculate screen position
        screen_x = self.pixel_x
        screen_y = self.pixel_y
        
        current_sprite = self.sprites[self.direction][self.frame]
        sprite_rect = current_sprite.get_rect()
        
        # Position sprite at the bottom center of the tile
        sprite_rect.midbottom = (
            int(screen_x + TILE_WIDTH // 2),
            int(screen_y + TILE_HEIGHT)
        )
        surface.blit(current_sprite, sprite_rect)

def get_direction(dx, dy):
    angle = math.atan2(-dy, dx)
    angle_deg = math.degrees(angle) % 360

    if 22.5 <= angle_deg < 67.5:
        return 1  # NE
    elif 67.5 <= angle_deg < 112.5:
        return 0  # N
    elif 112.5 <= angle_deg < 157.5:
        return 7  # NW
    elif 157.5 <= angle_deg < 202.5:
        return 6  # W
    elif 202.5 <= angle_deg < 247.5:
        return 5  # SW
    elif 247.5 <= angle_deg < 292.5:
        return 4  # S
    elif 292.5 <= angle_deg < 337.5:
        return 3  # SE
    else:
        return 2  # E

# === Classes ===
class IsometricGrid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def draw(self, surface, highlight_tile=None):
        for row in range(self.rows - 1, -1, -1):
            for col in range(self.cols):
                screen_x, screen_y = cart_to_iso(col, row)
                points = [
                    (screen_x, screen_y + TILE_HEIGHT // 2),
                    (screen_x + TILE_WIDTH // 2, screen_y),
                    (screen_x + TILE_WIDTH, screen_y + TILE_HEIGHT // 2),
                    (screen_x + TILE_WIDTH // 2, screen_y + TILE_HEIGHT)
                ]
                color = HIGHLIGHT_COLOR if highlight_tile == (col, row) else GRID_COLOR
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, WHITE, points, 2)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Isometric Grid")
    
    clock = pygame.time.Clock()
    grid = IsometricGrid(GRID_SIZE, GRID_SIZE)
    player = Player(2, 2)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        hovered_tile = iso_to_cart(*mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    player.move_to_tile(*hovered_tile)

        player.update()
        
        screen.fill(BLACK)
        grid.draw(screen, highlight_tile=hovered_tile)
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
