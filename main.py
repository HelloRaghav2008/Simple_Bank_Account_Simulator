import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

ACCOUNT_FILE = 'account_data.json'
STYLE_THEME = 'clam'


class BankAccount:
    def __init__(self, account_number, owner_name, password, balance=0.0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.password = password
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True, f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}"
        else:
            return False, "Invalid deposit amount. Must be positive."

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Invalid withdrawal amount. Must be positive."
        if amount > self.balance:
            return False, f"Insufficient funds. Current balance: ${self.balance:.2f}"
        else:
            self.balance -= amount
            return True, f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}"

    def check_password(self, entered_password):
        return self.password == entered_password

    def to_dict(self):
        return {
            'account_number': self.account_number,
            'owner_name': self.owner_name,
            'balance': self.balance,
            'password': self.password
        }

    @staticmethod
    def from_dict(data):
        return BankAccount(
            data['account_number'],
            data['owner_name'],
            data['password'],
            data['balance']
        )



def load_accounts():
    if not os.path.exists(ACCOUNT_FILE):
        return {}
    try:
        with open(ACCOUNT_FILE, 'r') as f:
            data = json.load(f)
            accounts_dict = {}
            for account_num, account_data in data.items():
                accounts_dict[account_num] = BankAccount.from_dict(account_data)
            return accounts_dict
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading account data: {e}. Starting fresh.")
        return {}


def save_accounts(accounts_dict):
    try:
        data_to_save = {}
        for account_num, account_obj in accounts_dict.items():
            data_to_save[account_num] = account_obj.to_dict()
        with open(ACCOUNT_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except IOError as e:
        print(f"Error saving account data: {e}")



class BankApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Simple Bank App")
        self.geometry("400x450")

        self.style = ttk.Style(self)
        self.style.theme_use(STYLE_THEME)

        self.all_accounts = load_accounts()
        self.current_account = None

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.frames = {}
        for F in (WelcomeFrame, LoginFrame, CreateAccountFrame, MainMenuFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # Place all frames in the same grid cell; only the one on top is visible
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeFrame")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def save_data(self):
        """Helper method to save all account data"""
        save_accounts(self.all_accounts)

    def logout(self):
        """Logs out the current user and returns to welcome screen"""
        self.current_account = None
        self.show_frame("WelcomeFrame")


class WelcomeFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Welcome to the Bank", font=("Arial", 20))
        label.pack(pady=40)

        btn_login = ttk.Button(self, text="Log In", command=lambda: controller.show_frame("LoginFrame"), width=20)
        btn_login.pack(pady=10)

        btn_create = ttk.Button(self, text="Create New Account",
                                command=lambda: controller.show_frame("CreateAccountFrame"), width=20)
        btn_create.pack(pady=10)

        btn_exit = ttk.Button(self, text="Exit", command=self.controller.destroy, width=20)
        btn_exit.pack(pady=10)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Log In", font=("Arial", 18)).pack(pady=20)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Account Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.acc_entry = ttk.Entry(form_frame, width=30)
        self.acc_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pass_entry = ttk.Entry(form_frame, show="*", width=30)
        self.pass_entry.grid(row=1, column=1, padx=5, pady=5)

        self.message_label = ttk.Label(self, text="", foreground="red")
        self.message_label.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Log In", command=self.handle_login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=5)

    def go_back(self):
        """Clears fields and goes back to welcome"""
        self.acc_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        self.message_label.config(text="")
        self.controller.show_frame("WelcomeFrame")

    def handle_login(self):
        acc_num = self.acc_entry.get()
        password = self.pass_entry.get()

        if acc_num not in self.controller.all_accounts:
            self.message_label.config(text="Account not found.")
            return

        account = self.controller.all_accounts[acc_num]

        if account.check_password(password):
            self.controller.current_account = account
            self.message_label.config(text="")
            self.acc_entry.delete(0, 'end')
            self.pass_entry.delete(0, 'end')
            self.controller.show_frame("MainMenuFrame")
        else:
            self.message_label.config(text="Incorrect password.")


class CreateAccountFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Create New Account", font=("Arial", 18)).pack(pady=20)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Account Number:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.acc_entry = ttk.Entry(form_frame, width=30)
        self.acc_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pass_entry = ttk.Entry(form_frame, show="*", width=30)
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Confirm Password:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.confirm_pass_entry = ttk.Entry(form_frame, show="*", width=30)
        self.confirm_pass_entry.grid(row=3, column=1, padx=5, pady=5)

        self.message_label = ttk.Label(self, text="", foreground="red")
        self.message_label.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Create", command=self.handle_create).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=self.go_back).pack(side="left", padx=5)

    def go_back(self):
        self.name_entry.delete(0, 'end')
        self.acc_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        self.confirm_pass_entry.delete(0, 'end')
        self.message_label.config(text="")
        self.controller.show_frame("WelcomeFrame")

    def handle_create(self):
        name = self.name_entry.get()
        acc_num = self.acc_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if not name or not acc_num or not password:
            self.message_label.config(text="All fields are required.")
            return

        if acc_num in self.controller.all_accounts:
            self.message_label.config(text="Account number already taken.")
            return

        if password != confirm_password:
            self.message_label.config(text="Passwords do not match.")
            return

        new_account = BankAccount(acc_num, name, password)
        self.controller.all_accounts[acc_num] = new_account
        self.controller.save_data()

        messagebox.showinfo("Success", f"Account for {name} created successfully!")
        self.go_back()


class MainMenuFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.welcome_label = ttk.Label(self, text="Welcome, [User]", font=("Arial", 16))
        self.welcome_label.pack(pady=(20, 5))

        self.balance_label = ttk.Label(self, text="Current Balance: $[Balance]", font=("Arial", 14))
        self.balance_label.pack(pady=(5, 20))


        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=20, pady=10)


        trans_frame = ttk.Frame(self)
        trans_frame.pack(pady=10)

        ttk.Label(trans_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(trans_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(trans_frame, text="Deposit", command=self.handle_deposit).grid(row=1, column=0, pady=10)
        ttk.Button(trans_frame, text="Withdraw", command=self.handle_withdraw).grid(row=1, column=1, pady=10)

        self.message_label = ttk.Label(self, text="", font=("Arial", 10))
        self.message_label.pack(pady=10)

        ttk.Button(self, text="Log Out", command=self.controller.logout).pack(pady=20)

    def on_show(self):
        if self.controller.current_account:
            self.update_labels()
        else:
            self.controller.logout()

    def update_labels(self):
        acc = self.controller.current_account
        self.welcome_label.config(text=f"Welcome, {acc.owner_name}!")
        self.balance_label.config(text=f"Current Balance: ${acc.balance:.2f}")

    def handle_deposit(self):
        try:
            amount = float(self.amount_entry.get())
            success, message = self.controller.current_account.deposit(amount)
            if success:
                self.controller.save_data()
                self.update_labels()
                self.message_label.config(text=message, foreground="green")
            else:
                self.message_label.config(text=message, foreground="red")
        except ValueError:
            self.message_label.config(text="Please enter a valid number.", foreground="red")

        self.amount_entry.delete(0, 'end')

    def handle_withdraw(self):
        try:
            amount = float(self.amount_entry.get())
            success, message = self.controller.current_account.withdraw(amount)
            if success:
                self.controller.save_data()
                self.update_labels()
                self.message_label.config(text=message, foreground="green")
            else:
                self.message_label.config(text=message, foreground="red")
        except ValueError:
            self.message_label.config(text="Please enter a valid number.", foreground="red")

        self.amount_entry.delete(0, 'end')


if __name__ == "__main__":
    app = BankApp()
    app.mainloop()