from enum import Enum, auto
from pyray import *
import os
import json
import math
import random
import user_interface
RESOLUTION_X = 1450
RESOLUTION_Y = 800
MODE_SETTINGS = {
    "DIGIT_PROCESSING_SETTINGS": {
        "Span": 3, # Minimum: 4 | Maximum: 20
        "Generations": 3,
        "Interval": 1.0,
    },
    "FLASH_ANZAN_SETTINGS": {
        "Span": 2,
        "Generations": 3,
        "Interval": 0.5
    },
    "MOT_FLASH_ANZAN_SETTINGS": {
        "Span": 1,
        "Generations": 4,
        "Trackers": 2,
        "Distractors": 5,
        "Interval": 2.0,
        "Speed": 6.0,
    },
    "ANAGRAMING_SETTINGS": {
        "Span": 9,
        "LookTime": 1.25,
    },
}
GAME_MODE_ORDER = ["Digit Processing", "Flash Anzan", "Flash Anzan ULTRA", "Anagraming"]
class GameState(Enum):
    LOBBY = auto()
    PLAYING = auto()
    RESULTS = auto()
    SETTINGS = auto()
game_state = GameState.LOBBY
game_mode = GAME_MODE_ORDER[0]
lobby_page = 0

interval_clock = 0.0
results_clock = 0.0
def center_text_offset(text: str, font_size: int):
    return (RESOLUTION_X / 2) - (measure_text(text, font_size) / 2)
dialogue_objects = {}
didnt_start_lobby = True
def lobby_selection():
    global game_state
    global dialogue_objects
    global didnt_start_lobby
    current_position = get_mouse_position()
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        if check_collision_point_rec(current_position, Rectangle(20.0, 50.0, measure_text("Settings", 25), 25)): # Settings Click
            game_state = GameState.SETTINGS
            didnt_start_lobby = True
            dialogue_objects["Title"].toggle()
        elif check_collision_point_rec(current_position, Rectangle(int(center_text_offset("Play", 50)), 600, measure_text("Play", 50), 50)): # Play Click
            game_state = GameState.PLAYING
            didnt_start_lobby = True
            dialogue_objects["Title"].toggle()
def gamemode_selection():
    global game_mode
    global lobby_page
    current_position = get_mouse_position()
    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
        difference = min(len(GAME_MODE_ORDER), (lobby_page + 1) * 5) - (lobby_page * 5)
        for i in range(difference):
            if check_collision_point_rec(current_position, Rectangle(int(center_text_offset(GAME_MODE_ORDER[(lobby_page * 5) + i], 25)), int(250 + (i * 50)), measure_text(GAME_MODE_ORDER[(lobby_page * 5) + i], 25), 25)):
                game_mode = GAME_MODE_ORDER[(lobby_page * 5) + i]
    relative_index = (GAME_MODE_ORDER.index(game_mode) % 5)
    draw_rectangle_lines(int(center_text_offset(game_mode, 25) - 10), int(250 + (relative_index * 50) - 10), measure_text(game_mode, 25) + 20, 45, RED)
if os.path.getsize("settings_data.json") == 0:
    with open("settings_data.json", "w") as settings_file:
        settings_file.write(json.dumps(MODE_SETTINGS, indent=4))
with open("settings_data.json", "r") as file:
    settings_data = json.load(file)
init_window(RESOLUTION_X, RESOLUTION_Y, "QuantSavant")
set_target_fps(get_monitor_refresh_rate(get_current_monitor()))
didnt_start_settings = True
dialogue_objects["Title"] = user_interface.Dialogue(1.0, "QuantSavant", 50, [RED, ORANGE, YELLOW], Vector2(center_text_offset("QuantSavant", 50), 125))
dialogue_objects["Global"] = user_interface.Dialogue(1.0, "Global", 50, [BLUE, PURPLE], Vector2(center_text_offset("Global", 50) - (RESOLUTION_X / 4), 125))
dialogue_objects["Mode"] = user_interface.Dialogue(1.0, "Mode", 50, [BLUE, PURPLE], Vector2(center_text_offset("Mode", 50) + (RESOLUTION_X / 4), 125))

def get_randomized_digits(include_first: bool):
    random_digits = list(range(10))
    random.shuffle(random_digits)
    start_index = 0
    if not include_first:
        start_index = 1
    return random_digits[start_index:]
### Digit Processing Helpers
### ------------------------------ ###
digit_processing_number = ""
digit_processing_generations = 0
digit_processing_list = []
digit_processing_noise = []
digit_processing_combined = []
digit_processing_evaluation_index = 0
def reset_digit_processing():
    global digit_processing_number
    global digit_processing_generations
    global digit_processing_list
    global digit_processing_noise
    global digit_processing_combined
    global digit_processing_evaluation_index

    digit_processing_number = ""
    digit_processing_generations = 0
    digit_processing_list = []
    digit_processing_noise = []
    digit_processing_combined = []
    digit_processing_evaluation_index = 0
### ------------------------------ ###
###
### Flash Anzan Helpers
### ------------------------------ ###
flash_anzan_number = ""
flash_anzan_input = ""
flash_anzan_generations = 0
flash_anzan_list = []
def reset_flash_anzan():
    global flash_anzan_number
    global flash_anzan_input
    global flash_anzan_generations
    global flash_anzan_list

    flash_anzan_number = ""
    flash_anzan_input = ""
    flash_anzan_generations = 0
    flash_anzan_list = []
### ------------------------------ ###
###
### Flash Anzan ULTRA Helpers
### ------------------------------ ###
mot_flash_anzan_number_list = []
mot_flash_anzan_input_number = 0
mot_flash_anzan_input = ""
mot_flash_anzan_x_filter = []
mot_flash_anzan_y_filter = []
mot_flash_anzan_grid_size = measure_text("0" * settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"], 25)
mot_flash_anzan_directions = []
mot_flash_anzan_generations = 0
mot_flash_anzan_init_clock = 0.0
def reset_flash_anzan_ultra():
    global mot_flash_anzan_number_list
    global mot_flash_anzan_input_number
    global mot_flash_anzan_input
    global mot_flash_anzan_x_filter
    global mot_flash_anzan_y_filter
    global mot_flash_anzan_directions
    global mot_flash_anzan_generations
    global mot_flash_anzan_init_clock

    mot_flash_anzan_number_list = []
    mot_flash_anzan_input_number = 0
    mot_flash_anzan_input = ""
    mot_flash_anzan_x_filter = []
    mot_flash_anzan_y_filter = []
    mot_flash_anzan_directions = []
    mot_flash_anzan_generations = 0
    mot_flash_anzan_init_clock = 0.0
### ------------------------------ ###
###
###
### Anagraming Helpers
### ------------------------------ ###
anagraming_number = ""
shuffled_anagram = ""
is_generating_anagram = False
anagram_clock = 0.0
def reset_anagraming():
    global anagraming_number
    global shuffled_anagram
    global is_generating_anagram
    global anagram_clock

    anagraming_number = ""
    shuffled_anagram = ""
    is_generating_anagram = False
    anagram_clock = 0.0
### ------------------------------ ###
###
settings_buttons = {}
def toggle_settings_buttons():
    match game_mode:
        case "Digit Processing":
            settings_buttons["DIGIT_PROCESSING" + "Span"].toggle()
            settings_buttons["DIGIT_PROCESSING" + "Generations"].toggle()
            settings_buttons["DIGIT_PROCESSING" + "Interval"].toggle()
        case "Flash Anzan":
            settings_buttons["FLASH_ANZAN" + "Span"].toggle()
            settings_buttons["FLASH_ANZAN" + "Generations"].toggle()
            settings_buttons["FLASH_ANZAN" + "Interval"].toggle()
        case "Flash Anzan ULTRA":
            settings_buttons["MOT_FLASH_ANZAN" + "Span"].toggle()
            settings_buttons["MOT_FLASH_ANZAN" + "Generations"].toggle()
            settings_buttons["MOT_FLASH_ANZAN" + "Interval"].toggle()
            settings_buttons["MOT_FLASH_ANZAN" + "Trackers"].toggle()
            settings_buttons["MOT_FLASH_ANZAN" + "Distractors"].toggle()
            settings_buttons["MOT_FLASH_ANZAN" + "Speed"].toggle()
        case "Anagraming":
            settings_buttons["ANAGRAMING" + "Span"].toggle()
            settings_buttons["ANAGRAMING" + "LookTime"].toggle()
        
is_evaluate_time = False
in_evaluation = False
is_correct = False
settings_buttons["DIGIT_PROCESSING" + "Span"] = user_interface.InputButton("Span:", 25, Rectangle(3 * RESOLUTION_X / 4, 250.0, measure_text("00000", 25), 25.0))
settings_buttons["DIGIT_PROCESSING" + "Span"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Span"])
settings_buttons["DIGIT_PROCESSING" + "Generations"] = user_interface.InputButton("Generations:", 25, Rectangle(3 * RESOLUTION_X / 4, 300.0, measure_text("00000", 25), 25.0))
settings_buttons["DIGIT_PROCESSING" + "Generations"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"])
settings_buttons["DIGIT_PROCESSING" + "Interval"] = user_interface.InputButton("Interval:", 25, Rectangle(3 * RESOLUTION_X / 4, 350.0, measure_text("00000", 25), 25.0))
settings_buttons["DIGIT_PROCESSING" + "Interval"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Interval"])

settings_buttons["FLASH_ANZAN" + "Span"] = user_interface.InputButton("Span:", 25, Rectangle(3 * RESOLUTION_X / 4, 250.0, measure_text("00000", 25), 25.0))
settings_buttons["FLASH_ANZAN" + "Span"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Span"])
settings_buttons["FLASH_ANZAN" + "Generations"] = user_interface.InputButton("Generations:", 25, Rectangle(3 * RESOLUTION_X / 4, 300.0, measure_text("00000", 25), 25.0))
settings_buttons["FLASH_ANZAN" + "Generations"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Generations"])
settings_buttons["FLASH_ANZAN" + "Interval"] = user_interface.InputButton("Interval:", 25, Rectangle(3 * RESOLUTION_X / 4, 350.0, measure_text("00000", 25), 25.0))
settings_buttons["FLASH_ANZAN" + "Interval"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Interval"])

settings_buttons["MOT_FLASH_ANZAN" + "Span"] = user_interface.InputButton("Span:", 25, Rectangle(3 * RESOLUTION_X / 4, 250.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Span"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"])
settings_buttons["MOT_FLASH_ANZAN" + "Generations"] = user_interface.InputButton("Generations:", 25, Rectangle(3 * RESOLUTION_X / 4, 300.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Generations"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"])
settings_buttons["MOT_FLASH_ANZAN" + "Interval"] = user_interface.InputButton("Interval:", 25, Rectangle(3 * RESOLUTION_X / 4, 350.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Interval"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"])
settings_buttons["MOT_FLASH_ANZAN" + "Trackers"] = user_interface.InputButton("Trackers:", 25, Rectangle(3 * RESOLUTION_X / 4, 400.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Trackers"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"])
settings_buttons["MOT_FLASH_ANZAN" + "Distractors"] = user_interface.InputButton("Distractors:", 25, Rectangle(3 * RESOLUTION_X / 4, 450.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Distractors"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"])
settings_buttons["MOT_FLASH_ANZAN" + "Speed"] = user_interface.InputButton("Speed:", 25, Rectangle(3 * RESOLUTION_X / 4, 500.0, measure_text("00000", 25), 25.0))
settings_buttons["MOT_FLASH_ANZAN" + "Speed"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Speed"])

settings_buttons["ANAGRAMING" + "Span"] = user_interface.InputButton("Span:", 25, Rectangle(3 * RESOLUTION_X / 4, 250.0, measure_text("00000", 25), 25.0))
settings_buttons["ANAGRAMING" + "Span"].text = str(settings_data["ANAGRAMING_SETTINGS"]["Span"])
settings_buttons["ANAGRAMING" + "LookTime"] = user_interface.InputButton("LookTime:", 25, Rectangle(3 * RESOLUTION_X / 4, 300.0, measure_text("00000", 25), 25.0))
settings_buttons["ANAGRAMING" + "LookTime"].text = str(settings_data["ANAGRAMING_SETTINGS"]["LookTime"])

wallpaper = load_image("lobby_symbols.png")
game_mode_wallpaper = load_image("game_symbols.png")
texture = load_texture_from_image(wallpaper)
game_mode_texture = load_texture_from_image(game_mode_wallpaper)
unload_image(wallpaper)
unload_image(game_mode_wallpaper)
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    if get_time() > 2.0:
        match game_state:
            case GameState.LOBBY:
                draw_texture(texture, 0, 0, GRAY)
                if didnt_start_lobby:
                    didnt_start_lobby = False
                    dialogue_objects["Title"].toggle()
                game_order_splice = GAME_MODE_ORDER[(lobby_page * 5):(min(len(GAME_MODE_ORDER), (lobby_page + 1) * 5))]
                for i, mode in enumerate(game_order_splice):
                    draw_text(mode, int(center_text_offset(mode, 25)), int(250 + (i * 50)), 25, WHITE)
                draw_text("Settings", 20, 50, 25, WHITE)
                draw_text("Play", int(center_text_offset("Play", 50)), 600, 50, WHITE)
                lobby_selection()
                gamemode_selection()
            case GameState.PLAYING:
                draw_texture(game_mode_texture, 0, 0, GRAY)
                match game_mode:
                    case "Digit Processing":
                        if is_evaluate_time:
                            if in_evaluation:
                                if digit_processing_evaluation_index == len(digit_processing_combined) - 1:
                                    is_correct = True
                                    game_state = GameState.RESULTS
                                    is_evaluate_time = False
                                    in_evaluation = False
                                    reset_digit_processing()
                                else:
                                    current_check = digit_processing_combined[digit_processing_evaluation_index]
                                    draw_text(current_check, int(center_text_offset(current_check, 50)), 400 - 50, 50, WHITE)
                                    draw_text("NO", int(center_text_offset("NO", 50)) - 100, 550, 50, WHITE)
                                    draw_text("YES", int(center_text_offset("YES", 50)) + 100, 550, 50, WHITE)
                                    current_position = get_mouse_position()
                                    if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                                        if check_collision_point_rec(current_position, Rectangle(center_text_offset("NO", 50) - 100, 550.0, measure_text("NO", 50), 50)):
                                            if current_check in digit_processing_list:
                                                is_correct = False
                                                game_state = GameState.RESULTS
                                                is_evaluate_time = False
                                                in_evaluation = False
                                                reset_digit_processing()
                                            else:
                                                digit_processing_evaluation_index += 1
                                        elif check_collision_point_rec(current_position, Rectangle(center_text_offset("YES", 50) + 100, 550.0, measure_text("YES", 50), 50)):
                                            if not current_check in digit_processing_list:
                                                is_correct = False
                                                game_state = GameState.RESULTS
                                                is_evaluate_time = False
                                                in_evaluation = False
                                                reset_digit_processing()
                                            else:
                                                digit_processing_evaluation_index += 1           
                            else:
                                in_evaluation = True
                                current_index = 0
                                for i in range(4 * settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"]):
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
                            if time_elapsed > settings_data["DIGIT_PROCESSING_SETTINGS"]["Interval"]:
                                interval_clock = get_time()
                                digit_processing_number = ""
                                digit_processing_generations += 1
                                if digit_processing_generations == settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"] + 1:
                                    is_evaluate_time = True
                                    digit_processing_generations = 0
                                else:
                                    remaining_digits = list(range(10))
                                    for i in range(settings_data["DIGIT_PROCESSING_SETTINGS"]["Span"]):
                                        if i == 0:
                                            digit_processing_number += str(random.randint(1, 9))
                                        else:
                                            if i % 9 == 0:
                                                remaining_digits = list(range(10))
                                            chosen_one = random.choice(remaining_digits)
                                            remaining_digits.remove(chosen_one)
                                            digit_processing_number += str(chosen_one)
                                    digit_processing_list.append(digit_processing_number)
                            draw_text(digit_processing_number, int(center_text_offset(digit_processing_number, 50)), 400 - 50, 50, WHITE)
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            reset_digit_processing()
                    case "Flash Anzan":
                        if is_evaluate_time:
                            draw_text("Enter Sum:", int(center_text_offset("Enter Sum:", 50)), 400 - 50, 50, WHITE)
                            draw_rectangle(int((RESOLUTION_X / 2) + (measure_text("0000000000", 50) / 2)), 400 - 50, measure_text("0000000000", 50), 50, WHITE)
                            pressed_key = get_key_pressed()
                            if pressed_key >= 48 and pressed_key <= 57:
                                flash_anzan_input += chr(pressed_key)
                            if is_key_pressed(KeyboardKey.KEY_BACKSPACE):
                                flash_anzan_input = flash_anzan_input[:-1]
                            elif is_key_pressed(KeyboardKey.KEY_ENTER):
                                is_correct = str(sum(flash_anzan_list)) == flash_anzan_input
                                game_state = GameState.RESULTS
                                is_evaluate_time = False
                                reset_flash_anzan()
                            to_write = flash_anzan_input
                            if int(get_time()) % 2 == 0:
                                to_write += "_"
                            draw_text(to_write, int(725 + (measure_text("0000000000", 50) / 2)), 400 - 50, 50, BLACK)
                        else:
                            time_elapsed = get_time() - interval_clock
                            if time_elapsed > settings_data["FLASH_ANZAN_SETTINGS"]["Interval"]:
                                interval_clock = get_time()
                                flash_anzan_number = ""
                                flash_anzan_generations += 1
                                if flash_anzan_generations == settings_data["FLASH_ANZAN_SETTINGS"]["Generations"] + 1:
                                    is_evaluate_time = True
                                    flash_anzan_generations = 0
                                else:
                                    remaining_digits = list(range(10))
                                    for i in range(settings_data["FLASH_ANZAN_SETTINGS"]["Span"]):
                                        if i == 0:
                                            flash_anzan_number += str(random.randint(1, 9))
                                        else:
                                            if i % 9 == 0:
                                                remaining_digits = list(range(10))
                                            chosen_one = random.choice(remaining_digits)
                                            remaining_digits.remove(chosen_one)
                                            flash_anzan_number += str(chosen_one)
                                    flash_anzan_list.append(int(flash_anzan_number))
                            draw_text(flash_anzan_number, int(center_text_offset(flash_anzan_number, 50)), 400 - 50, 50, WHITE)
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            is_evaluate_time = False
                            reset_flash_anzan()
                    case "Flash Anzan ULTRA":
                        if is_evaluate_time:
                            directions_data = mot_flash_anzan_directions[mot_flash_anzan_input_number]
                            draw_rectangle(int(directions_data["Position"].x), int(directions_data["Position"].y), int(measure_text(str(sum(mot_flash_anzan_number_list[mot_flash_anzan_input_number])), 25)), 25, WHITE)
                            pressed_key = get_key_pressed()
                            if pressed_key >= 48 and pressed_key <= 57:
                                mot_flash_anzan_input += chr(pressed_key)
                            if is_key_pressed(KeyboardKey.KEY_BACKSPACE):
                                mot_flash_anzan_input = mot_flash_anzan_input[:-1]
                            elif is_key_pressed(KeyboardKey.KEY_ENTER):
                                is_correct = str(sum(mot_flash_anzan_number_list[mot_flash_anzan_input_number])) == mot_flash_anzan_input
                                if not is_correct or mot_flash_anzan_input_number == settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] - 1:
                                    game_state = GameState.RESULTS
                                    is_evaluate_time = False
                                    reset_flash_anzan_ultra()
                                else:
                                    mot_flash_anzan_input_number += 1
                                    mot_flash_anzan_input = ""
                            to_write = mot_flash_anzan_input
                            if int(get_time()) % 2 == 0:
                                to_write += "_"
                            draw_text(to_write, int(directions_data["Position"].x), int(directions_data["Position"].y), 25, BLACK)
                        else:
                            time_elapsed = get_time() - interval_clock
                            if mot_flash_anzan_init_clock == 0.0:
                                mot_flash_anzan_init_clock = get_time()
                            time_elapsed_init = get_time() - mot_flash_anzan_init_clock
                            if time_elapsed > settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"]:
                                interval_clock = get_time()
                                mot_flash_anzan_generations += 1
                                if mot_flash_anzan_generations == settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"] + 1:
                                    is_evaluate_time = True
                                    mot_flash_anzan_generations = 0
                                    mot_flash_anzan_init_clock = 0.0
                                else:
                                    for i in range(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] + settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"]):
                                        mot_flash_anzan_number = ""
                                        remaining_digits = list(range(10))
                                        for j in range(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"]):
                                            if j == 0:
                                                mot_flash_anzan_number += str(random.randint(1, 9))
                                            else:
                                                if j % 9 == 0:
                                                    remaining_digits = list(range(10))
                                                chosen_one = random.choice(remaining_digits)
                                                remaining_digits.remove(chosen_one)
                                                mot_flash_anzan_number += str(chosen_one)
                                            pass
                                        if mot_flash_anzan_generations == 1:
                                            mot_flash_anzan_number_list.append([])
                                            x_cell = random.choice(list(set(range(int(RESOLUTION_X / mot_flash_anzan_grid_size))[1:(int(RESOLUTION_X / mot_flash_anzan_grid_size))]) - set(mot_flash_anzan_x_filter)))
                                            y_cell = random.choice(list(set(range(int(RESOLUTION_Y / 50))[1:(int(RESOLUTION_Y / 50))]) - set(mot_flash_anzan_y_filter)))
                                            mot_flash_anzan_x_filter.append(x_cell)
                                            mot_flash_anzan_y_filter.append(y_cell)
                                            random_theta = random.random() * (2 * math.pi)
                                            directions_data = {
                                                "Position": Vector2((x_cell * mot_flash_anzan_grid_size) + (mot_flash_anzan_grid_size / 2), (y_cell * 50) + 25),
                                                "Direction": vector2_scale(Vector2(math.cos(random_theta), math.sin(random_theta)), settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Speed"]),
                                            }
                                            mot_flash_anzan_directions.append(directions_data)
                                        mot_flash_anzan_number_list[i].append(int(mot_flash_anzan_number))
                            if mot_flash_anzan_generations > 0:
                                changed_filter = []
                                for i in range(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] + settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"]):
                                    if i in changed_filter:
                                        continue
                                    a = mot_flash_anzan_directions[i]["Position"]
                                    for j in range(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] + settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"]):
                                        if i == j:
                                            continue
                                        if j in changed_filter:
                                            continue
                                        b = mot_flash_anzan_directions[j]["Position"]
                                        if check_collision_recs(Rectangle(a.x, a.y, mot_flash_anzan_grid_size, 25), Rectangle(b.x, b.y, mot_flash_anzan_grid_size, 25)):
                                            mot_flash_anzan_directions[i]["Direction"], mot_flash_anzan_directions[j]["Direction"] = mot_flash_anzan_directions[j]["Direction"], mot_flash_anzan_directions[i]["Direction"]
                                            changed_filter.append(i)
                                            changed_filter.append(j)
                                            break
                                    c = Vector2(a.x + (mot_flash_anzan_grid_size), a.y + 25)
                                    if i not in changed_filter:
                                        if not check_collision_point_rec(a, Rectangle(0, 0, RESOLUTION_X, RESOLUTION_Y)):
                                            if a.x < 0:
                                                mot_flash_anzan_directions[i]["Direction"] = Vector2(-mot_flash_anzan_directions[i]["Direction"].x, mot_flash_anzan_directions[i]["Direction"].y) 
                                            elif a.y < 0:
                                                mot_flash_anzan_directions[i]["Direction"] = Vector2(mot_flash_anzan_directions[i]["Direction"].x, -mot_flash_anzan_directions[i]["Direction"].y)
                                        elif not check_collision_point_rec(c, Rectangle(0, 0, RESOLUTION_X, RESOLUTION_Y)):
                                            if c.x > RESOLUTION_X:
                                                mot_flash_anzan_directions[i]["Direction"] = Vector2(-mot_flash_anzan_directions[i]["Direction"].x, mot_flash_anzan_directions[i]["Direction"].y)
                                            elif c.y > RESOLUTION_Y:
                                                mot_flash_anzan_directions[i]["Direction"] = Vector2(mot_flash_anzan_directions[i]["Direction"].x, -mot_flash_anzan_directions[i]["Direction"].y)
                                for i in range(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] + settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"]):
                                    mot_flash_anzan_directions[i]["Position"] = vector2_add(mot_flash_anzan_directions[i]["Position"], mot_flash_anzan_directions[i]["Direction"])
                                    if i < settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"]:
                                        draw_text(str(mot_flash_anzan_number_list[i][-1]), int(mot_flash_anzan_directions[i]["Position"].x), int(mot_flash_anzan_directions[i]["Position"].y), 25, WHITE)
                                    elif time_elapsed_init > max(((settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"] * settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"]) / 2), settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"] + 2.0):
                                        draw_text(str(mot_flash_anzan_number_list[i][-1]), int(mot_flash_anzan_directions[i]["Position"].x), int(mot_flash_anzan_directions[i]["Position"].y), 25, WHITE)
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            is_evaluate_time = False
                            reset_flash_anzan_ultra()
                    case "Anagraming":
                        if not is_generating_anagram:
                            is_generating_anagram = True
                            remaining_digits = list(range(10))
                            for i in range(settings_data["ANAGRAMING_SETTINGS"]["Span"]):
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
                            if time_elapsed < settings_data["ANAGRAMING_SETTINGS"]["LookTime"]:
                                draw_text(anagraming_number, int(center_text_offset(anagraming_number, 50)), 400 - 50, 50, WHITE)
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
                                draw_text(shuffled_anagram, int(center_text_offset(shuffled_anagram, 50)), 400 - 50, 50, WHITE)
                                draw_text("NO", int(center_text_offset("NO", 50)) - 100, 550, 50, WHITE)
                                draw_text("YES", int(center_text_offset("YES", 50)) + 100, 550, 50, WHITE)
                                current_position = get_mouse_position()
                                if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                                    original_anagram = list(anagraming_number)
                                    new_anagram = list(shuffled_anagram)
                                    original_anagram.sort()
                                    new_anagram.sort()
                                    if check_collision_point_rec(current_position, Rectangle(center_text_offset("NO", 50) - 100, 550.0, measure_text("NO", 50), 50)):
                                        is_correct = original_anagram != new_anagram
                                        game_state = GameState.RESULTS
                                        in_evaluation = False   
                                        reset_anagraming()
                                    elif check_collision_point_rec(current_position, Rectangle(center_text_offset("YES", 50) + 100, 550.0, measure_text("YES", 50), 50)):
                                        is_correct = original_anagram == new_anagram
                                        game_state = GameState.RESULTS
                                        in_evaluation = False
                                        reset_anagraming()
                        if is_key_pressed(KeyboardKey.KEY_V):
                            game_state = GameState.LOBBY
                            in_evaluation = False   
                            reset_anagraming()         
            case GameState.RESULTS:
                if results_clock == 0.0:
                    results_clock = get_time()
                if get_time() - results_clock > 1.0:
                    game_state = GameState.LOBBY
                    results_clock = 0.0
                if is_correct:
                    draw_text("CORRECT", int(center_text_offset("CORRECT", 50)), 400 - 50, 50, GREEN)
                else:
                    draw_text("WRONG", int(center_text_offset("WRONG", 50)), 400 - 50, 50, RED)
            case GameState.SETTINGS:
                draw_line(int(RESOLUTION_X / 2), 0, int(RESOLUTION_X / 2), RESOLUTION_Y, RED)
                if didnt_start_settings:
                    didnt_start_settings = False
                    dialogue_objects["Global"].toggle()
                    dialogue_objects["Mode"].toggle()
                    toggle_settings_buttons()
                if is_key_pressed(KeyboardKey.KEY_V):
                    game_state = GameState.LOBBY
                    didnt_start_settings = True
                    dialogue_objects["Global"].toggle()
                    dialogue_objects["Mode"].toggle()
                    toggle_settings_buttons()
                    match game_mode:
                        case "Digit Processing":
                            settings_data["DIGIT_PROCESSING_SETTINGS"]["Span"] = int(settings_buttons["DIGIT_PROCESSING" + "Span"].text) or settings_data["DIGIT_PROCESSING_SETTINGS"]["Span"]
                            settings_buttons["DIGIT_PROCESSING" + "Span"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Span"])
                            settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"] = int(settings_buttons["DIGIT_PROCESSING" + "Generations"].text) or settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"]
                            settings_buttons["DIGIT_PROCESSING" + "Generations"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Generations"])
                            settings_data["DIGIT_PROCESSING_SETTINGS"]["Interval"] = float(settings_buttons["DIGIT_PROCESSING" + "Interval"].text) or settings_data["DIGIT_PROCESSING_SETTINGS"]["Interval"]
                            settings_buttons["DIGIT_PROCESSING" + "Interval"].text = str(settings_data["DIGIT_PROCESSING_SETTINGS"]["Interval"])
                        case "Flash Anzan":
                            settings_data["FLASH_ANZAN_SETTINGS"]["Span"] = int(settings_buttons["FLASH_ANZAN" + "Span"].text) or settings_data["FLASH_ANZAN_SETTINGS"]["Span"]
                            settings_buttons["FLASH_ANZAN" + "Span"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Span"])
                            settings_data["FLASH_ANZAN_SETTINGS"]["Generations"] = int(settings_buttons["FLASH_ANZAN" + "Generations"].text) or settings_data["FLASH_ANZAN_SETTINGS"]["Generations"]
                            settings_buttons["FLASH_ANZAN" + "Generations"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Generations"])
                            settings_data["FLASH_ANZAN_SETTINGS"]["Interval"] = float(settings_buttons["FLASH_ANZAN" + "Interval"].text) or settings_data["FLASH_ANZAN_SETTINGS"]["Interval"]
                            settings_buttons["FLASH_ANZAN" + "Interval"].text = str(settings_data["FLASH_ANZAN_SETTINGS"]["Interval"])
                        case "Flash Anzan ULTRA":
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"] = int(settings_buttons["MOT_FLASH_ANZAN" + "Span"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Span"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Span"])
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"] = int(settings_buttons["MOT_FLASH_ANZAN" + "Generations"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Generations"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Generations"])
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"] = int(settings_buttons["MOT_FLASH_ANZAN" + "Trackers"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Trackers"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Trackers"])
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"] = int(settings_buttons["MOT_FLASH_ANZAN" + "Distractors"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Distractors"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Distractors"])
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"] = float(settings_buttons["MOT_FLASH_ANZAN" + "Interval"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Interval"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Interval"])        
                            settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Speed"] = float(settings_buttons["MOT_FLASH_ANZAN" + "Speed"].text) or settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Speed"]
                            settings_buttons["MOT_FLASH_ANZAN" + "Speed"].text = str(settings_data["MOT_FLASH_ANZAN_SETTINGS"]["Speed"])    
                        case "Anagraming":
                            settings_data["ANAGRAMING_SETTINGS"]["Span"] = int(settings_buttons["ANAGRAMING" + "Span"].text) or settings_data["ANAGRAMING_SETTINGS"]["Span"]
                            settings_buttons["ANAGRAMING" + "Span"].text = str(settings_data["ANAGRAMING_SETTINGS"]["Span"])
                            settings_data["ANAGRAMING_SETTINGS"]["LookTime"] = float(settings_buttons["ANAGRAMING" + "LookTime"].text) or settings_data["ANAGRAMING_SETTINGS"]["LookTime"]
                            settings_buttons["ANAGRAMING" + "LookTime"].text = str(settings_data["ANAGRAMING_SETTINGS"]["LookTime"])
                    with open("settings_data.json", "w") as file:
                        json.dump(settings_data, file)
    for dialogue_object in dialogue_objects.values():
        dialogue_object.update()
    for settings_object in settings_buttons.values():
        settings_object.update()
    end_drawing()
close_window()
