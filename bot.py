import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Подключение к базе данных SQLite
conn = sqlite3.connect('todo_list.db')
cursor = conn.cursor()

# Создание таблицы задач, если она еще не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    description TEXT,
    status TEXT,
    date_added TEXT
)
''')
conn.commit()

# Функция для добавления задачи
def add_task():
    task_name = task_name_entry.get()
    description = description_entry.get()
    if task_name and description:
        date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                       INSERT INTO tasks (task_name, description, status, date_added)
                       VALUES (?, ?, 'pending', ?)
                       ''', (task_name, description, date_added))
        conn.commit()
        task_name_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        view_tasks()
    else:
        messagebox.showwarning("Input Error", "Please fill in both task name and description")

# Функция для отображения задач
def view_tasks():
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    
    # Очистка старых записей в списке
    for widget in tasks_frame.winfo_children():
        widget.destroy()

    # Отображение задач
    for task in tasks:
        task_id = task[0]
        task_name = task[1]
        status = task[3]
        description = task[2]

        # Панель для задачи
        task_frame = tk.Frame(tasks_frame)
        task_frame.pack(fill="x", pady=5)

        # Лейбл с названием задачи и статусом
        task_label = tk.Label(task_frame, text=f"ID: {task_id} - {task_name} - {status}", anchor="w")
        task_label.pack(side="left", padx=10)

        # Кнопка для отображения/скрытия описания
        toggle_button = tk.Button(task_frame, text="▼", command=lambda t_id=task_id: toggle_description(t_id))
        toggle_button.pack(side="left", padx=5)

        # Кнопка для удаления задачи
        delete_button = tk.Button(task_frame, text="Delete", command=lambda t_id=task_id: delete_task(t_id))
        delete_button.pack(side="right", padx=5)

        # Скрытое описание задачи (будет отображаться при нажатии на стрелочку)
        description_label = tk.Label(task_frame, text=f"Description: {description}", anchor="w", justify="left", wraplength=400, fg="gray")
        description_label.pack(side="bottom", fill="x", padx=10, pady=5)
        description_label.grid_forget()  # Скрыть описание по умолчанию

        # Сохраняем ссылку на описание, чтобы позже показать или скрыть
        task_frame.description_label = description_label
        task_frame.toggle_button = toggle_button

# Функция для отображения/скрытия описания задачи
def toggle_description(task_id):
    task_frame = find_task_frame(task_id)
    if task_frame:
        description_label = task_frame.description_label
        toggle_button = task_frame.toggle_button

        if description_label.winfo_ismapped():
            description_label.grid_forget()
            toggle_button.config(text="▼")
        else:
            description_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
            toggle_button.config(text="▲")

# Функция для нахождения панели задачи по ID
def find_task_frame(task_id):
    for widget in tasks_frame.winfo_children():
        if hasattr(widget, 'description_label') and widget.description_label.winfo_exists():
            if widget.description_label.cget("text").startswith(f"Description:"):
                if f"ID: {task_id}" in widget.winfo_children()[0].cget("text"):
                    return widget
    return None

# Функция для удаления задачи
def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    view_tasks()

# Основное окно
root = tk.Tk()
root.title("To-Do List")

# Поле ввода задачи
task_name_label = tk.Label(root, text="Task Name:")
task_name_label.pack()
task_name_entry = tk.Entry(root)task_name_entry.pack()

# Поле ввода описания задачи
description_label = tk.Label(root, text="Description:")
description_label.pack()
description_entry = tk.Entry(root)
description_entry.pack()

# Кнопка для добавления задачи
add_button = tk.Button(root, text="Add Task", command=add_task)
add_button.pack()

# Фрейм для отображения задач
tasks_frame = tk.Frame(root)
tasks_frame.pack()

# Загружаем задачи при старте
view_tasks()

root.mainloop()

# Закрываем соединение с базой данных
conn.close()