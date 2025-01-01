import pygame
import time
from math import sqrt
from scipy.interpolate import splprep, splev

# Initialize Pygame
pygame.init()
HIT_RADIUS = 10
SCALAR = 3
WINDOW_WIDTH, WINDOW_HEIGHT = 512*SCALAR, 384*SCALAR  
BG_COLOR = (0, 0, 0) 
DEFAULT_TRAIL_COLOR = (255, 255, 255)  
ACTIVE_TRAIL_COLOR = (255, 0, 0)  
TRAIL_DURATION_MS = 1000 

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Input Capture Tool")
clock = pygame.time.Clock()

mouse_trail = []
trail_color = DEFAULT_TRAIL_COLOR

processed_inputs = []
current_stroke = []

program_start_time = time.time()
def remove_duplicates(arr):
    result = []
    for item in arr:
        if not result or item[1] != result[-1][1] or item[2] != result[-1][2]:
            result.append(item)
    return result

def get_bezier(stroke_points):
    if len(stroke_points) < 2:
        return []
    stroke_points = remove_duplicates(stroke_points)

    time_ms = [pt[0] for pt in stroke_points]
    x_coords = [pt[1] for pt in stroke_points]
    y_coords = [pt[2] for pt in stroke_points]
    time_range = time_ms[-1] - time_ms[0]
    num_control_points = 2+int(20 * (time_range/1000.0))

    tck, _ = splprep([x_coords, y_coords], s=0)
    u_new = [i / (num_control_points - 1) for i in range(num_control_points)]
    x_new, y_new = splev(u_new, tck)
    return list(zip(x_new, y_new))
def process_inputs(mouse_x, mouse_y):
    current_time_ms = int((time.time() - program_start_time) * 1000)  # Time in ms since program start
    current_stroke.append((current_time_ms, mouse_x, mouse_y))

def process_stroke():
    if not current_stroke:
        return
    is_slider = False     
    # if all mouse movements are contained in circle starting from first position, then save brush movement as hit    
    time0,x0,y0 = current_stroke[0]
    for item in current_stroke:
        _,x,y = item
        delta_p = sqrt((x0-x)*(x0-x)+(y0-y)*(y0-y))
        print(HIT_RADIUS)
        if(delta_p>HIT_RADIUS):
            is_slider=True
            break
    if(is_slider):
        array = get_bezier(current_stroke)
        bezier_str = ""
        for i, item in enumerate(array):
            if(i==0):
                continue
            bezier_str+=f'|{int(item[0])}:{int(item[1])}'
        processed_inputs.append(f'{x0},{y0},{time0},2,0,B{bezier_str},1\n')
    else:
        processed_inputs.append(f'{x0},{y0},{time0},1,0\n')

running = True
drawing = False

pygame.mixer.init()
pygame.mixer.music.load("audio.mp3")
pygame.mixer.music.play()
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_e):
                trail_color = ACTIVE_TRAIL_COLOR  # Change trail color to red
                if not drawing:
                    drawing = not drawing
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_e):
                trail_color = DEFAULT_TRAIL_COLOR  # Revert to default trail color
                if drawing:
                    drawing = not drawing
                    process_stroke()
                    current_stroke = []
    mouse_x, mouse_y = pygame.mouse.get_pos()

    current_time = time.time() * 1000  # Current time in milliseconds
    mouse_trail.append((mouse_x, mouse_y, current_time, trail_color))

    mouse_trail = [(x, y, t, c) for x, y, t, c in mouse_trail if current_time - t <= TRAIL_DURATION_MS]

    if drawing:
        process_inputs(int(mouse_x/SCALAR), int(mouse_y/SCALAR))

    for x, y, _, color in mouse_trail:
        pygame.draw.circle(screen, color, (x, y), 3)

    pygame.display.flip()

    clock.tick(1000)  # Limit to 1000 frames per second for millisecond updates

pygame.quit()

with open("test.txt", 'w') as f:
    for row in processed_inputs:
        f.write(row)