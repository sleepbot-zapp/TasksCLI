import curses
import sqlite3
import os


def init_db():
    db_file = 'tasks.db'
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)  
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, status BOOLEAN)''')
        conn.commit()
    else:
        conn = sqlite3.connect(db_file)  
        c = conn.cursor()
    return conn, c


def fetch_tasks(c):
    c.execute("SELECT id, task_name, status FROM tasks")
    rows = c.fetchall()
    tasks = [{'id': row[0], 'task_name': row[1], 'status': row[2]} for row in rows]
    return tasks


def insert_task(c, task_name):
    c.execute("INSERT INTO tasks (task_name, status) VALUES (?, ?)", (task_name, False))
    c.connection.commit()


def update_task_status(c, task_id, status):
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    c.connection.commit()


def delete_task(c, task_id):
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    c.connection.commit()


def init_screen(stdscr):
    conn, c = init_db()
    tasks = fetch_tasks(c)
    curses.curs_set(0)  
    stdscr.clear()  
    stdscr.refresh()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  
    current_task = 0
    edit_mode = False
    task_editing = None
    new_task_mode = False  
    new_task_name = ""  
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        stdscr.addstr(0, 0, "Use arrow keys to navigate. Press 'Enter' to edit, 'Space' to toggle task completion, '/' to add a new task, and 'Delete' to delete.")
        if new_task_mode:
            stdscr.addstr(1, 0, "Enter new task: ")
            stdscr.addstr(1, len("Enter new task: "), new_task_name, curses.A_REVERSE)
        for idx, task in enumerate(tasks):
            task_status = "[•]" if task['status'] else "[ ]"
            if task['status']:  
                if current_task == idx:  
                    stdscr.addstr(idx + 2, 0, f"{task_status} {task['task_name']}", curses.color_pair(1))  
                else:
                    stdscr.addstr(idx + 2, 0, f"{task_status} {task['task_name']}", curses.color_pair(3))  
            else:  
                
                if current_task == idx:  
                    stdscr.addstr(idx + 2, 0, f"{task_status} {task['task_name']}", curses.color_pair(1))  
                else:
                    stdscr.addstr(idx + 2, 0, f"{task_status} {task['task_name']}", curses.color_pair(2))  
        key = stdscr.getch()
        if not new_task_mode:
            if key == curses.KEY_UP and current_task > 0:  
                current_task -= 1
            elif key == curses.KEY_DOWN and current_task < len(tasks) - 1:  
                current_task += 1
        if key == 10:  
            if not edit_mode:
                edit_mode = True
                task_editing = current_task
            else:
                edit_mode = False
                task_editing = None
        elif key == 32:  
            task_id = tasks[current_task]['id']  
            new_status = not tasks[current_task]['status']
            update_task_status(c, task_id, new_status)  
            tasks[current_task]['status'] = new_status  
        elif key == ord('q'):  
            break
        elif key == ord('/'):  
            new_task_mode = True  
            new_task_name = ""  
            curses.echo()  
        if key == 127 or key == curses.KEY_DC:  
            if len(tasks) > 0:
                task_id = tasks[current_task]['id']  
                delete_task(c, task_id)  
                tasks = fetch_tasks(c)  
                if current_task >= len(tasks):  
                    current_task = len(tasks) - 1
        if new_task_mode:
            if key == 27:  
                new_task_mode = False
            elif key == 10:  
                if new_task_name.strip() != "":  
                    
                    new_task_name = new_task_name.lstrip("/")  
                    insert_task(c, new_task_name)  
                    tasks = fetch_tasks(c)  
                new_task_mode = False  
                new_task_name = ""  
            elif key == 127 or key == curses.KEY_BACKSPACE:  
                new_task_name = new_task_name[:-1]  
            else:
                try:
                    new_task_name += chr(key)  
                except ValueError:
                    pass  

        stdscr.refresh()


def main():
    curses.wrapper(init_screen)

if __name__ == "__main__":
    main()
