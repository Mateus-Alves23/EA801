from machine import Pin, ADC, SoftI2C, PWM
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C

# ----- OLED -----
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# ----- BUZZER (GPIO21) -----
buzzer = PWM(Pin(21))
buzzer.duty_u16(0)

def start_race_sound(j):
    # Notas: 3 tons iguais + 1 mais agudo e longo
    notes = [440]  # A, A, A, A5
    durations = [0.3]
    volume = 1000
    if j == 2:
        notes = [440, 880]
        durations = [0.6, 0.3]
    for i in range(len(notes)):
        buzzer.freq(notes[i])
        buzzer.duty_u16(volume)
        utime.sleep(durations[i])
        buzzer.duty_u16(0)
        utime.sleep(0.1)  # pausa entre os bips

def game_over_sound():
    notes = [659, 523, 415, 330]
    durations = [0.2, 0.2, 0.2, 0.5]
    volume = 1000
    for i in range(len(notes)):
        buzzer.freq(notes[i])
        buzzer.duty_u16(volume)
        utime.sleep(durations[i])
    buzzer.duty_u16(0)

def victory_sound():
    notes = [523, 523, 659, 784]
    durations = [0.2, 0.2, 0.3, 0.7]
    volume = 1000
    for i in range(len(notes)):
        buzzer.freq(notes[i])
        buzzer.duty_u16(volume)
        utime.sleep(durations[i])
    buzzer.duty_u16(0)

# ----- MATRIZ DE LED -----
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5,  6,  7,  8,  9],
    [4,  3,  2,  1,  0]
]

# ----- NÚMEROS PARA A MATRIZ 5x5 -----
NUMBERS = {
    3: [
        [0,1,1,1,0],
        [0,0,0,1,0],
        [0,0,1,1,0],
        [0,0,0,1,0],
        [0,1,1,1,0]
    ],
    2: [
        [0,1,1,1,0],
        [0,0,0,1,0],
        [0,1,1,1,0],
        [0,1,0,0,0],
        [0,1,1,1,0]
    ],
    1: [
        [0,0,1,0,0],
        [0,1,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,1,1,1,0]
    ]
}

def show_number_on_matrix(n, color=(0, 0, 50)):
    np.fill((0, 0, 0))
    if n in NUMBERS:
        matrix = NUMBERS[n]
        for y in range(5):
            for x in range(5):
                if matrix[y][x]:
                    np[LED_MATRIX[y][x]] = color
    np.write()

def countdown():
    for i in [3, 2, 1]:
        show_number_on_matrix(i)
        oled.fill(0)
        oled.text("Iniciando em:", 0, 0)
        oled.text(str(i) + "...", 0, 20)
        oled.show()
        utime.sleep(1)
        start_race_sound(1)
        if i == 1:
            start_race_sound(2)
    np.fill((0, 0, 0))
    np.write()
    oled.fill(0)
    oled.show()

# ----- JOYSTICK -----
joy_x = ADC(Pin(27))
joy_y = ADC(Pin(26))

def get_direction():
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    if x < 10000: return 'LEFT'
    if x > 55000: return 'RIGHT'
    if y < 10000: return 'DOWN'
    if y > 55000: return 'UP'
    return None

# ----- BOTÃO A (GPIO5) -----
button_start = Pin(5, Pin.IN, Pin.PULL_UP)

# ----- VARIÁVEIS DO JOGO -----
snake = [(2, 2)]
direction = 'UP'
food = (random.randint(0, 4), random.randint(0, 4))
score = 0
VICTORY_SCORE = 10
waiting_to_start = True

def reset_game():
    global snake, direction, food, score, waiting_to_start
    snake = [(2, 2)]
    direction = 'UP'
    food = (random.randint(0, 4), random.randint(0, 4))
    score = 0
    waiting_to_start = True

def draw():
    np.fill((0, 0, 0))
    for segment in snake:
        np[LED_MATRIX[segment[1]][segment[0]]] = (0, 30, 0)
    if not waiting_to_start:
        np[LED_MATRIX[food[1]][food[0]]] = (50, 0, 0)
    np.write()

    oled.fill(0)
    if waiting_to_start:
        oled.text("Aperte A para", 0, 0)
        oled.text("iniciar", 0, 16)
    else:
        oled.text("Score:", 0, 0)
        oled.text(str(score), 60, 0)
    oled.show()

def move():
    global food, score
    head_x, head_y = snake[0]

    if direction == 'UP': head_y -= 1
    elif direction == 'DOWN': head_y += 1
    elif direction == 'LEFT': head_x -= 1
    elif direction == 'RIGHT': head_x += 1

    head_x %= 5
    head_y %= 5

    new_head = (head_x, head_y)

    if new_head in snake:
        return False

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        while food in snake:
            food = (random.randint(0, 4), random.randint(0, 4))
    else:
        snake.pop()

    return True

# ----- LOOP PRINCIPAL -----
reset_game()

while True:
    while waiting_to_start:
        draw()
        if button_start.value() == 0:
            countdown()
            waiting_to_start = False
            utime.sleep(0.3)

    new_dir = get_direction()
    if new_dir:
        direction = new_dir

    if not move():
        np.fill((50, 0, 0))
        np.write()
        oled.fill(0)
        oled.text("Game Over!", 0, 0)
        oled.text("Score: " + str(score), 0, 16)
        oled.show()
        game_over_sound()
        utime.sleep(2)
        reset_game()
        continue

    elif score >= VICTORY_SCORE:
        np.fill((0, 0, 50))
        np.write()
        oled.fill(0)
        oled.text("PARABENS!", 10, 20)
        oled.show()
        victory_sound()
        utime.sleep(3)
        reset_game()
        continue

    else:
        draw()

    utime.sleep(0.5)