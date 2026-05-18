import tkinter as tk
from gui import TarifApp


def main():
    root = tk.Tk()
    app = TarifApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
