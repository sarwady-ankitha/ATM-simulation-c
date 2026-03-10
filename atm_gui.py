# atm_gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import sys
import os
from datetime import datetime

ATM_EXE = "atm.exe"
ACCOUNTS_FILE = "accounts"

def load_accounts():
    accounts = {}
    if not os.path.exists(ACCOUNTS_FILE):
        return accounts
    with open(ACCOUNTS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 4:
                continue
            acc_num, pin, balance, name = parts[0], parts[1], parts[2], ",".join(parts[3:]).strip()
            accounts[acc_num] = {"pin": pin, "balance": float(balance), "name": name}
    return accounts

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        for acc_num, info in accounts.items():
            f.write(f"{acc_num},{info['pin']},{info['balance']:.2f},{info['name']}\n")

def run_atm(account, pin, actions):
    try:
        proc = subprocess.Popen([ATM_EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        input_lines = [str(account), str(pin)]
        for action, amount in actions:
            input_lines.append(str(action))
            if action in ("1", "2"):
                input_lines.append(str(amount))
            if action != "4":
                input_lines.append("y")
        input_lines.append("n")
        input_str = "\n".join(input_lines) + "\n"
        out, err = proc.communicate(input=input_str, timeout=10)
        return out
    except Exception as e:
        return f"Error running ATM backend: {e}"

def custom_popup(title, message, bg="#222244", fg="#FFFFFF"):
    popup = tk.Toplevel()
    popup.title(title)
    popup.configure(bg=bg)
    popup.geometry("350x180")  # Smaller size
    popup.resizable(False, False)
    label = tk.Label(popup, text=message, bg=bg, fg=fg, font=("Arial", 12), wraplength=320, justify="left")
    label.pack(padx=15, pady=15, fill="both", expand=True)
    btn = tk.Button(popup, text="OK", command=popup.destroy, bg="#44AA44", fg="#FFFFFF", font=("Arial", 11, "bold"))
    btn.pack(pady=8)
    popup.grab_set()
    popup.focus_set()
    popup.transient()
    popup.wait_window()

class ATMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Methodist ATM")
        self.root.configure(bg="#1e1e2f")
        self.root.geometry("450x500")  # Make the ATM frontend window bigger
        self.account = None
        self.pin = None
        self.actions = []
        self.transactions = []
        self.accounts_data = load_accounts()
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="ATM Login", font=("Arial", 26, "bold"), bg="#1e1e2f", fg="#FFD700").pack(pady=28)
        tk.Label(self.root, text="Account Number:", bg="#1e1e2f", fg="#FFFFFF", font=("Arial", 18, "bold")).pack()
        self.account_entry = tk.Entry(self.root, font=("Arial", 18, "bold"), bg="#333355", fg="#FFD700", insertbackground="#FFD700")
        self.account_entry.pack(pady=8)
        tk.Label(self.root, text="PIN:", bg="#1e1e2f", fg="#FFFFFF", font=("Arial", 18, "bold")).pack()
        self.pin_entry = tk.Entry(self.root, show="*", font=("Arial", 18, "bold"), bg="#333355", fg="#FFD700", insertbackground="#FFD700")
        self.pin_entry.pack(pady=8)
        tk.Button(self.root, text="Login", command=self.login, bg="#44AA44", fg="#FFFFFF", font=("Arial", 18, "bold")).pack(pady=28)

    def login(self):
        self.accounts_data = load_accounts()
        account = self.account_entry.get().strip()
        pin = self.pin_entry.get().strip()
        acc = self.accounts_data.get(account)
        if not acc or acc["pin"] != pin:
            custom_popup("Error", "Account and PIN do not match our records.", bg="#AA2222")
            return
        self.account = account
        self.pin = pin
        self.actions = []
        self.transactions = []
        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        name = self.accounts_data.get(self.account, {}).get("name", "Unknown User")
        tk.Label(self.root, text=f"Welcome, {name}", font=("Arial", 18, "bold"), bg="#1e1e2f", fg="#00CED1").pack(pady=15)
        tk.Label(self.root, text=f"Account: {self.account}", bg="#1e1e2f", fg="#FFD700", font=("Arial", 12)).pack()
        btn_style = {"width": 20, "font": ("Arial", 14, "bold"), "bg": "#333355", "fg": "#FFD700", "activebackground": "#FFD700", "activeforeground": "#333355"}
        tk.Button(self.root, text="💸 Withdraw", command=self.withdraw, **btn_style).pack(pady=7)
        tk.Button(self.root, text="💰 Deposit", command=self.deposit, **btn_style).pack(pady=7)
        tk.Button(self.root, text="💳 Balance Check", command=self.balance_check, **btn_style).pack(pady=7)
        tk.Button(self.root, text="📄 Transaction History", command=self.transaction_history, **btn_style).pack(pady=7)
        tk.Button(self.root, text="🔄 Refresh", command=self.refresh_account, bg="#2288CC", fg="#FFFFFF", font=("Arial", 14, "bold"), activebackground="#44CCFF", activeforeground="#1e1e2f").pack(pady=7)
        tk.Button(self.root, text="🚪 Logout", command=self.logout, bg="#AA2222", fg="#FFFFFF", font=("Arial", 14, "bold"), activebackground="#FF6347", activeforeground="#FFFFFF").pack(pady=15)

    def refresh_account(self):
        self.accounts_data = load_accounts()
        custom_popup("Refreshed", "Account data reloaded from file.", bg="#2288CC", fg="#FFFFFF")
        self.create_main_menu()

    def withdraw(self):
        amount = simpledialog.askfloat("Withdraw", "Enter amount to withdraw (multiples of 10):")
        if amount is None:
            return
        if amount <= 0 or amount % 10 != 0:
            custom_popup("Error", "Amount must be a positive multiple of 10.", bg="#AA2222")
            return
        acc = self.accounts_data[self.account]
        if amount > acc["balance"]:
            custom_popup("Withdraw", f"Insufficient balance.\nYour balance is: ₹{acc['balance']:.2f}", bg="#AA2222")
            return
        confirm = messagebox.askyesno("Confirm", f"Withdraw ₹{amount:.2f}?")
        if not confirm:
            return
        acc["balance"] -= amount
        save_accounts(self.accounts_data)
        self.transactions.append((datetime.now(), f"Withdraw ₹{amount:.2f}", f"Current Balance: ₹{acc['balance']:.2f}"))
        custom_popup("Withdraw Receipt", f"Withdrawal successful.\nCurrent Balance: ₹{acc['balance']:.2f}", bg="#222244")

    def deposit(self):
        amount = simpledialog.askfloat("Deposit", "Enter amount to deposit (multiples of 10):")
        if amount is None:
            return
        if amount <= 0 or amount % 10 != 0:
            custom_popup("Error", "Amount must be a positive multiple of 10.", bg="#AA2222")
            return
        confirm = messagebox.askyesno("Confirm", f"Deposit ₹{amount:.2f}?")
        if not confirm:
            return
        acc = self.accounts_data[self.account]
        acc["balance"] += amount
        save_accounts(self.accounts_data)
        self.transactions.append((datetime.now(), f"Deposit ₹{amount:.2f}", f"Current Balance: ₹{acc['balance']:.2f}"))
        custom_popup("Deposit Receipt", f"Deposit successful.\nCurrent Balance: ₹{acc['balance']:.2f}", bg="#224422")

    def balance_check(self):
        acc = self.accounts_data[self.account]
        balance = f"Your current balance is: ₹{acc['balance']}"
        self.transactions.append((datetime.now(), "Balance Check", balance))
        custom_popup("Balance", balance, bg="#222244")

    def mini_statement(self):
        if not self.transactions:
            custom_popup("Transaction Record", "No transactions this session.", bg="#444488")
            return
        statement = ""
        for t in self.transactions[-5:]:
            dt, action, balance = t
            statement += f"{dt.strftime('%Y-%m-%d %H:%M:%S')}\n{action}\n{balance}\n\n"
        # Use a larger popup for transaction record
        popup = tk.Toplevel()
        popup.title("Transaction Record")
        popup.configure(bg="#333355")
        popup.geometry("300x450")  # Bigger size for transaction record
        popup.resizable(True, True)
        label = tk.Label(popup, text=statement.strip(), bg="#333355", fg="#FFD700", font=("Arial", 13), wraplength=470, justify="left")
        label.pack(padx=20, pady=20, fill="both", expand=True)
        btn = tk.Button(popup, text="OK", command=popup.destroy, bg="#44AA44", fg="#FFFFFF", font=("Arial", 12, "bold"))
        btn.pack(pady=10)
        popup.grab_set()
        popup.focus_set()
        popup.transient()
        popup.wait_window()

    def transaction_history(self):
        if not self.transactions:
            custom_popup("Transaction History", "No transactions this session.", bg="#444488")
            return
        statement = ""
        for t in self.transactions[-5:]:
            dt, action, balance = t
            statement += f"{dt.strftime('%Y-%m-%d %H:%M:%S')}\n{action}\n{balance}\n\n"
        # Use a larger popup for transaction history
        popup = tk.Toplevel()
        popup.title("Transaction History")
        popup.configure(bg="#333355")
        popup.geometry("350x400")  # Bigger size for transaction history
        popup.resizable(True, True)
        label = tk.Label(popup, text=statement.strip(), bg="#333355", fg="#FFD700", font=("Arial", 13), wraplength=470, justify="left")
        label.pack(padx=20, pady=20, fill="both", expand=True)
        btn = tk.Button(popup, text="OK", command=popup.destroy, bg="#44AA44", fg="#FFFFFF", font=("Arial", 12, "bold"))
        btn.pack(pady=10)
        popup.grab_set()
        popup.focus_set()
        popup.transient()
        popup.wait_window()

    def logout(self):
        self.account = None
        self.pin = None
        self.actions = []
        self.transactions = []
        self.create_login_screen()

    def extract_last_transaction(self, output):
        lines = output.strip().splitlines()
        for i in range(len(lines)-1, -1, -1):
            if "Current Balance" in lines[i] or "balance is" in lines[i]:
                return "\n".join(lines[i-1:i+1])
        return "\n".join(lines[-5:]) if len(lines) > 5 else output

    def extract_balance(self, output):
        lines = output.strip().splitlines()
        for line in lines:
            if "current balance" in line.lower():
                return line
        for line in reversed(lines):
            if "balance" in line.lower():
                return line
        return lines[-1] if lines else "Balance not found"

if __name__ == "__main__":
    if not os.path.exists(ATM_EXE):
        messagebox.showerror("Error", f"{ATM_EXE} not found. Please compile atm.c to atm.exe and place it here.")
        sys.exit(1)
    root = tk.Tk()
    app = ATMGUI(root)
    root.mainloop()
