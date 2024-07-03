import sqlite3
from tkinter import *
from tkinter import messagebox
from cryptography.fernet import Fernet
import os

# Database setup
def setup_database():
    """Create the database and the passwords table if it does not exist."""
    conn = sqlite3.connect('password_manager.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS passwords (
                 id INTEGER PRIMARY KEY,
                 account TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Generate a key for encryption
def generate_key():
    """Generate and save an encryption key to a file."""
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load the previously generated key
def load_key():
    """Load the encryption key from the file."""
    return open("key.key", "rb").read()

# Encrypt a message
def encrypt_message(message):
    """Encrypt a message using the loaded encryption key."""
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

# Decrypt a message
def decrypt_message(encrypted_message):
    """Decrypt an encrypted message using the loaded encryption key."""
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

# Save password to database
def save_password(account, password):
    """Encrypt and save an account password to the database."""
    encrypted_password = encrypt_message(password)
    conn = sqlite3.connect('password_manager.db')
    c = conn.cursor()
    c.execute("INSERT INTO passwords (account, password) VALUES (?, ?)",
              (account, encrypted_password.decode()))
    conn.commit()
    conn.close()

# Retrieve password from database
def retrieve_password(account):
    """Retrieve and decrypt a password from the database for the given account."""
    conn = sqlite3.connect('password_manager.db')
    c = conn.cursor()
    c.execute("SELECT password FROM passwords WHERE account = ?", (account,))
    result = c.fetchone()
    conn.close()
    if result:
        return decrypt_message(result[0])
    else:
        return None

# GUI setup
def add_password():
    """Add a new password to the database."""
    account = account_entry.get()
    password = password_entry.get()
    if account and password:
        save_password(account, password)
        messagebox.showinfo("Success", "Password saved successfully.")
        account_entry.delete(0, END)
        password_entry.delete(0, END)
    else:
        messagebox.showwarning("Input Error", "Please provide both account and password.")

def get_password():
    """Retrieve and display the password for a given account."""
    account = account_entry.get()
    if account:
        password = retrieve_password(account)
        if password:
            messagebox.showinfo("Password Retrieved", f"Password for {account}: {password}")
        else:
            messagebox.showerror("Error", "Account not found.")
        account_entry.delete(0, END)
    else:
        messagebox.showwarning("Input Error", "Please provide the account name.")

# Generate the encryption key if it does not exist
if not os.path.exists("key.key"):
    generate_key()

# Set up the database
setup_database()

# GUI
root = Tk()
root.title("Password Manager")

# Labels and Entries
account_label = Label(root, text="Account")
account_label.grid(row=0, column=0, padx=10, pady=10)
account_entry = Entry(root, width=30)
account_entry.grid(row=0, column=1, padx=10, pady=10)

password_label = Label(root, text="Password")
password_label.grid(row=1, column=0, padx=10, pady=10)
password_entry = Entry(root, width=30, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

# Buttons
add_button = Button(root, text="Add Password", command=add_password)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

get_button = Button(root, text="Retrieve Password", command=get_password)
get_button.grid(row=3, column=0, columnspan=2, pady=10)

# Run the GUI loop
root.mainloop()
