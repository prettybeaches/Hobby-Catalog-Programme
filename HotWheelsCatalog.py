import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json
import uuid
import shutil

DATA_FILE = "catalog.json"
BRAND_FILE = "brands.json"
IMAGE_DIR = "images"
THUMB_DIR = os.path.join(IMAGE_DIR, "thumbs")
THUMB_SIZE = (100, 100)

os.makedirs(THUMB_DIR, exist_ok=True)

DEFAULT_BRANDS = ["HotWheels", "Matchbox", "Majorette"]


def load_catalog():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


def save_catalog(catalog):
    with open(DATA_FILE, 'w') as f:
        json.dump(catalog, f, indent=4)


def load_brands():
    if os.path.exists(BRAND_FILE):
        with open(BRAND_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_BRANDS.copy()


def save_brands(brand_list):
    with open(BRAND_FILE, 'w') as f:
        json.dump(brand_list, f, indent=4)


def create_thumbnail(image_path, thumb_path):
    img = Image.open(image_path)
    img.thumbnail(THUMB_SIZE)
    img.save(thumb_path)


class HotWheelsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hot Wheels Catalog")
        self.root.minsize(800, 600)

        self.catalog = load_catalog()
        self.filtered_catalog = self.catalog.copy()
        self.brand_list = load_brands()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Clickable.TLabel", foreground="black")
        style.map("Clickable.TLabel", background=[("active", "#cccccc")])

        self.catalog_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.catalog_tab, text="Catalog")

        self.car_image_path = None

        self.init_catalog_tab()

        # Define open_add_tab function
        self.brand_dropdown = None

    def open_add_tab(self):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == "Add Car":
                self.notebook.select(tab_id)
                return
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add Car")
        self.init_add_tab()
        self.notebook.select(self.add_tab)

    def init_add_tab(self):
        # Close button for Add Car tab
        tk.Button(self.add_tab, text="Close Tab", command=lambda: self.close_tab(self.add_tab), cursor="hand2").pack(
            anchor='ne', padx=5, pady=5)
        frame = tk.Frame(self.add_tab)
        frame.pack(fill='both', expand=True)
        labels = ["Brand", "Model", "Year", "Bought Value", "Internet Value", "Notes"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky='e')
            if label == "Brand":
                self.brand_var = tk.StringVar()
                self.brand_dropdown = ttk.Combobox(frame, textvariable=self.brand_var, values=self.brand_list,
                                                   state="readonly", width=37)
                self.brand_dropdown.grid(row=i, column=1, sticky='w')
                self.brand_dropdown.set(self.brand_list[0])
                add_button = tk.Button(frame, text="+", width=3, command=self.add_custom_brand, cursor="hand2")
                add_button.grid(row=i, column=2, sticky='w', padx=5)
            else:
                entry = tk.Entry(frame, width=40)
                entry.grid(row=i, column=1, columnspan=2, pady=2, sticky='w')
                self.entries[label.lower().replace(" ", "_")] = entry

        tk.Label(frame, text="State").grid(row=len(labels), column=0, sticky='e')
        self.cased_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Cased", variable=self.cased_var).grid(row=len(labels), column=1, sticky='w')
        tk.Button(frame, text="Upload Image", command=self.upload_image, cursor="hand2").grid(row=7, column=0,
                                                                                              columnspan=3, pady=5)
        tk.Button(frame, text="Add Car", command=self.add_car, cursor="hand2").grid(row=8, column=0, columnspan=3,
                                                                                    pady=5)

    def add_custom_brand(self):
        brand_window = tk.Toplevel(self.root)
        brand_window.update_idletasks()
        w = 300
        h = 180
        x = (brand_window.winfo_screenwidth() // 2) - (w // 2)
        y = (brand_window.winfo_screenheight() // 2) - (h // 2)
        brand_window.geometry(f"{w}x{h}+{x}+{y}")
        brand_window.title("Manage Brands")
        brand_window.transient(self.root)
        brand_window.grab_set()

        tk.Button(brand_window, text="Add Brand", width=15,
                  command=lambda: [brand_window.destroy(), self.prompt_add_brand()]).pack(pady=10)
        tk.Button(brand_window, text="Delete Brand", width=15,
                  command=lambda: [brand_window.destroy(), self.delete_brand()]).pack(pady=10)
        tk.Button(brand_window, text="Edit Brand", width=15,
                  command=lambda: [brand_window.destroy(), self.edit_brand()]).pack(pady=10)

    def prompt_add_brand(self):
        self.brand_image_path = None

        def upload_brand_image():
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.gif")])
            if path:
                self.brand_image_path = path
                messagebox.showinfo("Image", "Brand image uploaded successfully.")

        brand_prompt = tk.Toplevel(self.root)
        brand_prompt.title("Add Brand")
        brand_prompt.update_idletasks()
        w = 300
        h = 180
        x = (brand_prompt.winfo_screenwidth() // 2) - (w // 2)
        y = (brand_prompt.winfo_screenheight() // 2) - (h // 2)
        brand_prompt.geometry(f"{w}x{h}+{x}+{y}")
        brand_prompt.transient(self.root)
        brand_prompt.grab_set()

        tk.Label(brand_prompt, text="Enter new brand name:").pack(pady=5)
        brand_entry = tk.Entry(brand_prompt)
        brand_entry.pack(pady=5)

        tk.Button(brand_prompt, text="Upload Image", command=upload_brand_image).pack(pady=5)

        def submit_brand():
            new_brand = brand_entry.get().strip()
            if new_brand and new_brand not in self.brand_list:
                self.brand_list.append(new_brand)
                save_brands(self.brand_list)
                self.brand_dropdown['values'] = self.brand_list
                self.brand_dropdown.set(new_brand)
                if self.brand_image_path:
                    ext = os.path.splitext(self.brand_image_path)[1]
                    brand_img_filename = f"{new_brand.replace(' ', '_')}_logo{ext}"
                    dest_path = os.path.join(IMAGE_DIR, brand_img_filename)
                    shutil.copy(self.brand_image_path, dest_path)
                brand_prompt.destroy()

        tk.Button(brand_prompt, text="Add Brand", command=submit_brand).pack(pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.gif")])
        if file_path:
            self.car_image_path = file_path
            messagebox.showinfo("Image", "Image uploaded successfully.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.cased_var.set(True)
        self.brand_dropdown.set(self.brand_list[0])
        self.car_image_path = None

    def add_car(self):
        data = {}
        brand = self.brand_var.get().strip()
        if not brand:
            messagebox.showerror("Error", "Brand is required.")
            return
        data["brand"] = brand

        for key, entry in self.entries.items():
            value = entry.get().strip()
            if key in ['bought_value', 'internet_value', 'year']:
                if not value:
                    value = 0
                try:
                    value = float(value)
                except ValueError:
                    messagebox.showerror("Error", f"{key.replace('_', ' ').title()} must be a number.")
                    return
            data[key] = value

        data["open_state"] = "Cased" if self.cased_var.get() else "Open"

        if not self.car_image_path:
            placeholder_path = os.path.join(IMAGE_DIR, "placeholder.png")
            if not os.path.exists(placeholder_path):
                img = Image.new('RGB', (300, 300), color=(200, 200, 200))
                img.save(placeholder_path)
            self.car_image_path = placeholder_path

        car_id = str(uuid.uuid4())
        ext = os.path.splitext(self.car_image_path)[1]
        image_filename = f"{car_id}{ext}"
        thumb_filename = f"{car_id}_thumb{ext}"
        image_dest = os.path.join(IMAGE_DIR, image_filename)
        thumb_dest = os.path.join(THUMB_DIR, thumb_filename)

        shutil.copy(self.car_image_path, image_dest)
        create_thumbnail(image_dest, thumb_dest)

        data["image"] = image_filename
        data["thumb"] = thumb_filename
        data["id"] = car_id

        self.catalog.append(data)
        self.filtered_catalog = self.catalog.copy()
        save_catalog(self.catalog)
        self.refresh_catalog()

        # Add '+' button fixed to bottom right of the visible catalog_tab

        messagebox.showinfo("Success", "Car added to catalog.")
        self.clear_form()

    def edit_brand(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Brand")
        edit_window.update_idletasks()
        w = 300
        h = 200
        x = (edit_window.winfo_screenwidth() // 2) - (w // 2)
        y = (edit_window.winfo_screenheight() // 2) - (h // 2)
        edit_window.geometry(f"{w}x{h}+{x}+{y}")
        edit_window.transient(self.root)
        edit_window.grab_set()
        edit_window.lift()
        edit_window.attributes('-topmost', True)

        tk.Label(edit_window, text="Select existing brand:").pack(pady=5)
        old_var = tk.StringVar()
        old_entry = ttk.Combobox(edit_window, textvariable=old_var, values=self.brand_list, state="readonly")
        old_entry.pack(pady=5)
        old_entry.set(self.brand_list[0])

        tk.Label(edit_window, text="Enter new brand name:").pack(pady=5)
        new_entry = tk.Entry(edit_window)
        new_entry.pack(pady=5)

        image_path = tk.StringVar()

        def upload_image():
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.gif")])
            if path:
                image_path.set(path)
                messagebox.showinfo("Image", "Brand image selected.")

        tk.Button(edit_window, text="Upload New Image", command=upload_image).pack(pady=5)

        def apply_edit():
            old_brand = old_var.get().strip()
            new_brand = new_entry.get().strip() or old_brand
            if old_brand not in self.brand_list:
                messagebox.showerror("Error", f"'{old_brand}' is not in the brand list.", parent=edit_window)
                return
            if not new_brand:
                messagebox.showerror("Error", "New brand name cannot be empty.", parent=edit_window)
                return
            if new_brand != old_brand and new_brand in self.brand_list:
                messagebox.showerror("Error", f"'{new_brand}' already exists.", parent=edit_window)
                return

            for car in self.catalog:
                if car["brand"] == old_brand:
                    car["brand"] = new_brand

            self.brand_list.remove(old_brand)
            self.brand_list.append(new_brand)
            save_brands(self.brand_list)
            save_catalog(self.catalog)
            self.brand_dropdown['values'] = self.brand_list
            self.brand_dropdown.set(new_brand)

            if image_path.get():
                ext = os.path.splitext(image_path.get())[1]
                brand_img_filename = f"{new_brand.replace(' ', '_')}_logo{ext}"
                dest_path = os.path.join(IMAGE_DIR, brand_img_filename)
                shutil.copy(image_path.get(), dest_path)
            else:
                # If the brand was renamed but no new image uploaded, rename old image if it exists
                for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                    old_path = os.path.join(IMAGE_DIR, f"{old_brand.replace(' ', '_')}_logo{ext}")
                    if os.path.exists(old_path):
                        new_path = os.path.join(IMAGE_DIR, f"{new_brand.replace(' ', '_')}_logo{ext}")
                        shutil.move(old_path, new_path)
                        break

            messagebox.showinfo("Success", f"'{old_brand}' updated to '{new_brand}'.", parent=edit_window)
            edit_window.destroy()

        tk.Button(edit_window, text="Apply Changes", command=apply_edit).pack(pady=10)


    def delete_brand(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Brand")
        delete_window.update_idletasks()
        w = 300
        h = 150
        x = (delete_window.winfo_screenwidth() // 2) - (w // 2)
        y = (delete_window.winfo_screenheight() // 2) - (h // 2)
        delete_window.geometry(f"{w}x{h}+{x}+{y}")
        delete_window.transient(self.root)
        delete_window.grab_set()
        delete_window.lift()
        delete_window.attributes('-topmost', True)

        tk.Label(delete_window, text="Select the brand to delete:").pack(pady=5)
        brand_var = tk.StringVar()
        entry = ttk.Combobox(delete_window, textvariable=brand_var, values=self.brand_list, state="readonly")
        entry.pack(pady=5)
        entry.set(self.brand_list[0])

        def confirm_delete():
            brand_to_delete = brand_var.get().strip()
            if not brand_to_delete:
                return
            if brand_to_delete not in self.brand_list:
                messagebox.showerror("Error", f"'{brand_to_delete}' is not in the brand list.")
                return
            if any(car['brand'] == brand_to_delete for car in self.catalog):
                messagebox.showerror("Error", f"Cannot delete '{brand_to_delete}' — it's in use by existing cars.")
                return
            self.brand_list.remove(brand_to_delete)
            save_brands(self.brand_list)
            self.brand_dropdown['values'] = self.brand_list
            self.brand_dropdown.set(self.brand_list[0])
            delete_window.lift()
            delete_window.attributes('-topmost', True)
            messagebox.showinfo("Deleted", f"'{brand_to_delete}' was removed from the brand list.",
                                parent=delete_window)
            delete_window.attributes('-topmost', False)
            delete_window.destroy()

        tk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)
        return
        brand_to_delete = simpledialog.askstring("Delete Brand", "Enter the brand name to delete:")
        if not brand_to_delete:
            return
        if brand_to_delete not in self.brand_list:
            messagebox.showerror("Error", f"'{brand_to_delete}' is not in the brand list.")
            return
        if any(car['brand'] == brand_to_delete for car in self.catalog):
            messagebox.showerror("Error", f"Cannot delete '{brand_to_delete}' — it's in use by existing cars.")
            return
        self.brand_list.remove(brand_to_delete)
        save_brands(self.brand_list)
        self.brand_dropdown['values'] = self.brand_list
        self.brand_dropdown.set(self.brand_list[0])
        messagebox.showinfo("Deleted", f"'{brand_to_delete}' was removed from the brand list.")

        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.cased_var.set(False)
        self.brand_dropdown.set(self.brand_list[0])
        self.car_image_path = None

    def init_catalog_tab(self):
        search_frame = ttk.Frame(self.catalog_tab)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Search: ").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda event: self.apply_search())

        self.catalog_canvas = tk.Canvas(self.catalog_tab)
        self.catalog_frame = ttk.Frame(self.catalog_canvas)
        self.scrollbar = ttk.Scrollbar(self.catalog_tab, orient="vertical", command=self.catalog_canvas.yview)
        self.catalog_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.catalog_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.catalog_canvas.create_window((0, 0), window=self.catalog_frame, anchor="nw")
        self.catalog_canvas.bind_all("<MouseWheel>",
                                     lambda event: self.catalog_canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                                                                    "units"))
        self.catalog_frame.bind("<Configure>",
                                lambda e: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))

        self.refresh_catalog()

        # Fixed-position '+' button at bottom-right of the catalog tab
        self.add_car_button = tk.Button(
            self.catalog_tab,
            text='+',
            width=5,
            font=('Arial', 16),
            command=self.open_add_tab,
            cursor='hand2',
            bg='#007acc',
            fg='white',
            activebackground='#005f99',
            activeforeground='white'
        )
        self.add_car_button.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20)
        self.add_car_button.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20)

    def apply_search(self):
        term = self.search_var.get().lower()
        self.filtered_catalog = [car for car in self.catalog if
                                 term in car['model'].lower() or term in car['brand'].lower()]
        self.refresh_catalog()

    def refresh_catalog(self):
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()

        brand_sections = {}
        for car in self.filtered_catalog:
            brand = car["brand"]
            brand_sections.setdefault(brand, []).append(car)

        row = 0
        for brand in sorted(brand_sections.keys()):
            brand_label = tk.Label(self.catalog_frame, text=brand, font=("Arial", 11), cursor="hand2", bg="#f0f0f0",
                                   activebackground="#cccccc")
            brand_label.grid(row=row, column=0, sticky='w', pady=(10, 0))
            brand_label.bind("<Button-1>", lambda e, b=brand: self.open_brand_tab(b))
            row += 1
            sep = ttk.Separator(self.catalog_frame, orient='horizontal')
            sep.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(0, 5))
            row += 1

            for i, car in enumerate(brand_sections[brand]):
                img_path = os.path.join(THUMB_DIR, car["thumb"])
                img = Image.open(img_path)
                if car.get("open_state") == "Open":
                    red_dot = Image.new('RGBA', (15, 15), (255, 0, 0, 0))
                    dot_draw = Image.new('L', (15, 15), 0)
                    for x in range(15):
                        for y in range(15):
                            if (x - 7) ** 2 + (y - 7) ** 2 <= 49:
                                dot_draw.putpixel((x, y), 255)
                    red_dot.putalpha(dot_draw)
                    img.paste(red_dot, (img.width - 18, 3), red_dot)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(self.catalog_frame, image=photo, text=car["model"], compound="top", cursor="hand2",
                                 bg="#f0f0f0")
                label.bind("<Enter>", lambda e, w=label: w.configure(bg="#cccccc"))
                label.bind("<Leave>", lambda e, w=label: w.configure(bg="#f0f0f0"))
                label.image = photo
                label.grid(row=row + i // 4, column=i % 4, padx=10, pady=10)
                label.bind("<Button-1>", lambda e, c=car: self.open_detail_tab(c))

            row += (len(brand_sections[brand]) + 3) // 4

    def open_detail_tab(self, car):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == car["model"]:
                self.notebook.select(tab_id)
                return

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=car["model"])
        self.notebook.select(tab)

        tk.Button(tab, text="Close Tab", command=lambda: self.close_tab(tab), cursor="hand2").pack(anchor='ne', padx=5,
                                                                                                   pady=5)

                # Display brand logo in top-left if available
        brand_logo_path = os.path.join(IMAGE_DIR, f"{car['brand'].replace(' ', '_')}_logo.png")
        if not os.path.exists(brand_logo_path):
            brand_logo_path = os.path.join(IMAGE_DIR, f"{car['brand'].replace(' ', '_')}_logo.jpg")
        if os.path.exists(brand_logo_path):
            logo_img = Image.open(brand_logo_path)
            logo_img.thumbnail((160, 160))
            brand_logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(tab, image=brand_logo)
            logo_label.image = brand_logo
            logo_label.pack(anchor='nw', padx=10, pady=(5, 0))

        full_img_path = os.path.join(IMAGE_DIR, car["image"])
        full_img = Image.open(full_img_path)
        full_img.thumbnail((300, 300))
        full_photo = ImageTk.PhotoImage(full_img)

        img_label = tk.Label(tab, image=full_photo)
        img_label.image = full_photo
        img_label.pack()

        tk.Button(tab, text="Change Image", command=lambda: self.change_car_image(car, img_label), cursor="hand2").pack(
            pady=5)

        self.detail_entries = {}
        for key in ["brand", "model", "year", "bought_value", "internet_value", "notes", "open_state"]:
            frame = tk.Frame(tab)
            frame.grid_columnconfigure(1, weight=1)
            frame.pack(fill="x", padx=10, pady=2)
            tk.Label(frame, text=key.replace("_", " ").title() + ":", width=15, anchor='w').grid(row=0, column=0,
                                                                                                 sticky='w')

            if key == "open_state":
                var = tk.BooleanVar(value=(car.get("open_state") == "Cased"))
                chk = tk.Checkbutton(frame, text="Cased", variable=var)
                chk.grid(row=0, column=1, sticky='w')
                self.detail_entries[key] = var
            else:
                entry = tk.Entry(frame, width=40)
                entry.insert(0, str(car.get(key, "")))
                if key == "brand":
                    entry.configure(state="readonly")
                entry.grid(row=0, column=1, sticky='w')
                self.detail_entries[key] = entry

        button_frame = tk.Frame(tab)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Save Changes", command=lambda: self.save_edited_car(car, tab),
                  cursor="hand2").pack(side="left", padx=10)
        tk.Button(button_frame, text="Duplicate Car", command=lambda: self.duplicate_car(car), cursor="hand2").pack(
            side="left", padx=10)
        tk.Button(button_frame, text="Delete Car", fg="red", command=lambda: self.delete_car(car, tab),
                  cursor="hand2").pack(side="left", padx=10)

    def change_car_image(self, car, img_label):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.gif")])
        if not file_path:
            return

        image_dest = os.path.join(IMAGE_DIR, car["image"])
        thumb_dest = os.path.join(THUMB_DIR, car["thumb"])

        shutil.copy(file_path, image_dest)
        create_thumbnail(image_dest, thumb_dest)

        img = Image.open(image_dest).resize((300, 300))
        updated_photo = ImageTk.PhotoImage(img)
        img_label.configure(image=updated_photo)
        img_label.image = updated_photo

        save_catalog(self.catalog)
        self.refresh_catalog()
        messagebox.showinfo("Updated", "Image updated successfully.")

    def duplicate_car(self, car):
        new_car = car.copy()
        new_id = str(uuid.uuid4())
        ext = os.path.splitext(new_car["image"])[1]
        new_car["id"] = new_id
        new_car["image"] = f"{new_id}{ext}"
        new_car["thumb"] = f"{new_id}_thumb{ext}"

        shutil.copy(os.path.join(IMAGE_DIR, car["image"]), os.path.join(IMAGE_DIR, new_car["image"]))
        shutil.copy(os.path.join(THUMB_DIR, car["thumb"]), os.path.join(THUMB_DIR, new_car["thumb"]))

        self.catalog.append(new_car)
        self.filtered_catalog = self.catalog.copy()
        save_catalog(self.catalog)
        self.refresh_catalog()
        messagebox.showinfo("Duplicated", f"{car['model']} duplicated successfully.")

    def delete_car(self, car, tab):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {car['model']}?")
        if confirm:
            self.catalog = [c for c in self.catalog if c['id'] != car['id']]
            self.filtered_catalog = self.catalog.copy()
            save_catalog(self.catalog)
            self.refresh_catalog()
            self.close_tab(tab)

    def open_brand_tab(self, brand):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == brand:
                self.notebook.select(tab_id)
                return

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=brand)
        self.notebook.select(tab)

        tk.Button(tab, text="Close Tab", command=lambda: self.close_tab(tab)).pack(anchor='ne', padx=5, pady=5)
        tk.Label(tab, text=brand, font=("Arial", 14, "bold"), anchor="center").pack(pady=(0, 5))
        ttk.Separator(tab, orient='horizontal').pack(fill='x', padx=10, pady=(0, 10))

        canvas = tk.Canvas(tab)
        frame = ttk.Frame(canvas)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        brand_cars = [car for car in self.catalog if car["brand"] == brand]
        for i, car in enumerate(brand_cars):
            img_path = os.path.join(THUMB_DIR, car["thumb"])
            img = Image.open(img_path)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo, text=car["model"], compound="top", cursor="hand2", bg="#f0f0f0")
            label.bind("<Enter>", lambda e, w=label: w.configure(bg="#cccccc"))
            label.bind("<Leave>", lambda e, w=label: w.configure(bg="#f0f0f0"))
            label.image = photo
            label.grid(row=i // 4, column=i % 4, padx=10, pady=10)
            label.bind("<Button-1>", lambda e, c=car: self.open_detail_tab(c))

    def close_tab(self, tab):
        self.notebook.forget(tab)
        self.notebook.select(self.catalog_tab)

    def save_edited_car(self, car, tab):
        for key, entry in self.detail_entries.items():
            if key == "open_state":
                car[key] = "Cased" if entry.get() else "Open"
            else:
                value = entry.get().strip()
                if key in ['bought_value', 'internet_value', 'year']:
                    try:
                        value = float(value)
                    except ValueError:
                        messagebox.showerror("Error", f"{key.replace('_', ' ').title()} must be a number.")
                        return
                car[key] = value

        save_catalog(self.catalog)
        self.refresh_catalog()
        messagebox.showinfo("Success", "Car details updated.")
        self.close_tab(tab)


if __name__ == "__main__":
    root = tk.Tk()
    app = HotWheelsApp(root)
    root.mainloop()
