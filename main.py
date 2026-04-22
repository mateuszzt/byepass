from gui import App
from database import init_db

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()