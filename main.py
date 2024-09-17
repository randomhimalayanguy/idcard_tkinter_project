import customtkinter as ctk
from tkinter import filedialog
import os
import id_gen_logic as logic
import threading

def select_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_path.set(file_path)
        csv_display.configure(text=os.path.basename(file_path))

def export():
    if not csv_path.get():
        print("Please select a CSV file first.")
        return

    export_button.configure(state="disabled")  # Disable the button during processing
    msg_box = ctk.CTkLabel(app, text="Processing, Please Wait")
    msg_box.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")

    def run_export():
        nonlocal msg_box
        msg = logic.generate(csv_path.get(), batch_year.get())

        # Update GUI in the main thread
        app.after(0, lambda: update_gui(msg_box, msg))

    # Start the export process in a separate thread
    thread = threading.Thread(target=run_export)
    thread.start()

def update_gui(msg_box, msg):
    msg_box.grid_remove()
    new_msg_box = ctk.CTkLabel(app, text=msg)
    new_msg_box.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")
    export_button.configure(state="normal")  # Re-enable the button

# Create the main window
app = ctk.CTk()
app.title("ID Card Generator")
app.geometry("500x400")

app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(3, weight=1)

# Create variables
csv_path = ctk.StringVar()
batch_year = ctk.StringVar()

# CSV File Selection
csv_label = ctk.CTkLabel(app, text="Selected CSV:")
csv_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

csv_display = ctk.CTkLabel(app, text="No file selected", fg_color="black", corner_radius=6)
csv_display.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

csv_button = ctk.CTkButton(app, text="Select CSV", command=select_csv)
csv_button.grid(row=1, column=1, padx=(0, 20), pady=(0, 10))

# Batch Year Selection
year_label = ctk.CTkLabel(app, text="Batch Year:")
year_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

current_year = 2024
years = [f"{year}-{year - 2000 + 3}" for year in range(current_year - 3, current_year + 7)]
year_combo = ctk.CTkComboBox(app, values=years, variable=batch_year)
year_combo.set("2024-27")
year_combo.grid(row=2, column=1, padx=(0, 20), pady=(10, 0))

# Export Button
export_button = ctk.CTkButton(app, text="Export", command=export)
export_button.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="s")

# Start the application
if __name__ == "__main__":
    app.mainloop()