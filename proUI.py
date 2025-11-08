import base64
import io
import threading
import os
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import winsound

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        set_appearance_mode("light")
        self.geometry('800x600')
        self.title("Chat Client")

        self.username = "Yan"

        # Меню
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30,
                             fg_color="black", hover_color="darkgrey")
        self.btn.place(x=0, y=0)

        # Основне поле чату
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        # Поле введення та кнопки
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40,
                                     command=self.send_message, fg_color="black", hover_color="darkgrey")
        self.send_button.place(x=0, y=0)
        self.open_img_button = CTkButton(self, text='📂', width=50, height=40,
                                         command=self.open_image, fg_color="black", hover_color="darkgrey")
        self.open_img_button.place(x=0, y=0)

        self.adaptive_ui()

        # Демонстраційне повідомлення
        demo_img_path = r'C:\Users\User\Desktop\Python Zagalbna\Logitalk_official\Screenshot_1.png'
        if os.path.exists(demo_img_path):
            self.add_message("Демонстрація відображення зображення:",
                             CTkImage(Image.open(demo_img_path), size=(300, 300)))

        # Підключення до сервера
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    # --- Меню ---
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️', fg_color="black", hover_color="darkgrey")
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️', fg_color="black", hover_color="darkgrey")
            self.show_menu()
            # Меню редагування ніка
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name,
                                         fg_color="black", hover_color="darkgrey")
            self.save_button.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_button", None):
                self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    # --- Адаптивний UI ---
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.after(50, self.adaptive_ui)

    # --- Додавання повідомлень ---
    def add_message(self, message=None, img=None):
        if not message and not img:
            return
        message_frame = CTkFrame(self.chat_field, fg_color='grey')
        message_frame.pack(pady=5, anchor='w')
        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        # Час
        time_label = CTkLabel(message_frame, text=datetime.now().strftime("%H:%M"),
                               text_color="darkgrey", font=("Arial", 10))
        time_label.pack(anchor='e', padx=10)

        # Зображення або текст
        if img:
            CTkLabel(message_frame, image=img, text=message if message else None,
                     compound='top', wraplength=wrapleng_size,
                     text_color='black', justify='left').pack(padx=10, pady=5, anchor='w')
        elif message:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                     text_color='black', justify='left').pack(padx=10, pady=5, anchor='w')

    # --- Відправка повідомлення ---
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
                winsound.PlaySound("send.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass
        self.message_entry.delete(0, END)

    # --- Отримання повідомлень ---
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT" and len(parts) >= 3:
            author, message = parts[1], parts[2]
            self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE" and len(parts) >= 4:
            author, filename, b64_img = parts[1], parts[2], parts[3]
            try:
                img_data = base64.b64decode(b64_img)
                pil_img = Image.open(io.BytesIO(img_data))
                message_frame = CTkFrame(self.chat_field, fg_color='grey')
                message_frame.pack(pady=5, anchor='w')
                time_label = CTkLabel(message_frame, text=datetime.now().strftime("%H:%M"),
                                       text_color="darkgrey", font=("Arial", 10))
                time_label.pack(anchor='e', padx=10)

                if getattr(pil_img, "is_animated", False):
                    self.show_gif(pil_img, message_frame)
                else:
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    CTkLabel(message_frame, image=ctk_img,
                             text=f"{author} надіслав(ла) зображення: {filename}",
                             compound="top").pack(padx=10, pady=5, anchor='w')
            except Exception as e:
                self.add_message(f"Помилка відображення зображення: {e}")
        else:
            self.add_message(line)

    # --- Показ GIF ---
    def show_gif(self, pil_img, message_frame):
        frames = []
        try:
            while True:
                frames.append(pil_img.copy())
                pil_img.seek(len(frames))
        except EOFError:
            pass

        label = CTkLabel(message_frame)
        label.pack()

        def update(ind=0):
            frame = frames[ind]
            ctk_img = CTkImage(frame, size=(300, 300))
            label.configure(image=ctk_img)
            ind = (ind + 1) % len(frames)
            message_frame.after(100, update, ind)

        update()

    # --- Відправка зображення / GIF ---
    def open_image(self):
        file_name = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")])
        if not file_name:
            return
        try:
            pil_img = Image.open(file_name)
            short_name = os.path.basename(file_name)

            # Відправка на сервер
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())

            # Локальне відображення
            message_frame = CTkFrame(self.chat_field, fg_color='grey')
            message_frame.pack(pady=5, anchor='w')
            time_label = CTkLabel(message_frame, text=datetime.now().strftime("%H:%M"),
                                   text_color="darkgrey", font=("Arial", 10))
            time_label.pack(anchor='e', padx=10)

            if getattr(pil_img, "is_animated", False):
                self.show_gif(pil_img, message_frame)
            else:
                ctk_img = CTkImage(pil_img, size=(300, 300))
                CTkLabel(message_frame, image=ctk_img).pack(padx=10, pady=5, anchor='w')

        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
