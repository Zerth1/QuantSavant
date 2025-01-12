import math
import random
from enum import Enum, auto
from pyray import *
RESOLUTION_X = 1450
RESOLUTION_Y = 800
DIGIT_PROCESSING_SETTINGS = {
    "Span": 5, # Minimum: 4 | Maximum: 20
    "Generations": 2,
    "Interval": 1.0,
}
FLASH_ANZAN_SETTINGS = {
    "Span": 2,
    "Generations": 3,
    "Interval": 1.0
}
ANAGRAMING_SETTINGS = {
    "Span": 10,
    "LookTime": 1.0,
}
class GameState(Enum):
    LOBBY = auto()
    PLAYING = auto()
    RESULTS = auto()
    SETTINGS = auto()
    STATS = auto()
class GameMode(Enum):
    DIGIT_PROCESSING = auto()
    FLASH_ANZAN = auto()
    ANAGRAMING = auto()
game_state = GameState.LOBBY
game_mode = GameMode.DIGIT_PROCESSING
interval_clock = 0.0
results_clock = 0.0
def lobby_selection():
    global game_state
    global interval_clock
    current_position = get_mouse_position()
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        if check_collision_point_rec(current_position, Rectangle(20.0, 50.0, measure_text("Settings", 25), 25)): # Settings Click
            game_state = GameState.SETTINGS
        elif check_collision_point_rec(current_position, Rectangle(20.0, 100.0, measure_text("Stats", 25), 25)): # Stats Click
            game_state = GameState.STATS
        elif check_collision_point_rec(current_position, Rectangle(int(725 - (measure_text("Play", 50) / 2)), 600, measure_text("Play", 50), 50)): # Play Click
            interval_clock = get_time()
            game_state = GameState.PLAYING
def gamemode_selection():
    global game_mode
    draw_text("Digit Processing", int(725 - (measure_text("Digit Processing", 25) / 2)), 250, 25, GREEN)
    draw_text("Flash Anzan", int(725 - (measure_text("Flash Anzan", 25) / 2)), 325, 25, GREEN)
    draw_text("Anagraming", int(725 - (measure_text("Anagraming", 25) / 2)), 400, 25, GREEN)
    current_position = get_mouse_position()
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        if check_collision_point_rec(current_position, Rectangle(int(725 - (measure_text("Digit Processing", 25) / 2)), 250, measure_text("Digit Processing", 25), 25)):
            game_mode = GameMode.DIGIT_PROCESSING
        elif check_collision_point_rec(current_position, Rectangle(int(725 - (measure_text("Flash Anzan", 25) / 2)), 325, measure_text("Flash Anzan", 25), 25)):
            game_mode = GameMode.FLASH_ANZAN
        elif check_collision_point_rec(current_position, Rectangle(int(725 - (measure_text("Anagraming", 25) / 2)), 400, measure_text("Anagraming", 25), 25)):
            game_mode = GameMode.ANAGRAMING
    match game_mode:
        case GameMode.DIGIT_PROCESSING:
            draw_rectangle_lines(int(725 - (measure_text("Digit Processing", 25) / 2)) - 25, 250 - 25, measure_text("Digit Processing", 25) + 50, 75, RED)
        case GameMode.FLASH_ANZAN:
            draw_rectangle_lines(int(725 - (measure_text("Flash Anzan", 25) / 2)) - 25, 325 - 25, measure_text("Flash Anzan", 25) + 50, 75, RED)
        case GameMode.ANAGRAMING:
            draw_rectangle_lines(int(725 - (measure_text("Anagraming", 25) / 2)) - 25, 400 - 25, measure_text("Anagraming", 25) + 50, 75, RED)
init_window(RESOLUTION_X, RESOLUTION_Y, "QuantSavant")
digit_processing_number = ""
digit_processing_generations = 0
digit_processing_list = []
digit_processing_noise = []
digit_processing_combined = []
digit_processing_evaluation_index = 0

flash_anzan_number = ""
flash_anzan_input = ""
flash_anzan_generations = 0
flash_anzan_list = []

anagraming_number = ""
shuffled_anagram = ""
is_generating_anagram = False
anagram_clock = 0.0

is_evaluate_time = False
in_evaluation = False
is_correct = False
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    if get_time() > max(DIGIT_PROCESSING_SETTINGS["Interval"], FLASH_ANZAN_SETTINGS["Interval"]):
        match game_state:
            case GameState.LOBBY:
                draw_text("QuantSavant", int(725 - (measure_text("QuantSavant", 50) / 2)), 125, 50, WHITE)
                draw_text("Settings", 20, 50, 25, WHITE)
                draw_text("Stats", 20, 100, 25, WHITE)
                draw_text("Play", int(725 - (measure_text("Play", 50) / 2)), 600, 50, WHITE)
                lobby_selection()
                gamemode_selection()
            case GameState.SETTINGS:
                pass
            case GameState.STATS:
                pass
            case GameState.PLAYING:
                match game_mode:
                    case GameMode.DIGIT_PROCESSING:
                        if is_evaluate_time:
                            if in_evaluation:
                                if digit_processing_evaluation_index == len(digit_processing_combined) - 1:
                                    is_correct = True
                                    game_state = GameState.RESULTS
                                    is_evaluate_time = False
                                    in_evaluation = False
                                    digit_processing_number = ""
                                    digit_processing_generations = 0
                                    digit_processing_list = []
                                    digit_processing_noise = []
                                    digit_processing_combined = []
                                    digit_processing_evaluation_index = 0
                                else:
                                    current_check = digit_processing_combined[digit_processing_evaluation_index]
                                    draw_text(current_check, int(725 - (measure_text(current_check, 50) / 2)), 400 - 50, 50, WHITE)
                                    draw_text("NO", int(725 - (measure_text("NO", 50) / 2)) - 100, 550, 50, WHITE)
                                    draw_text("YES", int(725 - (measure_text("YES", 50) / 2)) + 100, 550, 50, WHITE)
                                    current_position = get_mouse_position()
                                    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                                        if check_collision_point_rec(current_position, Rectangle(725 - (measure_text("NO", 50) / 2) - 100, 550.0, measure_text("NO", 50), 50)):
                                            if current_check in digit_processing_list:
                                                is_correct = False
                                                game_state = GameState.RESULTS
                                                is_evaluate_time = False
                                                in_evaluation = False
                                                digit_processing_number = ""
                                                digit_processing_generations = 0
                                                digit_processing_list = []
                                                digit_processing_noise = []
                                                digit_processing_combined = []
                                                digit_processing_evaluation_index = 0
                                            else:
                                                digit_processing_evaluation_index += 1
                                        elif check_collision_point_rec(current_position, Rectangle(725 - (measure_text("YES", 50) / 2) + 100, 550.0, measure_text("YES", 50), 50)):
                                            if not current_check in digit_processing_list:
                                                is_correct = False
                                                game_state = GameState.RESULTS
                                                is_evaluate_time = False
                                                in_evaluation = False
                                                digit_processing_number = ""
                                                digit_processing_generations = 0
                                                digit_processing_list = []
                                                digit_processing_noise = []
                                                digit_processing_combined = []
                                                digit_processing_evaluation_index = 0
                                            else:
                                                digit_processing_evaluation_index += 1           
                            else:
                                in_evaluation = True
                                current_index = 0
                                for i in range(4 * DIGIT_PROCESSING_SETTINGS["Generations"]):
                                    if i != 0 and i % 4 == 0:
                                        current_index += 1
                                    current_number = digit_processing_list[current_index]
                                    splice = list(current_number[1:len(current_number) - 1])
                                    splice_count = list(range(len(splice)))
                                    random.shuffle(splice_count)
                                    to_shuffle = splice_count[:min(int(math.ceil(len(splice) / 2)), 5)]
                                    for j in to_shuffle:
                                        remaining_digits = list(range(10))
                                        original_digit = int(splice[j])
                                        remaining_digits.remove(original_digit)
                                        splice[j] = str(random.choice(remaining_digits))
                                    digit_processing_noise.append(current_number[0] + ''.join(splice) + current_number[len(current_number) - 1])
                                digit_processing_combined = digit_processing_list + digit_processing_noise
                                random.shuffle(digit_processing_combined)
                        else:
                            time_elapsed = get_time() - interval_clock
                            if time_elapsed > DIGIT_PROCESSING_SETTINGS["Interval"]:
                                interval_clock = get_time()
                                digit_processing_number = ""
                                digit_processing_generations += 1
                                if digit_processing_generations == DIGIT_PROCESSING_SETTINGS["Generations"] + 1:
                                    is_evaluate_time = True
                                    digit_processing_generations = 0
                                else:
                                    remaining_digits = list(range(10))
                                    for i in range(DIGIT_PROCESSING_SETTINGS["Span"]):
                                        if i == 0:
                                            digit_processing_number += str(random.randint(1, 9))
                                        else:
                                            if i % 9 == 0:
                                                remaining_digits = list(range(10))
                                            chosen_one = random.choice(remaining_digits)
                                            remaining_digits.remove(chosen_one)
                                            digit_processing_number += str(chosen_one)
                                    digit_processing_list.append(digit_processing_number)
                            draw_text(digit_processing_number, int(725 - (measure_text(digit_processing_number, 50) / 2)), 400 - 50, 50, WHITE)
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            is_evaluate_time = False
                            digit_processing_number = ""
                            digit_processing_generations = 0
                            digit_processing_list = []
                            digit_processing_noise = []
                            digit_processing_combined = []
                            digit_processing_evaluation_index = 0
                    case GameMode.FLASH_ANZAN:
                        if is_evaluate_time:
                            draw_text("Enter Sum:", int(725 - (measure_text("Enter Sum:", 50) / 2)), 400 - 50, 50, WHITE)
                            draw_rectangle(int(725 + (measure_text("0000000000", 50) / 2)), 400 - 50, measure_text("0000000000", 50), 50, WHITE)
                            pressed_key = get_key_pressed()
                            if pressed_key >= 48 and pressed_key <= 57:
                                flash_anzan_input += chr(pressed_key)
                            if is_key_pressed(KeyboardKey.KEY_BACKSPACE):
                                flash_anzan_input = flash_anzan_input[:-1]
                            elif is_key_pressed(KeyboardKey.KEY_ENTER):
                                is_correct = str(sum(flash_anzan_list)) == flash_anzan_input
                                game_state = GameState.RESULTS
                                is_evaluate_time = False
                                flash_anzan_number = ""
                                flash_anzan_input = ""
                                flash_anzan_generations = 0
                                flash_anzan_list = []
                            to_write = flash_anzan_input
                            if int(get_time()) % 2 == 0:
                                to_write += "_"
                            draw_text(to_write, int(725 + (measure_text("0000000000", 50) / 2)), 400 - 50, 50, BLACK)
                        else:
                            time_elapsed = get_time() - interval_clock
                            if time_elapsed > FLASH_ANZAN_SETTINGS["Interval"]:
                                interval_clock = get_time()
                                flash_anzan_number = ""
                                flash_anzan_generations += 1
                                if flash_anzan_generations == FLASH_ANZAN_SETTINGS["Generations"] + 1:
                                    is_evaluate_time = True
                                    flash_anzan_generations = 0
                                else:
                                    remaining_digits = list(range(10))
                                    for i in range(FLASH_ANZAN_SETTINGS["Span"]):
                                        if i == 0:
                                            flash_anzan_number += str(random.randint(1, 9))
                                        else:
                                            if i % 9 == 0:
                                                remaining_digits = list(range(10))
                                            chosen_one = random.choice(remaining_digits)
                                            remaining_digits.remove(chosen_one)
                                            flash_anzan_number += str(chosen_one)
                                    flash_anzan_list.append(int(flash_anzan_number))
                            draw_text(flash_anzan_number, int(725 - (measure_text(flash_anzan_number, 50) / 2)), 400 - 50, 50, WHITE)
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            is_evaluate_time = False
                            flash_anzan_number = ""
                            flash_anzan_input = ""
                            flash_anzan_generations = 0
                            flash_anzan_list = []
                    case GameMode.ANAGRAMING:
                        if not is_generating_anagram:
                            is_generating_anagram = True
                            remaining_digits = list(range(10))
                            for i in range(ANAGRAMING_SETTINGS["Span"]):
                                if i == 0:
                                    anagraming_number += str(random.randint(1, 9))
                                else:
                                    if i % 9 == 0:
                                        remaining_digits = list(range(10))
                                    chosen_one = random.choice(remaining_digits)
                                    remaining_digits.remove(chosen_one)
                                    anagraming_number += str(chosen_one)
                            anagram_clock = get_time()
                        else:
                            time_elapsed = get_time() - anagram_clock              
                            if time_elapsed < ANAGRAMING_SETTINGS["LookTime"]:
                                draw_text(anagraming_number, int(725 - (measure_text(anagraming_number, 50) / 2)), 400 - 50, 50, WHITE)
                            else:
                                if not in_evaluation:
                                    in_evaluation = True
                                    shuffled_anagram = list(anagraming_number)
                                    random.shuffle(shuffled_anagram)
                                    if random.randint(0, 1) == 0:
                                        splice = list(shuffled_anagram[1:len(shuffled_anagram) - 1])
                                        splice_count = list(range(len(splice)))
                                        random.shuffle(splice_count)
                                        to_shuffle = splice_count[:min(int(math.ceil(len(splice) / 3)), 5)]
                                        for j in to_shuffle:
                                            remaining_digits = list(range(10))
                                            original_digit = int(splice[j])
                                            remaining_digits.remove(original_digit)
                                            splice[j] = str(random.choice(remaining_digits))
                                        shuffled_anagram = shuffled_anagram[0] + ''.join(splice) + shuffled_anagram[len(shuffled_anagram) - 1]
                                    else:
                                        shuffled_anagram = ''.join(shuffled_anagram)
                                draw_text(shuffled_anagram, int(725 - (measure_text(shuffled_anagram, 50) / 2)), 400 - 50, 50, WHITE)
                                draw_text("NO", int(725 - (measure_text("NO", 50) / 2)) - 100, 550, 50, WHITE)
                                draw_text("YES", int(725 - (measure_text("YES", 50) / 2)) + 100, 550, 50, WHITE)
                                current_position = get_mouse_position()
                                if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                                    original_anagram = list(anagraming_number)
                                    new_anagram = list(shuffled_anagram)
                                    original_anagram.sort()
                                    new_anagram.sort()
                                    if check_collision_point_rec(current_position, Rectangle(725 - (measure_text("NO", 50) / 2) - 100, 550.0, measure_text("NO", 50), 50)):
                                        is_correct = original_anagram != new_anagram
                                        game_state = GameState.RESULTS
                                        in_evaluation = False   
                                        anagraming_number = ""
                                        shuffled_anagram = ""
                                        is_generating_anagram = False
                                        anagram_clock = 0.0           
                                    elif check_collision_point_rec(current_position, Rectangle(725 - (measure_text("YES", 50) / 2) + 100, 550.0, measure_text("YES", 50), 50)):
                                        is_correct = original_anagram == new_anagram
                                        game_state = GameState.RESULTS
                                        in_evaluation = False
                                        anagraming_number = ""
                                        shuffled_anagram = ""
                                        is_generating_anagram = False
                                        anagram_clock = 0.0
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            in_evaluation = False   
                            anagraming_number = ""
                            shuffled_anagram = ""
                            is_generating_anagram = False
                            anagram_clock = 0.0
            case GameState.RESULTS:
                if results_clock == 0.0:
                    results_clock = get_time()
                if get_time() - results_clock > 1.0:
                    game_state = GameState.LOBBY
                    results_clock = 0.0
                if is_correct:
                    draw_text("CORRECT", int(725 - (measure_text("CORRECT", 50) / 2)), 400 - 50, 50, GREEN)
                else:
                    draw_text("WRONG", int(725 - (measure_text("WRONG", 50) / 2)), 400 - 50, 50, RED)
    end_drawing()
close_window()
