import curses
from textwrap import wrap
import random
import json
import threading
import time

icons = {
    "beer": [
        "┏┓",
        "┗┛"
    ],
    "saw": [
        "┌▄",
        "│█"
    ],
    "handcfs": [
        "O┐",
        "O┘"
    ],
    "cig": [
        "║│",
        "██"
    ],
    "glass": [
        " O",
        " │"
    ]
}

def log(string);
    with open("latest.log", "a", encoding="utf-8") as f:
        f.write(f"{string}\n")

class ReactiveDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = None

        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = ReactiveDict(value)
                self[key].callback = self.callback

    def set_callback(self, callback):
    
        self.callback = callback
        for value in self.values():
            if isinstance(value, ReactiveDict):
                value.set_callback(callback)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = ReactiveDict(value)
            value.callback = self.callback
        super().__setitem__(key, value)
        if self.callback:
            self.callback()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.callback:
            self.callback()

    def clear(self):
        super().clear()
        if self.callback:
            self.callback()

    def pop(self, *args):
        result = super().pop(*args)
        if self.callback:
            self.callback()
        return result

data = ReactiveDict({
    "text": [],
    "round": 0,
    "hp": -1,
    "answers": [],
    "inventory": {
        0: "",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
    },
    "cylinder": []
})

def clear_inv():
    data["inventory"].clear()

def draw_interface(stdscr):
    height, width = stdscr.getmaxyx()

    def gen_inv():
        inv = [[], []]
        lines = [["", ""], ["", ""], ["", ""], ["", ""]]

        for slot in range(8):
            if slot <= 1:
                if len(data["inventory"][slot]) > 0:
                    lines[0][0] += f"│  {icons[data["inventory"][slot]]}"
                    lines[0][1] += f"│  {icons[data["inventory"][slot]]}  "
                    if slot == 1:
                        lines[0][0] += "│"
                        lines[0][1] += "│"
                else:
                    lines[0][0] += "│      "
                    lines[0][1] += "│      "
                    if slot == 1:
                        lines[0][0] += "│"
                        lines[0][1] += "│"
            elif slot <= 3:
                if len(data["inventory"][slot]) > 0:
                    lines[1][0] += f"│  {icons[data["inventory"][slot]]}  "
                    lines[1][1] += f"│  {icons[data["inventory"][slot]]}  "
                    if slot == 3:
                        lines[1][0] += "│"
                        lines[1][1] += "│"
                else:
                    lines[1][0] += "│      "
                    lines[1][1] += "│      "
                    if slot == 3:
                        lines[1][0] += "│"
                        lines[1][1] += "│"
            elif slot <= 5:
                if len(data["inventory"][slot]) > 0:
                    lines[2][0] += f"│  {icons[data["inventory"][slot]]}  "
                    lines[2][1] += f"│  {icons[data["inventory"][slot]]}  "
                    if slot == 5:
                        lines[2][0] += "│"
                        lines[2][1] += "│"
                else:
                    lines[2][0] += "│      "
                    lines[2][1] += "│      "
                    if slot == 5:
                        lines[2][0] += "│"
                        lines[2][1] += "│"
            elif slot <= 7:
                if len(data["inventory"][slot]) > 0:
                    lines[3][0] += f"│  {icons[data["inventory"][slot]]}  "
                    lines[3][1] += f"│  {icons[data["inventory"][slot]]}  "
                    if slot == 7:
                        lines[3][0] += "│"
                        lines[3][1] += "│"
                else:
                    lines[3][0] += "│      "
                    lines[3][1] += "│      "
                    if slot == 7:
                        lines[3][0] += "│"
                        lines[3][1] += "│"

        inv[0].append("1──────┬──────2")
        inv[0].append(lines[0][0])
        inv[0].append(lines[0][1])
        inv[0].append("3──────┼──────4")
        inv[0].append(lines[1][0])
        inv[0].append(lines[1][1])
        inv[0].append("└──────┴──────┘ ")

        inv[1].append("5──────┬──────6")
        inv[1].append(lines[2][0])
        inv[1].append(lines[2][1])
        inv[1].append("7──────┼──────8")
        inv[1].append(lines[3][0])
        inv[1].append(lines[3][1])
        inv[1].append("└──────┴──────┘")

        return inv

    for column in range(width):
        try:
            if column != 0 or column != width - 1:
                stdscr.addstr(0, column, "—")
                stdscr.addstr(height - 1, column, "—")
                stdscr.addstr(height // 3 * 2, column, "—")
        except curses.error:
            pass

    for line in range(height):
        try:
            if line == 0:
                stdscr.addstr(line, 0, "┌")
                stdscr.addstr(line, width - 1, "┐")
            elif line == height - 1:
                stdscr.addstr(line, 0, "└")
                stdscr.addstr(line, width - 1, "┘")
            elif line == height // 3 * 2:
                stdscr.addstr(line, 0, "├")
                stdscr.addstr(line, width - 1, "┤")
            else:
                stdscr.addstr(line, 0, "│")
                stdscr.addstr(line, width - 1, "│")
        except curses.error:
            pass

    for i, text in enumerate(data["text"]):
        line, scheme = text
        try:
            stdscr.addstr(1+i, width//2-len(line)//2, line, scheme)
        except curses.error:
            pass

    for i, answer in enumerate(data["answers"]):
        try:
            stdscr.addstr(height//4*3+i*2, width//2-5, f" [{i + 1}] {answer}")
        except curses.error:
            pass


    if data["round"] > 0:
        for i, line in enumerate(gen_inv()[0]):
            stdscr.addstr(height//4*3+i, 5, line)

        for i, line in enumerate(gen_inv()[1]):
            stdscr.addstr(height//4*3+i, width-len(line)-5, line)

    #stdscr.addstr(height-5, width//50*50, "⚡" * data["hp"] + " " * (3 - data["hp"]))


def save_scoreboard(scoreboard, filename='scoreboard.json'):
    try:
        with open(filename, 'w') as file:
            json.dump(scoreboard, file, indent=4)
    except IOError as e:
        log(f"Error saving scoreboard: {e}")
    except TypeError:
        log("Invalid data format.")


def read_scoreboard(filename='scoreboard.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file).sort(key=lambda x: x["score"], reverse=True)
    except FileNotFoundError:
        try:
            with open(filename, 'w') as file:
                json.dump([], file)
            log(f"Created new scoreboard file: {filename}")
        except IOError as e:
            log(f"Error creating file {filename}: {e}. Returning empty scoreboard.")
    except json.JSONDecodeError:
        log(f"Error: Invalid JSON in {filename}. Returning empty scoreboard.")
        return []
    except IOError as e:
        log(f"Error reading file: {e}. Returning empty scoreboard.")
        return []

def main(stdscr):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    def refresh():
        stdscr.clear()
        draw_interface(stdscr)
        stdscr.refresh()

    def add_text(text):
        data["text"].append(text)
        refresh()

    def clear_text():
        data["text"].clear()
        refresh()

    data.set_callback(refresh)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    blue = curses.color_pair(2)
    gray = curses.color_pair(1) | curses.A_DIM
    red = curses.color_pair(3)
    green = curses.color_pair(4)
    white = curses.color_pair(1)
    yellow = curses.color_pair(5)
    gold = curses.color_pair(5) | curses.A_DIM

    bold = curses.A_BOLD
    italic = curses.A_ITALIC
    underline = curses.A_UNDERLINE

    endless = False

    def bullets_fall(window, stop_event):
        bullets = {
            "left": [],
            "right": []
        }

        for i in range(12):
            if i < 6:
                col = random.randint(3, width//3-2)
            else:
                col = random.randint(width//3*2+2, width-3)

            row = random.randint(2, height//3*2)
            color = random.choice([red, blue])
            if len(bullets["left"]) <= 5:
                bullets["left"].append((row, col, color))
            else:
                bullets["right"].append((row, col, color))

        while not stop_event.is_set():
            for _, bullets_list in bullets.items():
                for i, bullet in enumerate(bullets_list):
                    row, col, color = bullet
                    if stop_event.is_set():
                        break

                    if row <= height//3*2-2:
                        window.addstr(row, col, "█", color)
                        window.addstr(row + 1, col, "▀", gold)
                        window.refresh()

                        bullets_list[i] = (row + 1, col, color)
                    else:
                        if bullet in bullets["left"]:
                            new_col = random.randint(3, width // 3 - 2)
                        else:
                            new_col = random.randint(width // 3 * 2 + 2, width - 3)
                        bullets_list[i] = (random.randint(2, 7), new_col, random.choice([blue, red]))
            time.sleep(0.5)
            for _, bullets_list in bullets.items():
                for i, bullet in enumerate(bullets_list):
                    row, col, color = bullet

                    window.addstr(row-1, col, " ")
                    window.addstr(row, col, " ")
                    window.refresh()
    
    def main_menu():
        clear_text()
        add_text(("Buckshot Roulette", white | bold))
        add_text(("Python Edition", gray | italic))

        data["answers"] = ["START", "CREDITS", "EXIT"]

        stop_event = threading.Event()
        thread = threading.Thread(target=bullets_fall, args=(stdscr, stop_event))
        thread.start()

        valid_input = False
        while not valid_input:
                key = stdscr.getch()
                if key == ord("1"):
                    stop_event.set()
                    thread.join()
                    pass
                elif key == ord("2"):
                    valid_input = True
                    stop_event.set()
                    thread.join()
                    credits_menu()
                elif key == ord("3"):
                    stop_event.set()
                    thread.join()
                    quit()

    def credits_menu():
        clear_text()
        add_text(("CREDITS", bold | italic))
        add_text(("", white))
        add_text(("Python Edition by:", white))
        add_text(("Lemonnik", bold))
        add_text(("", white))
        add_text(("Original game by:", white))
        add_text(("Mike Klubnika", bold))

        data["answers"] = ["BACK"]

        valid_input = False
        while not valid_input:
            key = stdscr.getch()
            if key == ord("1"):
                valid_input = True
                main_menu()

    def restroom():
        clear_text()
        add_text(("RESTROOM", bold | italic))
        add_text(("", white))
        add_text(("You are in the restroom", white))
        add_text(("", white))
        if not endless:
            add_text(("There is a computer here", white))
            add_text(("It looks out of place...", white))
            add_text(("", white))
            add_text((""))

    main_menu()

curses.wrapper(main)
