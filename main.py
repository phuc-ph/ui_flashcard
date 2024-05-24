import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style

from database.IE221_DoAn.Controllers.StackController import StackController
from database.IE221_DoAn.Controllers.CardController import CardController
from database.IE221_DoAn.main import init

# Kết nối tới database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nesko@032",
    database="flashcard"
)


class UIFlashcard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.init_app()
        self.init_frame_import_stack()
        self.init_frame_handle_stack()
        self.init_frame_learn_mode()

    def init_app(self):
        self.title('Flashcards App')
        self.geometry('500x400')

        # Thiết lập style cho giao diện
        self.style = Style(theme='superhero')
        self.style.configure('TLabel', font=('TkDefaultFont', 18))
        self.style.configure('TButton', font=('TkDefaultFont', 16))

        # Thiết lập các biến dành cho người dùng nhập dữ liệu
        self.stack_name_var = tk.StringVar()
        self.front_var = tk.StringVar()
        self.back_var = tk.StringVar()
        self.answer_var = tk.StringVar()

        # Tạo notebook để quản lý các frame
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Tạo frame import stack
        self.create_stack_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_stack_frame, text='Create Stack')

        # Tạo frame xử lý các nội dung về stack như create, select, delete
        self.select_stack_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.select_stack_frame, text="Select Stack")

        # Tạo frame learn mode
        self.flashcards_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flashcards_frame, text='Learn Mode')

        # Khởi tạo các biến để quản lý trạng thái flashcard
        self.card_index = 0
        self.current_cards = []
        self.score = 0

        # Lắng nghe sự kiện người dùng nhấn phím enter
        self.bind("<Return>", self.handle_flip_card)

    def init_frame_import_stack(self):
        ttk.Label(self.create_stack_frame, text='Stack Name:').pack(padx=5, pady=5)
        self.stack_name_combobox = ttk.Combobox(self.create_stack_frame, textvariable=self.stack_name_var, width=30,
                                                state='readonly')
        self.stack_name_combobox.pack(padx=5, pady=10)

        ttk.Label(self.create_stack_frame, text='Front:').pack(padx=5, pady=5)
        ttk.Entry(self.create_stack_frame, textvariable=self.front_var, width=30).pack(padx=5, pady=5)

        ttk.Label(self.create_stack_frame, text='Back:').pack(padx=5, pady=5)
        ttk.Entry(self.create_stack_frame, textvariable=self.back_var, width=30).pack(padx=5, pady=10)

        ttk.Button(self.create_stack_frame, text='Add Word', command=self.add_front).pack(padx=5, pady=10)

    def init_frame_handle_stack(self):
        self.stacks_combobox = ttk.Combobox(self.select_stack_frame, state='readonly')
        self.stacks_combobox.pack(padx=5, pady=40)

        button_frame = ttk.Frame(self.select_stack_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text='Create Stack', command=self.create_stack).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text='Select Stack', command=self.handle_select_stack).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text='Delete Stack', command=self.handle_delete_selected_stack).grid(row=0, column=2, padx=5)

        # Populate the combobox with available stacks
        self.populate_stacks_combobox()
        self.update_stack_name_combobox()

    def init_frame_learn_mode(self):
        self.front_label = ttk.Label(self.flashcards_frame, text='', wraplength=400, justify='center')
        self.front_label.pack(pady=0)

        self.back_label = ttk.Label(self.flashcards_frame, text='', wraplength=400, justify='center')
        self.back_label.pack(pady=0)

        self.result_frame = ttk.Frame(self.flashcards_frame, height=50, width=400)
        self.result_frame.pack(pady=0, fill='x')
        self.result_frame.pack_propagate(False)

        self.result_label = ttk.Label(self.result_frame, text='', wraplength=400, justify='center')
        self.result_label.pack()

        self.score_label = ttk.Label(self.flashcards_frame, text=f"Score: {self.score}", font=('TkDefaultFont', 16))
        self.score_label.place(relx=1.0, rely=0.0, anchor='ne')

        ttk.Entry(self.flashcards_frame, textvariable=self.answer_var, width=30).pack(pady=30)

        self.button_frame = ttk.Frame(self.flashcards_frame)
        self.button_frame.pack(pady=5)

        ttk.Button(self.button_frame, text='Prev Card', command=self.handle_button_prev).grid(row=0, column=0, padx=10)
        ttk.Button(self.button_frame, text='Answer', command=self.handle_button_answer).grid(row=0, column=1, padx=10)
        ttk.Button(self.button_frame, text='Next Card', command=self.handle_button_next).grid(row=0, column=2, padx=10)

    def create_stack(self):
        def save_stack():
            stack_name = entry_var.get()
            if stack_name:
                stack_name = stack_name.strip().lower()
                if stack_name not in [stack.name for stack in StackController.get_stacks()]:
                    StackController.add_stack(stack_name)
                    self.populate_stacks_combobox()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Stack name already exists!")

        def cancel():
            dialog.destroy()

        dialog = tk.Toplevel(self)
        dialog.title("Create Stack")
        dialog.geometry("300x150")

        entry_var = tk.StringVar()

        ttk.Label(dialog, text="Enter stack name:").pack(pady=10)
        ttk.Entry(dialog, textvariable=entry_var, width=30).pack(pady=5)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Ok", command=save_stack).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).grid(row=0, column=1, padx=5)

    def add_front(self):
        stack_name = self.stack_name_var.get()
        front = self.front_var.get()
        back = self.back_var.get()

        CardController.add_card(stack_name, front, back)
        self.front_var.set('')
        self.back_var.set('')

        self.populate_stacks_combobox()
        self.update_stack_name_combobox()

    def populate_stacks_combobox(self):
        stacks = StackController.get_stacks()
        stack_names = [stack.name for stack in stacks]
        self.stacks_combobox['values'] = tuple(stack_names)

    def update_stack_name_combobox(self):
        stacks = StackController.get_stacks()
        stack_names = [stack.name for stack in stacks]
        self.stack_name_combobox['values'] = tuple(stack_names)

    def handle_delete_selected_stack(self):
        stack_name = self.stacks_combobox.get()
        if stack_name:
            stack_name = stack_name.strip().lower()
            result = messagebox.askyesno(
                'Confirmation', f'Are you sure you want to delete the "{stack_name}" set?'
            )
            if result == tk.YES:
                stack_id = StackController.get_stack_id_by_name(stack_name)
                StackController.delete_stack(stack_id)
                self.populate_stacks_combobox()
                self.update_stack_name_combobox()
                self.clear_flashcard_display()

    def handle_select_stack(self):
        stack_name = self.stacks_combobox.get()
        if stack_name:
            stack_name = stack_name.strip().lower()
            cards = CardController.get_cards_by_stack_name(stack_name)
            if cards:
                self.display_flashcards(cards)
            else:
                self.front_label.config(text="No cards in this set")
                self.back_label.config(text='')
        else:
            self.current_cards = []
            self.card_index = 0
            self.clear_flashcard_display()

    def display_flashcards(self, cards):
        self.card_index = 0
        self.current_cards = cards
        if not cards:
            self.clear_flashcard_display()
        else:
            self.handle_show_card()

    def clear_flashcard_display(self):
        self.front_label.config(text='')
        self.back_label.config(text='')

    def handle_show_card(self):
        if self.current_cards:
            if 0 <= self.card_index < len(self.current_cards):
                card = self.current_cards[self.card_index]
                self.front_label.config(text=card.front)
                self.back_label.config(text='')
                self.result_label.config(text='')
            else:
                self.clear_flashcard_display()
        else:
            self.clear_flashcard_display()

    def handle_button_answer(self):
        if self.current_cards:
            card = self.current_cards[self.card_index]
            user_answer = self.answer_var.get().strip()
            correct_answer = card.back.strip()
            self.answer_var.set('')
            if user_answer.lower() == correct_answer.lower():
                self.score += 1
                self.update_score_label()
                self.result_label.config(text='Tuyệt vời, bạn đã trả lời đúng rồi!', foreground='green')
            else:
                self.result_label.config(
                    text=f'Hình như bạn đang không học bài? {correct_answer} mới là câu trả lời đúng!',
                    foreground='red')
            self.front_label.config(text=card.back)

    def handle_button_next(self):
        if self.current_cards:
            self.card_index = min(self.card_index + 1, len(self.current_cards) - 1)
            self.result_label.config(text='')
            self.answer_var.set('')
            self.handle_show_card()

    def handle_button_prev(self):
        if self.current_cards:
            self.card_index = max(self.card_index - 1, 0)
            self.result_label.config(text='')
            self.answer_var.set('')
            self.handle_show_card()

    def handle_flip_card(self, event=None):
        current_text = self.front_label.cget("text")
        if current_text:
            self.handle_button_answer()
        else:
            self.handle_show_card()

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score}")


if __name__ == '__main__':
    init()
    app = UIFlashcard()
    app.mainloop()
