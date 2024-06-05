import pygame
import random
import math
import serial


class Game:
    def __init__(self) -> None:
        self.width = 1080
        self.height = 720
        self.fps = 60
        self.head_x = self.width // 2
        self.head_y = self.height // 2
        self.head_angle = 0
        self.position_offset = None
        
        self.snake_block_radius = 30
        self.snake_list = []
        self.snake_length = 1
        
        self.max_turn_rate = 5  # Maximum turn rate in degrees per frame
        self.snake_speed = 3 # pixels per frame
        self.spacing = 10 # moves between blocks
        self.sensitivity = 0.8  # 1 encoder rotation -> snake rotations 
        
        self.apple_x = 0
        self.apple_y = 0
        self.make_new_apple()
        
        self.score = 0
        
        self.obstacles = [
            (300, 300, 30, 30),
            (600, 400, 30, 30),
            (800, 200, 30, 30),
            (200, 100, 30, 30),
            (400, 500, 30, 30),
            (700, 600, 30, 30),
            (500, 250, 30, 30),
            (100, 650, 30, 30),
            (900, 350, 30, 30),
            (850, 500, 30, 30)
        ]

        
        self.running = False
        self.close = False
        
        pygame.init()
        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")
        self.font = pygame.font.SysFont("arial", 40)
        
        self.selected_button = 0
        self.total_buttons = 2
        
        self.ser = None
        self.init_serial_port()
        
        
        self.black = (0, 0, 0)
        self.obstacle_color = (145, 145, 145)
        self.white = (255, 255, 255)
        self.gray = (169, 169, 169)
        
        self.red = (255, 0, 0)
        self.bright_red = (255, 100, 100)
        self.border_red = (200, 0, 0)
        self.dark_red = (150, 0, 0)
        
        self.snake_body = (255, 165, 0)  # A vibrant orange color for the snake's body
        self.snake_body_border = (255, 140, 0)  # Slightly darker orange for the border
        
        self.green = (0, 255, 0)
        self.border_green = (0, 200, )
        self.bright_green = (120, 255, 120)
        self.dark_green = (0, 150, 0)
        
        self.blue = (0, 0, 255)
        self.bright_blue = (100, 100, 255)
        self.dark_blue = (0, 0, 150)
        
        self.grass_color = (34, 139, 34)  # A natural, darker green for the grass
        
    def init_serial_port(self):
        serial_port = 'COM4'
        baud_rate = 115200
        try:
            self.ser = serial.Serial(serial_port, baud_rate)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            pygame.quit()
            exit()
            
        
    def pause_menu(self):
        button_width = 200
        button_height = 45
        vertical_spacing = 70
        center_x = self.width // 2 - button_width // 2
        start_y = self.height // 2 - (button_height * self.total_buttons + vertical_spacing * (self.total_buttons - 1)) // 2

        while not self.running:
            self.win.fill(self.black)
            self.message("Pause Menu", self.white, (200, 200))
            if self.handle_selection_change():
                self.confirm_button()
                
            self.draw_button("Play", center_x, start_y + vertical_spacing, button_width, button_height,
                             self.green, self.bright_green, self.dark_green, self.selected_button == 0, self.play)
            # self.draw_button("Settings", center_x, start_y + 2 * vertical_spacing, button_width, button_height,
            #                  self.blue, self.bright_blue, self.dark_blue, self.selected_button == 1, self.settings)
            self.draw_button("Exit", center_x, start_y + 2 * vertical_spacing, button_width, button_height,
                             self.red, self.bright_red, self.dark_red, self.selected_button == 1, self.exit)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.clear()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.clear()
                    if event.key == pygame.K_RETURN:
                        self.confirm_button()
                        
            if self.close:
                self.clear()

    def confirm_button(self):
        if self.selected_button == 0:
            self.play()
        # elif self.selected_button == 1:
        #     self.settings()
        elif self.selected_button == 1:
            self.exit()
    
    def reset(self):
        self.head_x = self.width // 2
        self.head_y = self.height // 2
        self.head_angle = 0
        # target_angle = 0
        self.snake_list = []
        self.snake_length = 1
        self.make_new_apple()
        
        
        self.running = True
        self.position_offset = None
               
               
    def play(self):
        self.running = True
        
               
    def position_to_angle(self, data):
        if self.position_offset is None:
            self.position_offset = data
            
        position = data - self.position_offset
        position %= 30 / self.sensitivity 
        angle_value = -(position / 30 * self.sensitivity) * 360
        return angle_value
               
    def encoder_position(self):
        if self.ser.in_waiting > 0:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                
                if data == "Button pressed":
                    return "Button pressed"
                
                data_int = int(data)
                return data_int
            except Exception as e:
                print("Error reading serial data:", e)
                return None
        return None
                  
                  
    def handle_selection_change(self):
        position = self.encoder_position()
        if position == "Button pressed":
            return True
        
        if position is None or not isinstance(position, int):
            return False
        
        if self.position_offset is None:
            self.position_offset = position
            
        position = position - self.position_offset
        self.selected_button = position % self.total_buttons
        return False

    def settings(self):
        pass
    
    def exit(self):
        self.close = True
          
    def clear(self):
        self.ser.close()
        pygame.quit()
        quit()
        
    def draw_everything(self):
        self.win.fill(self.grass_color)
        pygame.draw.rect(self.win, self.border_red, [self.apple_x, self.apple_y, self.snake_block_radius, self.snake_block_radius])
        self.draw_obstacles()
        
        self.draw_snake()
        self.draw_score() 

        pygame.display.update()
    
    def draw_score(self):
        score_text = f"Score: {self.score}"
        self.message(score_text, self.white, position=(10, 10), font_size=30)
        
    def draw_snake(self):
        radius = self.snake_block_radius // 2
        
        for i, x in enumerate(self.snake_list):
            if i % self.spacing == 0 and i != len(self.snake_list) - 1 - (len(self.snake_list) - 1) % self.spacing:
                # Calculate the center of the circle
                center_x, center_y = x[0] + radius, x[1] + radius
                
                # Draw the filled circle
                pygame.draw.circle(self.win, self.snake_body, (center_x, center_y), radius)
                
                # Draw the border
                pygame.draw.circle(self.win, self.snake_body_border, (center_x, center_y), radius, 2)  # 2 is the border width
                
                # Draw direction line inside the circle
                if i < len(self.snake_list) - self.spacing:
                    next_block = self.snake_list[i + self.spacing]
                    next_center_x, next_center_y = next_block[0] + radius, next_block[1] + radius
                    angle_diff = math.atan2(next_center_y - center_y, next_center_x - center_x)
                    start_x = center_x + radius * math.cos(angle_diff)
                    start_y = center_y + radius * math.sin(angle_diff)
                    end_x = center_x - (radius - 2) * math.cos(angle_diff)
                    end_y = center_y - (radius - 2) * math.sin(angle_diff)
                    pygame.draw.line(self.win, self.snake_body_border, (start_x, start_y), (end_x, end_y), 2)  # 2 is the line width
                
        # Draw direction line for the head based on the angle
        if self.snake_list:
            head = self.snake_list[len(self.snake_list) - 1 - (len(self.snake_list) - 1) % self.spacing]
            head_center_x, head_center_y = head[0] + radius, head[1] + radius
            
            # Draw the filled circle
            pygame.draw.circle(self.win, self.red, (head_center_x, head_center_y), radius)
            
            # Draw the border
            pygame.draw.circle(self.win, self.border_red, (head_center_x, head_center_y), radius, 2)  # 2 is the border width
            
            head_end_x = head_center_x + (radius - 2) * math.cos(math.radians(self.head_angle))
            head_end_y = head_center_y - (radius - 2) * math.sin(math.radians(self.head_angle))
            head_start_x = head_center_x - radius * math.cos(math.radians(self.head_angle))
            head_start_y = head_center_y + radius * math.sin(math.radians(self.head_angle))
            pygame.draw.line(self.win, self.border_red, (head_start_x, head_start_y), (head_end_x, head_end_y), 2)  # 2 is the line width
            
    def draw_obstacles(self):
        for (x, y, w, h) in self.obstacles:
            pygame.draw.rect(self.win, self.obstacle_color, [x, y, w, h])
            
    def message(self, msg, color, position=(0, 0), font_size=50):
        font_style = pygame.font.SysFont(None, font_size)
        mesg = font_style.render(msg, True, color)
        self.win.blit(mesg, position)
        
    def draw_button(self, msg, x, y, w, h, ic, ac, dc, selected=False, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if selected:
            color = ac
        else:
            color = ic

        # Shadow
        pygame.draw.rect(self.win, dc, (x + 3, y + 3, w, h), border_radius=10)

        # Button
        pygame.draw.rect(self.win, color, (x, y, w, h), border_radius=10)
        
        # Button text
        small_text = pygame.font.SysFont("arial", 30)
        text_surf, text_rect = self.text_objects(msg, small_text)
        text_rect.center = ((x + (w / 2)), (y + (h / 2)))
        self.win.blit(text_surf, text_rect)
        if selected and click[0] == 1 and action is not None:
            action()
            
    def text_objects(self, text, font):
        text_surface = font.render(text, True, self.black)
        return text_surface, text_surface.get_rect()

    def check_collisions(self):
        for (ox, oy, ow, oh) in self.obstacles:
            if in_collision(ox + ow//2, oy + oh//2,
                            ow//2,
                            self.head_x + self.snake_block_radius//2, self.head_y + self.snake_block_radius//2,
                            self.snake_block_radius//2,
                            'sc'):
                self.reset()
                self.running = False
                
        for i in range(len(self.snake_list), 0, -self.spacing):
            if i > len(self.snake_list) - self.spacing:
                continue
            if in_collision(self.head_x, self.head_y, 
                            self.snake_block_radius//2, 
                            self.snake_list[i][0], self.snake_list[i][1], 
                            self.snake_block_radius//2,
                            'cc'):
                self.reset()
                self.running = False
    
    def make_new_apple(self):
        self.apple_x = round(random.randrange(0, self.width - self.snake_block_radius) / 10.0) * 10.0
        self.apple_y = round(random.randrange(0, self.height - self.snake_block_radius) / 10.0) * 10.0
        
    def teleport_snake(self):
        if self.head_x + self.snake_block_radius // 2 >= self.width:
            self.head_x = -self.snake_block_radius // 2
        elif self.head_x + self.snake_block_radius // 2 < 0:
            self.head_x = self.width - 1 - self.snake_block_radius // 2
        if self.head_y + self.snake_block_radius // 2 >= self.height:
            self.head_y = -self.snake_block_radius // 2
        elif self.head_y + self.snake_block_radius // 2 < 0:
            self.head_y = self.height - 1 - self.snake_block_radius // 2

        
def in_collision(x1, y1, r1, x2, y2, r2, obj_type, clearance=5):
    r1 -= clearance
    if obj_type == "ss":  # square-square collision
        return (x1 - r1 < x2 + r2 and x1 + r1 > x2 - r2 and y1 - r1 < y2 + r2 and y1 + r1 > y2 - r2)
    elif obj_type == "cc":  # circle-circle collision
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance < (r1 + r2)
    elif obj_type == "sc":  # square-circle collision
        closest_x = max(x1 - r1, min(x2, x1 + r1))
        closest_y = max(y1 - r1, min(y2, y1 + r1))
        distance = math.hypot(closest_x - x2, closest_y - y2)
        return distance < r2
    elif obj_type == "cs":  # circle-square collision
        return in_collision(x2, y2, r2, x1, y1, r1, "sc")
    else:
        raise ValueError("Invalid object type specified. Use 'ss', 'cc', 'sc', or 'cs'.")


def main():
    
    game = Game()
    target_angle = 0
    
    while True:
        if not game.running:
            game.pause_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game.exit()
                if event.key == pygame.K_RETURN:
                    if game.selected_button == 0:
                        game.cont()
                    elif game.selected_button == 1:
                        game.new_game()
                    elif game.selected_button == 2:
                        game.settings()
                    elif game.selected_button == 3:
                        game.exit()
        
        if game.close:
            break
        
        position = game.encoder_position()
        if position == "Button pressed":
            game.running = False
            # game.position_offset = None
            continue
        elif position is not None:
            target_angle = game.position_to_angle(position)

        target_angle = target_angle % 360
        angle_diff = (target_angle - game.head_angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        if abs(angle_diff) > game.max_turn_rate:
            game.head_angle += game.max_turn_rate if angle_diff > 0 else -game.max_turn_rate
        else:
            game.head_angle = target_angle
        game.head_angle = game.head_angle % 360

        game.head_x += game.snake_speed * math.cos(math.radians(game.head_angle))
        game.head_y -= game.snake_speed * math.sin(math.radians(game.head_angle))

        game.teleport_snake()
        
        snake_head = [game.head_x, game.head_y]
        game.snake_list.append(snake_head)
        if len(game.snake_list) > game.snake_length:
            del game.snake_list[0]

        game.check_collisions()

        if in_collision(game.apple_x + game.snake_block_radius//2, game.apple_y + game.snake_block_radius//2,
                        game.snake_block_radius//2,
                        game.head_x + game.snake_block_radius//2, game.head_y + game.snake_block_radius//2,
                        game.snake_block_radius//2,
                        'sc', 0):
            game.make_new_apple()
            game.score += 1
            game.snake_length += game.spacing
            
        game.draw_everything()

        game.clock.tick(game.fps)

    game.clear()

if __name__ == "__main__":
    main()

