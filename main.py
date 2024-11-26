import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.ttk import Treeview
from PIL import ImageTk, Image
from datetime import datetime
import json
import os

# Constants
BASE_VOLUME = 30
MAX_IMAGE_WIDTH = 250
MAX_IMAGE_HEIGHT = 200
HISTORY_FILE = "history.json"

class SpaceVapeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Vape")
        self.root.geometry("1500x800")
        self.root.configure(bg="lightgray")

        # Load history
        self.historique = []
        self.load_history()

        # Apply a theme
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.setup_ui()

    def setup_ui(self):
        # Notebook (Tabbed UI)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main Tab
        self.main_frame = ttk.Frame(self.notebook, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.main_frame, text="Calculator")

        # History Tab
        self.history_frame = ttk.Frame(self.notebook, padding=10)
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.history_frame, text="History")

        # Logo
        self.add_logo()

        # Inputs
        self.inputs = {}
        input_fields = [
            ("Prix 30ML arome (DT):", "30", "prix_arome"),
            ("Prix 1L base (DT):", "60", "prix_base"),
            ("Cout emballage:", "0.8", "PACKAGING_COST"),
            ("Quantité d'arome (ml):", "30", "arome"),
            ("Pourcentage d'arome (%):", "10", "P_arome"),
            ("Prix de vente de 30ml (DT):", "15", "prix_vente"),
        ]
        for label, default, key in input_fields:
            self.create_input(label, default, key)

        # Calculate Button
        style = ttk.Style()
        style.configure('Green.TButton', background='green', foreground='white')
        style.configure('Red.TButton', background='red', foreground='white')

        ttk.Button(self.main_frame, text="Calculate", style='Green.TButton', command=self.calculate).pack(pady=10, fill=tk.X)
        ttk.Button(self.history_frame, text="Delete History", style='Red.TButton', command=lambda: self.clear_history(HISTORY_FILE)).pack(pady=10, fill=tk.X)


        self.root.bind('<Return>', lambda _: self.calculate())

        # Results Table
        self.results_table = Treeview(self.main_frame, columns=("Label", "Value"), show="headings", height=8)
        self.results_table.heading("Label", text="Label")
        self.results_table.heading("Value", text="Value")
        self.results_table.pack(fill=tk.BOTH, pady=10)

        # History Table
        self.history_table = Treeview(self.history_frame, columns=("Timestamp", "Arome %", "Base Added", "Total Qty", "Bottles", "Cost", "Profits"), show="headings", height=15)
        self.history_table.heading("Timestamp", text="Timestamp", command=lambda: self.sort_history_table("timestamp"))
        self.history_table.heading("Arome %", text="Arome %", command=lambda: self.sort_history_table("arome_percentage"))
        self.history_table.heading("Base Added", text="Base Added", command=lambda: self.sort_history_table("base_added"))
        self.history_table.heading("Total Qty", text="Total Qty", command=lambda: self.sort_history_table("total_quantity"))
        self.history_table.heading("Bottles", text="Bottles", command=lambda: self.sort_history_table("bottles_count"))
        self.history_table.heading("Cost", text="Cost", command=lambda: self.sort_history_table("liquid_cost"))
        self.history_table.heading("Profits", text="Profits", command=lambda: self.sort_history_table("total_profits"))
        for col in self.history_table["columns"]:
            self.history_table.column(col, anchor="center")
        self.history_table.pack(fill=tk.BOTH, pady=10)

        # Total Profits Label
        self.total_profits_label = ttk.Label(self.history_frame, text="Total Profits: 0.00 DT", font=("Arial", 12, "bold"))
        self.total_profits_label.pack(pady=5, anchor="e")  # Align to the right

        # Populate History Table
        self.populate_history_table()

    def add_logo(self):
        logo_path = "assets/logo.png"
        try:
            logo_image = Image.open(logo_path)
            logo_image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.ANTIALIAS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            ttk.Label(self.main_frame, image=self.logo_photo).pack(pady=10)
        except FileNotFoundError:
            ttk.Label(self.main_frame, text="Logo not found!", foreground="red").pack(pady=10)

    def create_input(self, label_text, default_value, key):
        frame = ttk.Frame(self.main_frame, padding=5)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=label_text).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.insert(0, default_value)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.inputs[key] = entry

    def calculate(self):
        try:
            # Input values
            arome = float(self.inputs["arome"].get())
            P_arome = float(self.inputs["P_arome"].get())
            prix_vente = float(self.inputs["prix_vente"].get())
            prix_base = float(self.inputs["prix_base"].get()) / 1000
            PACKAGING_COST = float(self.inputs["PACKAGING_COST"].get())
            prix_arome = float(self.inputs["prix_arome"].get()) / BASE_VOLUME

            # Calculations
            base_ajoute = (arome * (100 - P_arome)) / P_arome
            total_liquid = base_ajoute + arome
            nbr_flacon = total_liquid / BASE_VOLUME
            charge_liquide = base_ajoute * prix_base + prix_arome * arome
            profits = prix_vente * int(nbr_flacon) - (charge_liquide + int(nbr_flacon) * PACKAGING_COST)

            # Display Results
            self.results_table.delete(*self.results_table.get_children())
            results = [
                ("Base ajoutée", f"{base_ajoute:.2f} ml"),
                ("Quantité totale", f"{total_liquid:.2f} ml"),
                ("Nombre de flacons", f"{nbr_flacon:.2f}"),
                ("Charges liquides", f"{charge_liquide:.2f} DT"),
                ("Profits totaux", f"{profits:.2f} DT"),
            ]
            for label, value in results:
                self.results_table.insert("", "end", values=(label, value))

            # Add to History in Structured Format
            new_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "arome_percentage": P_arome,
                "base_added": f"{base_ajoute:.2f} ml",
                "total_quantity": f"{total_liquid:.2f} ml",
                "bottles_count": f"{nbr_flacon:.2f}",
                "liquid_cost": f"{charge_liquide:.2f} DT",
                "total_profits": f"{profits:.2f} DT"
            }
            self.historique.append(new_entry)
            self.populate_history_table()  # Refresh the table

            # Save to JSON File
            self.save_history()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")



    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                self.historique = json.load(file)
        else:
            self.historique = []

    def save_history(self):
        with open(HISTORY_FILE, "w") as file:
            json.dump(self.historique, file, indent=4)

    def populate_history_table(self):
        self.history_table.delete(*self.history_table.get_children())  # Clear the table first
        total_profits = 0
        for entry in self.historique:
            self.history_table.insert("", "end", values=(
                entry["timestamp"],
                entry["arome_percentage"],
                entry["base_added"],
                entry["total_quantity"],
                entry["bottles_count"],
                entry["liquid_cost"],
                entry["total_profits"]
            ))
            try:
                total_profits += float(entry["total_profits"].split()[0])  # Extract numeric value from "X.XX DT"
            except (ValueError, KeyError):
                pass
        self.total_profits_label.config(text=f"Total Profits: {total_profits:.2f} DT")

    def clear_history(self, filename):  
        try:  
            if os.path.exists(filename):
                os.remove(filename)  
                self.historique = []
                self.history_table.delete(*self.history_table.get_children())  # Clear the table display
                messagebox.showinfo("Success", f"{filename} has been deleted.") 
                 
            else:
                messagebox.showwarning("Warning", "No history file found to delete.")
        except Exception as e:  
            messagebox.showerror("Error", f"An error occurred: {e}")

    def filter_history_table(self, event=None):
        keyword = self.filter_entry.get().lower()
        self.history_table.delete(*self.history_table.get_children())
        for entry in self.historique:
            if any(keyword in str(value).lower() for value in entry.values()):
                self.history_table.insert("", "end", values=tuple(entry.values()))

    def sort_history_table(self, column):
        reverse = getattr(self, "sort_reverse", {}).get(column, False)
        self.historique.sort(key=lambda x: self.parse_sort_value(x[column]), reverse=reverse)
        self.sort_reverse = {column: not reverse}  # Toggle sorting direction
        self.populate_history_table()

    def parse_sort_value(self, value):
        try:
            return float(value.split()[0])  # For numeric values like "270.00 ml"
        except (ValueError, AttributeError):
            return value  # For strings like "2024-11-26 13:54:22"


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceVapeApp(root)
    root.mainloop()
