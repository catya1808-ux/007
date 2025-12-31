import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import datetime
import json
import os
import pygame
from datetime import datetime, timedelta
from pathlib import Path

# Инициализация pygame для воспроизведения звуков
pygame.mixer.init()

class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Часы с будильником")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Загрузка иконок (можно заменить на свои)
        self.alarm_icon = "🔔"
        self.clock_icon = "⏰"
        self.music_icon = "🎵"
        self.save_icon = "💾"
        self.delete_icon = "🗑️"
        
        # Список активных будильников
        self.alarms = []
        self.alarm_id_counter = 1
        self.current_alarm_sound = None
        
        # Доступные мелодии
        self.sounds = {
            "Классический": "system_default",
            "Звонок": "beep",
            "Птицы": "birds",
            "Радио": "radio"
        }
        
        # Дни недели
        self.days_of_week = {
            "Пн": 0,
            "Вт": 1,
            "Ср": 2,
            "Чт": 3,
            "Пт": 4,
            "Сб": 5,
            "Вс": 6
        }
        
        # Загрузка сохраненных будильников
        self.load_alarms()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск потока для отслеживания времени
        self.running = True
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)
        self.update_thread.start()
        
        # Запуск потока для проверки будильников
        self.alarm_check_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.alarm_check_thread.start()
    
    def create_widgets(self):
        # Создание стилей
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 24, 'bold'),
                       background='#2c3e50',
                       foreground='#ecf0f1')
        
        style.configure('Time.TLabel',
                       font=('Digital-7', 48),
                       background='#2c3e50',
                       foreground='#2ecc71')
        
        style.configure('Alarm.TFrame',
                       background='#34495e',
                       relief='raised',
                       borderwidth=2)
        
        style.configure('AddButton.TButton',
                       font=('Arial', 12, 'bold'),
                       background='#3498db',
                       foreground='white')
        
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text=f"{self.clock_icon} Умные часы с будильником",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Текущее время
        self.time_label = ttk.Label(main_frame,
                                   text="00:00:00",
                                   style='Time.TLabel')
        self.time_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Дата
        self.date_label = ttk.Label(main_frame,
                                   text="1 января 2024",
                                   font=('Arial', 14),
                                   background='#2c3e50',
                                   foreground='#bdc3c7')
        self.date_label.grid(row=2, column=0, columnspan=2, pady=(0, 30))
        
        # Фрейм для добавления нового будильника
        add_frame = ttk.LabelFrame(main_frame, 
                                  text=f"{self.alarm_icon} Добавить новый будильник",
                                  padding="15",
                                  style='Alarm.TFrame')
        add_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Время будильника
        ttk.Label(add_frame, text="Время:", 
                 font=('Arial', 11),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=0, column=0, padx=5, pady=5)
        
        self.hour_var = tk.StringVar(value="08")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")
        
        hour_spin = ttk.Spinbox(add_frame, from_=0, to=23, width=3,
                               textvariable=self.hour_var, font=('Arial', 12))
        hour_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text=":", 
                 font=('Arial', 12),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=0, column=2)
        
        minute_spin = ttk.Spinbox(add_frame, from_=0, to=59, width=3,
                                 textvariable=self.minute_var, font=('Arial', 12))
        minute_spin.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text=":", 
                 font=('Arial', 12),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=0, column=4)
        
        second_spin = ttk.Spinbox(add_frame, from_=0, to=59, width=3,
                                 textvariable=self.second_var, font=('Arial', 12))
        second_spin.grid(row=0, column=5, padx=5)
        
        # Название будильника
        ttk.Label(add_frame, text="Название:", 
                 font=('Arial', 11),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=1, column=0, padx=5, pady=10)
        
        self.name_var = tk.StringVar(value="Будильник")
        name_entry = ttk.Entry(add_frame, textvariable=self.name_var,
                              width=20, font=('Arial', 11))
        name_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=10, sticky=tk.W)
        
        # Мелодия
        ttk.Label(add_frame, text="Мелодия:", 
                 font=('Arial', 11),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=2, column=0, padx=5, pady=5)
        
        self.sound_var = tk.StringVar(value="Классический")
        sound_combo = ttk.Combobox(add_frame, textvariable=self.sound_var,
                                  values=list(self.sounds.keys()),
                                  state="readonly", width=18, font=('Arial', 11))
        sound_combo.grid(row=2, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)
        
        # Дни повторения
        ttk.Label(add_frame, text="Повторять:", 
                 font=('Arial', 11),
                 background='#34495e',
                 foreground='#ecf0f1').grid(row=3, column=0, padx=5, pady=10)
        
        self.repeat_vars = {}
        repeat_frame = ttk.Frame(add_frame, style='Alarm.TFrame')
        repeat_frame.grid(row=3, column=1, columnspan=5, padx=5, pady=10, sticky=tk.W)
        
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.repeat_vars[day] = var
            cb = ttk.Checkbutton(repeat_frame, text=day, variable=var)
            cb.grid(row=0, column=i, padx=2)
        
        # Кнопка добавления будильника
        add_button = ttk.Button(add_frame, 
                               text=f"{self.alarm_icon} Добавить будильник",
                               command=self.add_alarm,
                               style='AddButton.TButton')
        add_button.grid(row=4, column=0, columnspan=6, pady=15)
        
        # Фрейм списка будильников
        list_frame = ttk.LabelFrame(main_frame, 
                                   text=f"{self.alarm_icon} Активные будильники",
                                   padding="15",
                                   style='Alarm.TFrame')
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Создание таблицы для будильников
        columns = ('id', 'time', 'name', 'sound', 'repeat', 'active')
        self.alarm_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Настройка колонок
        self.alarm_tree.heading('id', text='ID')
        self.alarm_tree.heading('time', text='Время')
        self.alarm_tree.heading('name', text='Название')
        self.alarm_tree.heading('sound', text='Мелодия')
        self.alarm_tree.heading('repeat', text='Повтор')
        self.alarm_tree.heading('active', text='Статус')
        
        self.alarm_tree.column('id', width=50, anchor=tk.CENTER)
        self.alarm_tree.column('time', width=100, anchor=tk.CENTER)
        self.alarm_tree.column('name', width=150, anchor=tk.W)
        self.alarm_tree.column('sound', width=100, anchor=tk.CENTER)
        self.alarm_tree.column('repeat', width=150, anchor=tk.CENTER)
        self.alarm_tree.column('active', width=80, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=scrollbar.set)
        
        self.alarm_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления
        button_frame = ttk.Frame(list_frame, style='Alarm.TFrame')
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text=f"🗑️ Удалить выбранный",
                  command=self.delete_selected_alarm).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text=f"✅ Вкл/Выкл",
                  command=self.toggle_selected_alarm).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text=f"{self.save_icon} Сохранить все",
                  command=self.save_alarms).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text=f"🗑️ Удалить все",
                  command=self.delete_all_alarms).pack(side=tk.LEFT, padx=5)
        
        # Панель статуса
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, 
                              textvariable=self.status_var,
                              relief=tk.SUNKEN,
                              anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Обновление отображения будильников
        self.update_alarm_list()
    
    def update_time(self):
        """Обновление текущего времени"""
        while self.running:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%d %B %Y (%A)")
            
            self.time_label.config(text=current_time)
            self.date_label.config(text=current_date)
            
            time.sleep(0.5)
    
    def add_alarm(self):
        """Добавление нового будильника"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())
            name = self.name_var.get()
            sound = self.sound_var.get()
            
            # Проверка времени
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                messagebox.showerror("Ошибка", "Некорректное время!")
                return
            
            # Получение выбранных дней повторения
            repeat_days = []
            for day, var in self.repeat_vars.items():
                if var.get():
                    repeat_days.append(day)
            
            # Создание объекта будильника
            alarm_time = datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)
            
            # Если время уже прошло сегодня и нет повторения, установить на завтра
            if alarm_time < datetime.now() and not repeat_days:
                alarm_time += timedelta(days=1)
            
            alarm = {
                'id': self.alarm_id_counter,
                'time': alarm_time.strftime("%H:%M:%S"),
                'name': name,
                'sound': sound,
                'repeat_days': repeat_days,
                'active': True,
                'next_ring': alarm_time,
                'original_time': alarm_time.time()
            }
            
            self.alarms.append(alarm)
            self.alarm_id_counter += 1
            
            self.update_alarm_list()
            self.status_var.set(f"Будильник '{name}' добавлен на {alarm_time.strftime('%H:%M:%S')}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
    
    def update_alarm_list(self):
        """Обновление списка будильников в таблице"""
        # Очистка таблицы
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)
        
        # Заполнение данными
        for alarm in self.alarms:
            repeat_text = ", ".join(alarm['repeat_days']) if alarm['repeat_days'] else "Однократно"
            status_text = "✅" if alarm['active'] else "❌"
            
            self.alarm_tree.insert('', tk.END, values=(
                alarm['id'],
                alarm['time'],
                alarm['name'],
                alarm['sound'],
                repeat_text,
                status_text
            ))
    
    def check_alarms(self):
        """Проверка срабатывания будильников"""
        while self.running:
            now = datetime.now()
            current_time = now.time()
            
            for alarm in self.alarms:
                if not alarm['active']:
                    continue
                
                # Проверка времени срабатывания
                alarm_time = alarm['next_ring'].time() if 'next_ring' in alarm else datetime.strptime(alarm['time'], "%H:%M:%S").time()
                
                # Сравнение времени с точностью до секунды
                if (current_time.hour == alarm_time.hour and
                    current_time.minute == alarm_time.minute and
                    current_time.second == alarm_time.second):
                    
                    # Запуск будильника в отдельном потоке
                    threading.Thread(target=self.trigger_alarm, args=(alarm,), daemon=True).start()
                    
                    # Обновление следующего срабатывания для повторяющихся будильников
                    if alarm['repeat_days']:
                        self.update_next_ring_time(alarm)
                    else:
                        alarm['active'] = False
            
            self.update_alarm_list()
            time.sleep(1)
    
    def update_next_ring_time(self, alarm):
        """Обновление времени следующего срабатывания для повторяющихся будильников"""
        if not alarm['repeat_days']:
            return
        
        now = datetime.now()
        current_weekday = now.weekday()
        
        # Поиск следующего дня срабатывания
        for i in range(1, 8):  # Проверяем следующие 7 дней
            next_day = (current_weekday + i) % 7
            day_name = list(self.days_of_week.keys())[list(self.days_of_week.values()).index(next_day)]
            
            if day_name in alarm['repeat_days']:
                next_date = now.date() + timedelta(days=i)
                next_time = datetime.combine(next_date, alarm['original_time'])
                alarm['next_ring'] = next_time
                break
    
    def trigger_alarm(self, alarm):
        """Срабатывание будильника"""
        # Создание окна оповещения
        alert_window = tk.Toplevel(self.root)
        alert_window.title(f"Будильник: {alarm['name']}")
        alert_window.geometry("400x300")
        alert_window.configure(bg='#e74c3c')
        alert_window.attributes('-topmost', True)
        
        # Заголовок
        title_label = tk.Label(alert_window,
                              text="🔥 БУДИЛЬНИК! 🔥",
                              font=('Arial', 24, 'bold'),
                              bg='#e74c3c',
                              fg='white')
        title_label.pack(pady=20)
        
        # Информация
        info_label = tk.Label(alert_window,
                            text=f"{alarm['name']}\n{alarm['time']}",
                            font=('Arial', 18),
                            bg='#e74c3c',
                            fg='white')
        info_label.pack(pady=10)
        
        # Кнопка отключения
        stop_button = tk.Button(alert_window,
                               text="ОТКЛЮЧИТЬ",
                               font=('Arial', 16, 'bold'),
                               bg='#2c3e50',
                               fg='white',
                               command=lambda: self.stop_alarm_sound(alert_window, alarm))
        stop_button.pack(pady=30)
        
        # Воспроизведение звука
        self.play_alarm_sound(alarm['sound'])
    
    def play_alarm_sound(self, sound_name):
        """Воспроизведение выбранного звука"""
        try:
            # Здесь можно добавить реальные звуковые файлы
            # Например: pygame.mixer.music.load(f"sounds/{sound_name}.mp3")
            # Пока используем системный звук
            
            # Имитация разных звуков
            if sound_name == "Классический":
                for _ in range(10):
                    print('\a', end='', flush=True)
                    time.sleep(0.5)
            elif sound_name == "Звонок":
                for freq in [1000, 1200, 1000, 1200]:
                    print('\a', end='', flush=True)
                    time.sleep(0.3)
            # Добавьте другие звуки по аналогии
            
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def stop_alarm_sound(self, window, alarm):
        """Остановка звука будильника и закрытие окна"""
        pygame.mixer.music.stop() if pygame.mixer.music.get_busy() else None
        window.destroy()
        
        # Если будильник не повторяется, отключаем его
        if not alarm['repeat_days']:
            alarm['active'] = False
            self.update_alarm_list()
    
    def delete_selected_alarm(self):
        """Удаление выбранного будильника"""
        selection = self.alarm_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите будильник для удаления!")
            return
        
        item = selection[0]
        values = self.alarm_tree.item(item)['values']
        alarm_id = values[0]
        
        # Удаление из списка
        self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
        self.update_alarm_list()
        self.status_var.set(f"Будильник ID {alarm_id} удален")
    
    def toggle_selected_alarm(self):
        """Включение/выключение выбранного будильника"""
        selection = self.alarm_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите будильник!")
            return
        
        item = selection[0]
        values = self.alarm_tree.item(item)['values']
        alarm_id = values[0]
        
        # Поиск и переключение статуса
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                alarm['active'] = not alarm['active']
                status = "включен" if alarm['active'] else "выключен"
                self.status_var.set(f"Будильник '{alarm['name']}' {status}")
                break
        
        self.update_alarm_list()
    
    def delete_all_alarms(self):
        """Удаление всех будильников"""
        if messagebox.askyesno("Подтверждение", "Удалить все будильники?"):
            self.alarms.clear()
            self.update_alarm_list()
            self.status_var.set("Все будильники удалены")
    
    def save_alarms(self):
        """Сохранение будильников в файл"""
        try:
            # Подготовка данных для сохранения
            save_data = []
            for alarm in self.alarms:
                save_alarm = alarm.copy()
                # Преобразование datetime в строку
                if 'next_ring' in save_alarm and isinstance(save_alarm['next_ring'], datetime):
                    save_alarm['next_ring'] = save_alarm['next_ring'].isoformat()
                if 'original_time' in save_alarm:
                    save_alarm['original_time'] = save_alarm['original_time'].isoformat()
                save_data.append(save_alarm)
            
            # Выбор файла для сохранения
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                self.status_var.set(f"Будильники сохранены в {filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def load_alarms(self):
        """Загрузка будильников из файла"""
        try:
            # Автозагрузка из стандартного файла
            default_file = "alarms_backup.json"
            if os.path.exists(default_file):
                with open(default_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Восстановление datetime объектов
                for alarm in loaded_data:
                    if 'next_ring' in alarm and alarm['next_ring']:
                        alarm['next_ring'] = datetime.fromisoformat(alarm['next_ring'])
                    if 'original_time' in alarm:
                        alarm['original_time'] = datetime.fromisoformat(alarm['original_time']).time()
                
                self.alarms = loaded_data
                if loaded_data:
                    self.alarm_id_counter = max(a['id'] for a in loaded_data) + 1
                
        except Exception as e:
            print(f"Не удалось загрузить будильники: {e}")
    
    def on_closing(self):
        """Действия при закрытии окна"""
        self.running = False
        # Автоматическое сохранение при закрытии
        try:
            with open("alarms_backup.json", 'w', encoding='utf-8') as f:
                save_data = []
                for alarm in self.alarms:
                    save_alarm = alarm.copy()
                    if 'next_ring' in save_alarm and isinstance(save_alarm['next_ring'], datetime):
                        save_alarm['next_ring'] = save_alarm['next_ring'].isoformat()
                    if 'original_time' in save_alarm:
                        save_alarm['original_time'] = save_alarm['original_time'].isoformat()
                    save_data.append(save_alarm)
                
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        self.root.destroy()

# Дополнительные функции для управления будильниками
def create_test_alarms():
    """Создание тестовых будильников"""
    app = type('App', (), {})()  # Создаем mock объект
    app.alarms = []
    
    # Пример будильника с повторением
    test_alarm = {
        'id': 1,
        'time': '08:00:00',
        'name': 'Подъем',
        'sound': 'Классический',
        'repeat_days': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
        'active': True,
        'next_ring': datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
        'original_time': datetime.strptime('08:00:00', '%H:%M:%S').time()
    }
    
    app.alarms.append(test_alarm)
    return app.alarms

# Запуск приложения
if __name__ == "__main__":
    try:
        # Установка шрифта (если есть)
        try:
            import tkinter.font as tkFont
            # Можно добавить загрузку специальных шрифтов
        except:
            pass
        
        root = tk.Tk()
        app = AlarmClockApp(root)
        
        # Обработка закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")