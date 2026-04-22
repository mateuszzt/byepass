import customtkinter as ctk
import threading
import time

from hashing import *
from attacks import *
from utils import *
from analysis import *
from reports import *
from database import save_password, save_attack, get_passwords

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Password Security Dashboard 🔐")
        self.geometry("1200x750")

        self.stop_flag = False

        # ===== SIDEBAR =====
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="🔐 Security Lab", font=("Arial", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Hash Password", command=self.hash_password).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Compare Algorithms", command=self.compare_hashes).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Brute Force", command=self.run_brute_thread).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="STOP", fg_color="red", command=self.stop_brute).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="History", command=self.show_history).pack(pady=10)

        # ===== MAIN =====
        self.main = ctk.CTkFrame(self)
        self.main.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self.password_entry = ctk.CTkEntry(self.main, width=400, placeholder_text="Enter password...")
        self.password_entry.pack(pady=10)

        # ===== STATS =====
        self.stats_frame = ctk.CTkFrame(self.main)
        self.stats_frame.pack(pady=10, fill="x")

        self.speed_label = ctk.CTkLabel(self.stats_frame, text="Speed: 0/s")
        self.speed_label.pack(side="left", padx=10)

        self.eta_label = ctk.CTkLabel(self.stats_frame, text="ETA: -")
        self.eta_label.pack(side="left", padx=10)

        self.progress_label = ctk.CTkLabel(self.stats_frame, text="0%")
        self.progress_label.pack(side="left", padx=10)

        # ===== PROGRESS =====
        self.progress = ctk.CTkProgressBar(self.main, width=500)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.attempt_label = ctk.CTkLabel(self.main, text="Trying: -")
        self.attempt_label.pack()

        self.status_label = ctk.CTkLabel(self.main, text="Status: Idle")
        self.status_label.pack()

        # ===== OUTPUT =====
        self.output = ctk.CTkTextbox(self.main, width=850, height=350)
        self.output.pack(pady=20)

        # ===== STATE =====
        self.current_hash = None
        self.current_salt = None
        self.password_plain = None

    # ===== UTILS =====
    def log(self, text):
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def set_status(self, text):
        self.status_label.configure(text=f"Status: {text}")

    def stop_brute(self):
        self.stop_flag = True
        self.set_status("Stopping...")

    # ===== HASH =====
    def hash_password(self):
        password = self.password_entry.get()
        self.password_plain = password
        self.current_salt = generate_salt()

        self.sha256 = hash_sha256(password, self.current_salt)
        self.sha1 = hash_sha1(password, self.current_salt)
        self.bcrypt_hash = hash_bcrypt(password)

        self.current_hash = self.sha256

        self.log("=== HASHES ===")
        self.log(f"SHA-256: {self.sha256}")
        self.log(f"SHA-1: {self.sha1}")
        self.log(f"bcrypt: {self.bcrypt_hash}")

        save_password(password, self.sha256, self.sha1, self.bcrypt_hash.decode(), self.current_salt)

    # ===== COMPARE =====
    def compare_hashes(self):
        if not self.password_plain:
            self.log("Hash password first!")
            return

        results = {}

        start = time.time()
        hash_sha1(self.password_plain, self.current_salt)
        results["SHA-1"] = time.time() - start

        start = time.time()
        hash_sha256(self.password_plain, self.current_salt)
        results["SHA-256"] = time.time() - start

        start = time.time()
        hash_bcrypt(self.password_plain)
        results["bcrypt"] = time.time() - start

        self.log("=== COMPARISON ===")
        for k, v in results.items():
            self.log(f"{k}: {v:.6f}s")

        plot_times(results)

    # ===== BRUTE FORCE =====
    def run_brute_thread(self):
        self.stop_flag = False
        threading.Thread(target=self.run_brute).start()

    def run_brute(self):
        if not self.current_hash:
            self.log("Hash first!")
            return

        self.set_status("Running brute force...")
        self.progress.set(0)

        start = time.time()
        checked = 0
        charset = get_charset()
        total = sum(len(charset) ** i for i in range(1, 5))

        for length in range(1, 5):
            for attempt in __import__("itertools").product(charset, repeat=length):
                if self.stop_flag:
                    self.set_status("Stopped")
                    return

                attempt = ''.join(attempt)
                checked += 1

                # CHECK
                if hash_sha256(attempt, self.current_salt) == self.current_hash:
                    t = time.time() - start
                    self.log(f"FOUND: {attempt}")
                    self.log(f"Time: {t:.2f}s")
                    save_attack("Brute Force", attempt, t)
                    self.set_status("Done")
                    return

                # ===== LIVE STATS =====
                elapsed = time.time() - start
                speed = checked / elapsed if elapsed > 0 else 0
                remaining = total - checked
                eta = remaining / speed if speed > 0 else 0

                percent = checked / total

                # UPDATE UI
                self.progress.set(percent)
                self.progress_label.configure(text=f"{percent*100:.2f}%")
                self.attempt_label.configure(text=f"Trying: {attempt[:10]}")
                self.speed_label.configure(text=f"Speed: {int(speed)} /s")

                if eta > 0:
                    self.eta_label.configure(text=f"ETA: {int(eta)}s")

                dots = "." * (checked % 4)
                self.set_status(f"Brute forcing{dots}")

        self.set_status("Finished")

    # ===== HISTORY =====
    def show_history(self):
        data = get_passwords()
        self.log("=== HISTORY ===")

        for row in data[:10]:
            self.log(f"ID {row[0]} | SHA256: {row[2][:12]}...")