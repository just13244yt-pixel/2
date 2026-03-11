import curses
import subprocess
import os
import sys
import json

MENU_FILE = "menus.json"
menus = []

# -----------------------------
# Menü laden und speichern
# -----------------------------
def load_menus():
    global menus
    if os.path.exists(MENU_FILE):
        try:
            with open(MENU_FILE, "r") as f:
                menus = json.load(f)
        except:
            menus = []
    else:
        menus = []

def save_menus():
    with open(MENU_FILE, "w") as f:
        json.dump(menus, f, indent=4)

# -----------------------------
# Hauptbildschirm zeichnen
# -----------------------------
def draw_main(stdscr, selected):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    title = "JUST OS"
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(1, w//2 - len(title)//2, title)
    stdscr.attroff(curses.color_pair(1))

    for i, menu in enumerate(menus):
        x = w//2 - 10
        y = 4 + i
        if i == selected:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, menu["name"])
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, menu["name"])

    hint = "B = Menü hinzufügen | Ctrl+A = Befehl ausführen | ENTER = Start | ESC = Neustart | Q = Beenden"
    stdscr.addstr(h-2, w-len(hint)-2, hint)

    stdscr.refresh()

# -----------------------------
# Eingabefeld
# -----------------------------
def input_screen(stdscr, prompt):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 1, w//2 - len(prompt)//2, prompt)
    curses.echo()
    raw = stdscr.getstr(h//2 + 1, w//2 - 20, 60)
    value = raw.decode() if raw else ""
    curses.noecho()
    return value.strip()

# -----------------------------
# Neustart-Funktion
# -----------------------------
def restart_justos():
    curses.endwin()
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print("Neustart fehlgeschlagen:", e)
        input("Drücke ENTER zum Beenden...")
        sys.exit(1)

# -----------------------------
# Befehl ausführen
# -----------------------------
def run_command(cmd):
    curses.endwin()
    try:
        if cmd:
            subprocess.run(cmd, shell=True)
        else:
            print("Kein Befehl angegeben!")
    except Exception as e:
        print("Fehler beim Ausführen:", e)
    input("ENTER drücken um zurückzukehren...")

# -----------------------------
# Hauptschleife
# -----------------------------
def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    selected = 0

    while True:
        draw_main(stdscr, selected)
        key = stdscr.getch()

        if key == 27:  # ESC
            restart_justos()

        elif key == curses.KEY_UP and menus:
            selected = (selected - 1) % len(menus)

        elif key == curses.KEY_DOWN and menus:
            selected = (selected + 1) % len(menus)

        elif key in (ord('b'), ord('B')):
            # Menüeintrag hinzufügen
            name = input_screen(stdscr, "Name eingeben")
            cmd = input_screen(stdscr, "Befehl eingeben")
            if name and cmd:
                menus.append({"name": name, "cmd": cmd})
                save_menus()

        elif key == 1:  # Ctrl+A
            # Direkt Befehl ausführen
            cmd = input_screen(stdscr, "Befehl ausführen")
            run_command(cmd)

        elif key in (curses.KEY_ENTER, 10, 13):
            if menus and 0 <= selected < len(menus):
                cmd = menus[selected].get("cmd", "")
                if cmd:
                    run_command(cmd)
                else:
                    stdscr.addstr(0, 0, "Kein Befehl definiert!")
                    stdscr.getch()

        elif key in (ord('q'), ord('Q')):
            curses.endwin()
            sys.exit(0)

# -----------------------------
# Programmstart
# -----------------------------
if __name__ == "__main__":
    load_menus()
    curses.wrapper(main)