import pygame
import math

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

def cart_to_iso(x, y):
    iso_x = (x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2)
    return iso_x + GRID_OFFSET_X, iso_y + GRID_OFFSET_Y

class Player:
    def __init__(self, x, y, tile_width, tile_height, grid_size, grid_offset_x, grid_offset_y):
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
        self.FRAME_DURATION = 100  # milliseconds per frame
        self.sprites = self.load_spritesheet()
        
        # Grid properties
        self.TILE_WIDTH = tile_width
        self.TILE_HEIGHT = tile_height
        self.GRID_SIZE = grid_size
        self.GRID_OFFSET_X = grid_offset_x
        self.GRID_OFFSET_Y = grid_offset_y
        
        # Update sprite size
        self.sprite_width = 64
        self.sprite_height = 64
        self.sprites = self.load_spritesheet()
        self.frame = 0
        self.frame_timer = pygame.time.get_ticks()
        self.FRAME_DURATION = 100

    def load_spritesheet(self):
        directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
        sprites = []
        
        for direction in directions:
            direction_sprites = []
            for frame in range(8):  # 8 frames per direction
                image_path = f"assets/character/cs_{direction}{frame}.png"
                try:
                    sprite = pygame.image.load(image_path).convert_alpha()
                    direction_sprites.append(sprite)
                except pygame.error:
                    print(f"Warning: Could not load {image_path}")
                    # Use first frame if others are missing
                    if frame > 0 and direction_sprites:
                        direction_sprites.append(direction_sprites[0])
            sprites.append(direction_sprites)
        
        return sprites

    def move_to_tile(self, tile_x, tile_y):
        if 0 <= tile_x < self.GRID_SIZE and 0 <= tile_y < self.GRID_SIZE:
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
            
            # Update animation frame
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