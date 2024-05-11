'''
    John Patrick I. Marasigan
    BSCS-3B-M
    MACHINE PROBLEM 5 - WUMPUS WORLD (AI)
'''


from time import sleep
import random
import pygame
import sys

# Initialize Pygame
pygame.init()

INFO_DISPLAY_HEIGHT = 30
WIDTH, HEIGHT = 640, 640 + INFO_DISPLAY_HEIGHT
ROWS, COLS = 4, 4
SQUARE_SIZE = WIDTH // COLS

# Set up the screen display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up title
pygame.display.set_caption("Wumpus World in AI")

# Load images and transform its size
floor_img = pygame.image.load("images/flooring.jpg")
floor_img = pygame.transform.scale(floor_img, (SQUARE_SIZE, SQUARE_SIZE))
bottom_pos_agent_img = pygame.image.load("images/bottom_agent.png")
bottom_pos_agent_img = pygame.transform.scale(bottom_pos_agent_img, (SQUARE_SIZE-50, SQUARE_SIZE-50))
up_pos_agent_img = pygame.image.load("images/top-agent.png")
up_pos_agent_img = pygame.transform.scale(up_pos_agent_img, (SQUARE_SIZE-50, SQUARE_SIZE-50))
left_pos_agent_img = pygame.image.load("images/left-agent.png")
left_pos_agent_img = pygame.transform.scale(left_pos_agent_img, (SQUARE_SIZE-50, SQUARE_SIZE-50))
right_pos_agent_img = pygame.image.load("images/right-agent.png")
right_pos_agent_img = pygame.transform.scale(right_pos_agent_img, (SQUARE_SIZE-50, SQUARE_SIZE-50))
fireball_img = pygame.image.load("images/fireball.png")
fireball_img = pygame.transform.scale(fireball_img, (SQUARE_SIZE-80, SQUARE_SIZE-80))
wumpus_img = pygame.image.load("images/wumpus.png")
wumpus_img = pygame.transform.scale(wumpus_img, (SQUARE_SIZE-20, SQUARE_SIZE-20))
stench_img = pygame.image.load("images/stench.png")
stench_img = pygame.transform.scale(stench_img, (SQUARE_SIZE-50, SQUARE_SIZE-120))
pit_img = pygame.image.load("images/pit.png")
pit_img = pygame.transform.scale(pit_img, (SQUARE_SIZE-40, SQUARE_SIZE-40))
breeze_img = pygame.image.load("images/breeze.png")
breeze_img = pygame.transform.scale(breeze_img, (SQUARE_SIZE-40, SQUARE_SIZE-90))
gold_img = pygame.image.load("images/gold.png")
gold_img = pygame.transform.scale(gold_img, (SQUARE_SIZE-70, SQUARE_SIZE-100))
undiscovered_area_img = pygame.image.load("images/undiscovered_area.jpg")
undiscovered_area_img = pygame.transform.scale(undiscovered_area_img, (SQUARE_SIZE, SQUARE_SIZE))

# Set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load a font
font = pygame.font.Font(None, 32)

# Initialization
agent_img = up_pos_agent_img    # Starting agent position
agent_pos = (0, 0)              # Start at bottom left
agent_current_look = "up"       # Looking at the top
agent_gold_amount = 50          # Starting gold amount
wumpus_pos = None               
pit_pos = []                    
stench_pos = []                 
breeze_pos = []
gold_pos = None                 

# AI inference initialization
grid_status = [[[] for _ in range(COLS)] for _ in range(ROWS)]
grid_status[0][0] = ['OK', 'V']
grid_status[0][1] = ['OK']
grid_status[1][0] = ['OK']


''' RULE OF INFERENCE FOR WUMPUS AI '''
# Decision making for AI
def decide_next_move(local_agent_pos):
    global agent_pos, grid_status, gold_pos, agent_gold_amount, agent_current_look
    # Define adjacent moves
    moves = [(0, 1, 'right'), (1, 0, 'up'), (0, -1, 'left'), (-1, 0, 'down')]
    
    # If agent perceives Stench, then mark adjacent position as Wumpus
    if 'S' in grid_status[local_agent_pos[0]][local_agent_pos[1]]:
        for adj_move in moves:
            adj_pos = (local_agent_pos[0] + adj_move[0], local_agent_pos[1] + adj_move[1])
            sensor_readings = get_sensor_readings(adj_pos)
            if sensor_readings[3] == 'Bump':
                continue
            if 'V' not in grid_status[adj_pos[0]][adj_pos[1]]:
                sensor_readings = get_sensor_readings(adj_pos)
                if sensor_readings[3] == 'Bump':
                    continue
                if 'W' not in grid_status[adj_pos[0]][adj_pos[1]]:
                    grid_status[adj_pos[0]][adj_pos[1]].append('W')
    
    # If agent perceives Breeze, then mark adjacent position as Pit
    if 'B' in grid_status[local_agent_pos[0]][local_agent_pos[1]]:
        for adj_move in moves:
            adj_pos = (local_agent_pos[0] + adj_move[0], local_agent_pos[1] + adj_move[1])
            sensor_readings = get_sensor_readings(adj_pos)
            if sensor_readings[3] == 'Bump':
                continue
            if 'V' not in grid_status[adj_pos[0]][adj_pos[1]]:
                sensor_readings = get_sensor_readings(adj_pos)
                if sensor_readings[3] == 'Bump':
                    continue
                if 'P' not in grid_status[adj_pos[0]][adj_pos[1]]:
                    grid_status[adj_pos[0]][adj_pos[1]].append('P')

    # If agent perceives Glitter, then pick up the Gold
    if 'G' in grid_status[local_agent_pos[0]][local_agent_pos[1]] and gold_pos:
        gold_pos = None  
        agent_gold_amount += 150 

    # Evaluate future moves
    random.shuffle(moves)
    for move in moves:
        new_pos = (local_agent_pos[0] + move[0], local_agent_pos[1] + move[1])

        sensor_readings = get_sensor_readings(new_pos)

        # evaluate next move first
        if sensor_readings[3] == 'Bump':
            continue
        if sensor_readings[0] == 'Stench':
            if all(item not in grid_status[new_pos[0]][new_pos[1]] for item in ['S', 'W']):
                grid_status[new_pos[0]][new_pos[1]].append('S')
        if sensor_readings[1] == 'Breeze':
            if all(item not in grid_status[new_pos[0]][new_pos[1]] for item in ['B', 'P']):
                grid_status[new_pos[0]][new_pos[1]].append('B')    
        if sensor_readings[2] == 'Glitter':
            if 'G' not in grid_status[new_pos[0]][new_pos[1]]:
                grid_status[new_pos[0]][new_pos[1]].append('G') 
        
        if 'W' not in grid_status[new_pos[0]][new_pos[1]] and 'P' not in grid_status[new_pos[0]][new_pos[1]]:
            if 'OK' not in grid_status[new_pos[0]][new_pos[1]]: 
                # Mark as safe
                grid_status[new_pos[0]][new_pos[1]].append('OK')    

    # Calculate next move
    prio_not_visited_pos = None
    for move in moves:
        new_pos = (local_agent_pos[0] + move[0], local_agent_pos[1] + move[1])
        sensor_readings = get_sensor_readings(new_pos)
        if sensor_readings[3] == 'Bump':
            continue
        # If not visited and safe
        if 'OK' in grid_status[new_pos[0]][new_pos[1]] and 'V' not in grid_status[new_pos[0]][new_pos[1]]:
            prio_not_visited_pos = (new_pos[0], new_pos[1], move[2])
            break
    
    # Agent priority not visited position
    if prio_not_visited_pos:
        change_agent_direction(prio_not_visited_pos[2])
        local_agent_pos = (prio_not_visited_pos[0], prio_not_visited_pos[1])
        # Mark as now as visited
        if 'V' not in grid_status[new_pos[0]][new_pos[1]]:
            grid_status[new_pos[0]][new_pos[1]].append('V')
    else:
        random.shuffle(moves)
        for move in moves:
            new_pos = (local_agent_pos[0] + move[0], local_agent_pos[1] + move[1])
            # Check if new_pos is adjacent to local_agent_pos
            sensor_readings = get_sensor_readings(new_pos)
            if sensor_readings[3] == 'Bump':
                continue  
            
            # Available moves for agent (labelled as OK)
            if 'OK' in grid_status[new_pos[0]][new_pos[1]]:
                change_agent_direction(move[2])
                local_agent_pos = new_pos
                break
        
        # No more available moves for agent
        if randomize_move():
            for move in moves:
                randomize_adj_pos = (local_agent_pos[0] + move[0], local_agent_pos[1] + move[1])
                sensor_readings = get_sensor_readings(randomize_adj_pos)
                if sensor_readings[3] == 'Bump':
                    continue  
                if all(item not in grid_status[randomize_adj_pos[0]][randomize_adj_pos[1]] for item in ['V', 'W', 'OK']):
                    if 'OK' not in grid_status[randomize_adj_pos[0]][randomize_adj_pos[1]]:
                        grid_status[randomize_adj_pos[0]][randomize_adj_pos[1]].append('OK')
                        break
    
    # Decrease by 1 per move
    agent_gold_amount -= 1
    
    # Check wumpus state and evaluate
    predicted_wumpus_pos = check_wumpus_state(moves)
    if predicted_wumpus_pos:
        # Update the board first
        agent_pos = local_agent_pos
        draw_grid()
        pygame.display.flip()

        # Look agent into the predicted wumpus position
        agent_current_look = calculate_direction(local_agent_pos, predicted_wumpus_pos)
        
        # Throw arrow to the wumpus
        if agent_current_look:
            if agent_gold_amount > 10:
                agent_gold_amount -= 10         # Decrease by 10 per arrow throw
                fireball_pos = set_arrow_pos(agent_current_look)
                display_throw_arrow(fireball_pos)
                if wumpus_pos:
                    grid_status[predicted_wumpus_pos[0]][predicted_wumpus_pos[1]].remove('W')
                    if all(item not in grid_status[predicted_wumpus_pos[0]][predicted_wumpus_pos[1]] for item in ['P', 'OK']):
                        grid_status[predicted_wumpus_pos[0]][predicted_wumpus_pos[1]].append('OK')

    # Check pit state and evaluate
    check_pit_state(moves)
    
    return local_agent_pos
        

# Evaluate wumpus state in grid
def check_wumpus_state(moves):
    for row in range(ROWS):
        for col in range(COLS):
            num_visited_adj = 0
            num_visited_stench = 0
            if 'W' in grid_status[row][col]:
                for move in moves:
                    adj_pos_to_wumpus = (row + move[0], col + move[1])
                    sensor_readings = get_sensor_readings(adj_pos_to_wumpus)
                    if sensor_readings[3] == 'Bump':
                        continue
                    # If stench is adjacent to wumpus is visited
                    if all(item in grid_status[adj_pos_to_wumpus[0]][adj_pos_to_wumpus[1]] for item in ['V', 'OK']):
                        num_visited_adj += 1
                        # If adjacent to pit has breeze
                        if 'S' in grid_status[adj_pos_to_wumpus[0]][adj_pos_to_wumpus[1]]:
                            num_visited_stench += 1
        
                    if num_visited_stench < num_visited_adj and num_visited_stench < 2:
                        # Remove pit and mark as OK
                        if 'W' in grid_status[row][col]:                
                            grid_status[row][col].remove('W')
                        if 'P' not in grid_status[row][col] and 'OK' not in grid_status[row][col]:                
                            grid_status[row][col].append('OK')
                        return
                    elif num_visited_stench >= 2:
                        if 'V' not in grid_status[row][col]:
                            return (row, col)
    return None


# Evaluate pit state in grid
def check_pit_state(moves):
    global grid_status

    for row in range(ROWS):
        for col in range(COLS):
            num_visited_adj = 0
            num_visited_breeze = 0
            if 'P' in grid_status[row][col]:
                for move in moves:
                    adj_pos_to_pit = (row + move[0], col + move[1])
                    sensor_readings = get_sensor_readings(adj_pos_to_pit)
                    if sensor_readings[3] == 'Bump':
                        continue

                    # If adjacent to pit is visited
                    if all(item in grid_status[adj_pos_to_pit[0]][adj_pos_to_pit[1]] for item in ['V', 'OK']):
                        num_visited_adj += 1
                        # If adjacent to pit has breeze
                        if 'B' in grid_status[adj_pos_to_pit[0]][adj_pos_to_pit[1]]:
                            num_visited_breeze += 1

                    # All adjacent to pit that has less than 2 breeze and visited,
                    # can infer that predicted pit is False, and mark as OK.
                    if num_visited_breeze < 2 and num_visited_adj > 1:
                        # Remove pit and mark as OK
                        if 'P' in grid_status[row][col]:                
                            grid_status[row][col].remove('P')
                        if 'W' not in grid_status[row][col] and 'OK' not in grid_status[row][col]:                
                            grid_status[row][col].append('OK')
                        break
                

# Sensor readings for agent moves
def get_sensor_readings(agent_pos):
    sensor_readings = [None, None, None, None, None]

    # Check for stench
    if wumpus_pos:
        if (abs(agent_pos[0] - wumpus_pos[0]) + abs(agent_pos[1] - wumpus_pos[1])) == 1:
            sensor_readings[0] = 'Stench'
    else:
        # Check for scream
        sensor_readings[4] = 'Scream'

    # Check for breeze
    for pit in pit_pos:
        if (abs(agent_pos[0] - pit[0]) + abs(agent_pos[1] - pit[1])) == 1:
            sensor_readings[1] = 'Breeze'
            break

    # Check for glitter
    if agent_pos == gold_pos:
        sensor_readings[2] = 'Glitter'
    # Check for bump
    if agent_pos[0] < 0 or agent_pos[1] < 0 or agent_pos[0] > ROWS-1 or agent_pos[1] > COLS-1:
        sensor_readings[3] = 'Bump'

    return sensor_readings


# Agent will look into the predicted wumpus position
def calculate_direction(agent_pos, target_pos):
    agent_look = None

    if agent_pos[0] == target_pos[0]:
        dx = target_pos[1] - agent_pos[1]
        if dx > 0:
            change_agent_direction('right')
            agent_look = 'right'
        elif dx < 0:
            change_agent_direction('left')
            agent_look = 'left'
    elif agent_pos[1] == target_pos[1]:
        dy = target_pos[0] - agent_pos[0]
        if dy > 0:
            change_agent_direction('up')
            agent_look = 'up'
        elif dy < 0:
            change_agent_direction('down')
            agent_look = 'down'
    # Update the display
    draw_grid()
    pygame.display.flip()
    sleep(0.3)
    return agent_look


# Change agent look direction
def change_agent_direction(direction):
    global agent_img

    if direction == 'right':
        agent_img = right_pos_agent_img
    elif direction == 'up':
        agent_img = up_pos_agent_img
    elif direction == 'left':
        agent_img = left_pos_agent_img
    elif direction == 'down':
        agent_img = bottom_pos_agent_img
    sleep(0.3)
    draw_grid()
    pygame.display.flip()
    sleep(0.3)

    return


# Randomize move if all OK is VISITED, and no more moves
def randomize_move():
    for row in grid_status:
        for cell in row:
            if 'V' not in cell and 'OK' in cell:
                return False
    return True


''' AGENT STATE CHECKING '''
# If agent fell into the pit
def check_agent_pit():
    global agent_pos

    if agent_pos in pit_pos:
        draw_grid()
        pygame.display.flip()
        sleep(0.2)
        print("Agent fell into the pit")
        agent_pos = None
        return True
    return False


# If agent encounter the Wumpus
def check_agent_wumpus():
    global agent_pos 

    if agent_pos == wumpus_pos:
        draw_grid()
        pygame.display.flip()
        sleep(0.1)
        print("Agent encounter the Wumpus")
        agent_pos = None
        return True
    return False


''' INITIALIZATION OF GAME '''
# Initialize the game state
def initialize_game():
    global agent_img, agent_pos, agent_current_look, agent_gold_amount, wumpus_pos, pit_pos, stench_pos, breeze_pos, gold_pos, grid_status
    agent_img = up_pos_agent_img    # Starting agent position
    agent_pos = (0, 0)              # Start at bottom left
    agent_current_look = "up"       # Looking at the top
    agent_gold_amount = 50          # Starting gold amount
    wumpus_pos = None               
    pit_pos = []                    
    stench_pos = []                 
    breeze_pos = []
    gold_pos = None                 
    grid_status = [[[] for _ in range(COLS)] for _ in range(ROWS)]
    grid_status[0][0] = ['OK', 'V']
    grid_status[0][1] = ['OK']
    grid_status[1][0] = ['OK']


''' INSTANCES DISPLAY '''
# Display gold position
def generate_gold():
    global gold_pos

    while True:
        get_gold_pos = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
        if get_gold_pos not in [(0,0), (1,0), (0,1), (1,1)] and get_gold_pos not in pit_pos and get_gold_pos != wumpus_pos:
            gold_pos = get_gold_pos
            break


# Display pits position
def generate_pit():
    global pit_pos

    num_of_pit = random.randint(2, 3)
    for _ in range(num_of_pit):
        while True:
            get_pit_pos = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
            if get_pit_pos not in [(0,0), (1,0), (0,1), (1,1)] and get_pit_pos not in pit_pos and get_pit_pos != wumpus_pos and get_pit_pos not in stench_pos:
                pit_pos.append(get_pit_pos)
                break 

    for pos in pit_pos:
        row, col = pos
        if row > 0 and (row - 1, col) not in pit_pos:
            breeze_pos.append((row - 1, col))
        if row < ROWS-1 and (row + 1, col) not in pit_pos:
            breeze_pos.append((row + 1, col))
        if col > 0 and (row, col - 1) not in pit_pos:
            breeze_pos.append((row, col - 1))
        if col < COLS-1 and (row, col + 1) not in pit_pos:
            breeze_pos.append((row, col + 1))


# Display wumpus position
def generate_wumpus():
    global wumpus_pos, stench_pos

    while True:
        wumpus_pos = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
        if wumpus_pos not in [(0,0), (1,0), (0,1), (1,1)]:
            row, col = wumpus_pos
            if row > 0:
                stench_pos.append((row - 1, col))
            if row < ROWS-1:
                stench_pos.append((row + 1, col))
            if col > 0:
                stench_pos.append((row, col - 1))
            if col < COLS-1:
                stench_pos.append((row, col + 1))
            break


# Set fireball position and its direction 
def set_arrow_pos(agent_direction):
    fireball_pos = []
    current_pos_agent = list(agent_pos)

    if agent_direction == "up":
        fireball_pos.append("up")
        while current_pos_agent[0] < ROWS - 1:
            current_pos_agent[0] += 1
            fireball_pos.append((current_pos_agent[0], agent_pos[1]))
    elif agent_direction == "down":
        fireball_pos.append("down")
        while current_pos_agent[0] > 0:
            current_pos_agent[0] -= 1
            fireball_pos.append((current_pos_agent[0], agent_pos[1]))
    elif agent_direction == "right":
        fireball_pos.append("right")
        while current_pos_agent[1] < COLS - 1:
            current_pos_agent[1] += 1
            fireball_pos.append((agent_pos[0], current_pos_agent[1]))
    elif agent_direction == "left":
        fireball_pos.append("left")
        while current_pos_agent[1] > 0:
            current_pos_agent[1] -= 1
            fireball_pos.append((agent_pos[0], current_pos_agent[1]))
    return fireball_pos


# Display throwed fireball direction
def display_throw_arrow(fireball_pos):
    global wumpus_pos, grid_status

    # Make it center display in grid position
    fireball_offset_x = (SQUARE_SIZE - fireball_img.get_width()) // 2
    fireball_offset_y = (SQUARE_SIZE - fireball_img.get_height()) // 2
    
    arrow_direction = fireball_pos.pop(0)
    if arrow_direction == "up":
        rotate_fireball_img = pygame.transform.rotate(fireball_img, 90)
    elif arrow_direction == "down":
        rotate_fireball_img = pygame.transform.rotate(fireball_img, -90)
    elif arrow_direction == "right":
        rotate_fireball_img = fireball_img
    elif arrow_direction == "left":
        rotate_fireball_img = pygame.transform.rotate(fireball_img, 180)

    # Starting from character throw display
    screen.blit(rotate_fireball_img, (agent_pos[1] * SQUARE_SIZE + fireball_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - agent_pos[0]) * SQUARE_SIZE + fireball_offset_y))
    pygame.display.flip()
    sleep(0.3)          # arrow delay
    draw_grid()
    
    # Then, the arrow position display
    for pos in fireball_pos:
        screen.blit(rotate_fireball_img, (pos[1] * SQUARE_SIZE + fireball_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - pos[0]) * SQUARE_SIZE + fireball_offset_y))
        pygame.display.flip()
        sleep(0.3)          # arrow delay
        draw_grid()         # Remove the current position of arrow for update the next position
        if pos == wumpus_pos:
            grid_status[wumpus_pos[0]][wumpus_pos[1]].remove('W')
            grid_status[wumpus_pos[0]][wumpus_pos[1]].append('SCREAM')
            wumpus_pos = None
            return
    return
        

# Display fell in pit message container
def display_fell_in_pit_container():
    rect_color = (212, 25, 54) 
    rect_pos = ((WIDTH - 350) // 2, (HEIGHT - 70) // 2, 350, 70)
    pygame.draw.rect(screen, rect_color, rect_pos)

    text_color = WHITE  
    text = font.render("Agent dead, You failed!", True, text_color)
    text_rect = text.get_rect(center=((WIDTH // 2, HEIGHT // 2)))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


# Display agent killed the wumpus message container
def display_killed_wumpus_container():
    rect_color = (13, 104, 35) 
    rect_pos = ((WIDTH - 400) // 2, (HEIGHT - 70) // 2, 400, 70)
    pygame.draw.rect(screen, rect_color, rect_pos)

    text_color = WHITE  
    text = font.render("You killed the Wumpus, You won!", True, text_color)
    text_rect = text.get_rect(center=((WIDTH // 2, HEIGHT // 2)))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


# Display wumpus killed the agent message container
def display_player_killed_container():
    rect_color = (212, 25, 54) 
    rect_pos = ((WIDTH - 400) // 2, (HEIGHT - 70) // 2, 400, 70)
    pygame.draw.rect(screen, rect_color, rect_pos)

    text_color = WHITE  
    text = font.render("Wumpus killed you, You failed!", True, text_color)
    text_rect = text.get_rect(center=((WIDTH // 2, HEIGHT // 2)))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


# Display no more gold message container
def display_no_gold_container():
    rect_color = (212, 25, 54) 
    rect_pos = ((WIDTH - 400) // 2, (HEIGHT - 70) // 2, 400, 70)
    pygame.draw.rect(screen, rect_color, rect_pos)

    text_color = WHITE  
    text = font.render("No gold left, You lost!", True, text_color)
    text_rect = text.get_rect(center=((WIDTH // 2, HEIGHT // 2)))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


# Display navigation button container
def display_nav_button_container():
    button_width = 150
    button_height = 40
    restart_button_pos = ((WIDTH - button_width) - 350, (HEIGHT - button_height) // 1.3, button_width, button_height)
    exit_button_pos = ((WIDTH - button_width) - 150, (HEIGHT - button_height) // 1.3, button_width, button_height) 

    # Create the buttons
    restart_button = pygame.Rect(restart_button_pos[0], restart_button_pos[1], button_width, button_height)
    exit_button = pygame.Rect(exit_button_pos[0], exit_button_pos[1], button_width, button_height) 

    # Draw the buttons
    pygame.draw.rect(screen, BLACK, restart_button)
    pygame.draw.rect(screen, BLACK, exit_button)

    # Render the text
    restart_text = font.render("Restart", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)

    # Position the text in the middle of its corresponding button
    restart_text_pos = restart_text.get_rect(center=(restart_button_pos[0] + button_width // 2, restart_button_pos[1] + button_height // 2))
    exit_text_pos = exit_text.get_rect(center=(exit_button_pos[0] + button_width // 2, exit_button_pos[1] + button_height // 2))

    # Display the text
    screen.blit(restart_text, restart_text_pos)
    screen.blit(exit_text, exit_text_pos)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if restart_button.collidepoint(mouse_pos):
                    return False
                elif exit_button.collidepoint(mouse_pos):
                    return True


# Display the grid with agent, wumpus, pit, gold, stench, breeze
def draw_grid():
    # Draw info display
    info_display_rect = pygame.Rect(0, 0, WIDTH, INFO_DISPLAY_HEIGHT)
    pygame.draw.rect(screen, WHITE, info_display_rect)
    
    # Draw the gold status on display
    gold_info_offset_x = (INFO_DISPLAY_HEIGHT - gold_img.get_width()) // 2
    gold_info_offset_y = (INFO_DISPLAY_HEIGHT - gold_img.get_height()) // 2
    gold_img_resized = pygame.transform.scale(gold_img, (30, 30))
    screen.blit(gold_img_resized, (gold_info_offset_x + 50, gold_info_offset_y + 15))

    # Draw the amount of gold on display
    text = font.render(f"{agent_gold_amount}", True, BLACK)
    screen.blit(text, (gold_info_offset_x + 50 + gold_img_resized.get_width() + 10, gold_info_offset_y + 20))

    # Draw the board
    for row in range(ROWS):
        for col in range(COLS):
            screen.blit(floor_img, (col * SQUARE_SIZE, INFO_DISPLAY_HEIGHT + (ROWS - 1 - row) * SQUARE_SIZE))

    if wumpus_pos:
        # Draw the wumpus
        wumpus_offset_x = (SQUARE_SIZE - wumpus_img.get_width()) // 2
        wumpus_offset_y = (SQUARE_SIZE - wumpus_img.get_height()) // 2
        screen.blit(wumpus_img, (wumpus_pos[1] * SQUARE_SIZE + wumpus_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - wumpus_pos[0]) * SQUARE_SIZE + wumpus_offset_y))

        # Draw the adjacent stench
        stench_offset_x = (SQUARE_SIZE - stench_img.get_width()) // 2
        stench_offset_y = 20
        for pos in stench_pos:
            screen.blit(stench_img, (pos[1] * SQUARE_SIZE + stench_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - pos[0]) * SQUARE_SIZE + stench_offset_y))

    # Draw the pit/s
    pit_offset_x = (SQUARE_SIZE - pit_img.get_width()) // 2
    pit_offset_y = (SQUARE_SIZE - pit_img.get_height()) // 2
    for pos in pit_pos:
        screen.blit(pit_img, (pos[1] * SQUARE_SIZE + pit_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - pos[0]) * SQUARE_SIZE + pit_offset_y))

    # Draw the adjacent breeze
    breeze_offset_x = (SQUARE_SIZE - breeze_img.get_width()) // 2
    breeze_offset_y = (SQUARE_SIZE - breeze_img.get_height()) - 20
    for pos in breeze_pos:
        screen.blit(breeze_img, (pos[1] * SQUARE_SIZE + breeze_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - pos[0]) * SQUARE_SIZE + breeze_offset_y))
    
    if gold_pos:
        # Draw the gold
        gold_offset_x = (SQUARE_SIZE - gold_img.get_width()) // 2
        gold_offset_y = (SQUARE_SIZE - gold_img.get_height()) // 2
        screen.blit(gold_img, (gold_pos[1] * SQUARE_SIZE + gold_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - gold_pos[0]) * SQUARE_SIZE + gold_offset_y))

    if agent_pos:
        # Draw the agent
        agent_offset_x = (SQUARE_SIZE - up_pos_agent_img.get_width()) // 2
        agent_offset_y = (SQUARE_SIZE - up_pos_agent_img.get_height()) // 2
        screen.blit(agent_img, (agent_pos[1] * SQUARE_SIZE + agent_offset_x, INFO_DISPLAY_HEIGHT + (ROWS - 1 - agent_pos[0]) * SQUARE_SIZE + agent_offset_y))

    # Draw the blockage for undiscovered area
    for row in range(ROWS):
        for col in range(COLS):
            if 'V' not in grid_status[row][col]:
                screen.blit(undiscovered_area_img, (col * SQUARE_SIZE, INFO_DISPLAY_HEIGHT + (ROWS - 1 - row) * SQUARE_SIZE))


# For logging grid sensors
def print_grid():
    print("AGENT KNOWLEDGE:")
    print(f"{grid_status[3][0]} {grid_status[3][1]} {grid_status[3][2]} {grid_status[3][3]}")
    print(f"{grid_status[2][0]} {grid_status[2][1]} {grid_status[2][2]} {grid_status[2][3]}")
    print(f"{grid_status[1][0]} {grid_status[1][1]} {grid_status[1][2]} {grid_status[1][3]}")
    print(f"{grid_status[0][0]} {grid_status[0][1]} {grid_status[0][2]} {grid_status[0][3]}")
    print("="*45)


# MAIN FUNCTION
if __name__ == "__main__":
    while True:
        initialize_game()
        clock = pygame.time.Clock()
        running = True
        player_lose = False

        # Generate instances
        generate_wumpus()
        generate_pit()
        generate_gold()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
            if agent_gold_amount > 0:
                agent_pos = decide_next_move(agent_pos)    
                print_grid()

                is_agent_fell = check_agent_pit()
                is_agent_encounter_wumpus = check_agent_wumpus()
                draw_grid()
                pygame.display.flip()
                
                if is_agent_fell:
                    running = False
                    display_fell_in_pit_container()
                elif is_agent_encounter_wumpus:
                    running = False
                    display_player_killed_container()
                elif wumpus_pos == None:
                    running = False
                    display_killed_wumpus_container()
                
            else:
                running = False
                display_no_gold_container()

        # Restart or Exit the game
        if not running:
            is_exit = display_nav_button_container()
            if is_exit:
                break

    pygame.quit()
    sys.exit()
