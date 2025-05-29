import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from ttkthemes.themed_tk import ThemedTk

JSON_FILE = "apps.json"

def load_data():
    if not os.path.exists(JSON_FILE):
        return {"categories": []}
    with open(JSON_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)

class AppManager:
    def __init__(self, root):
        self.root = root
        self.root.title("App Manager")
        self.root.geometry("850x500")
        self.data = load_data()

        self.style = ttk.Style(self.root)
        self.style.theme_use("equilux")
        self.root.configure(bg="#2e2e2e")
        self.style.configure("Treeview", background="#333333", fieldbackground="#333333", foreground="white")
        self.style.configure("TLabel", background="#2e2e2e", foreground="white")
        self.style.configure("TFrame", background="#2e2e2e")
        self.style.configure("TButton", background="#444", foreground="white")

        self.setup_ui()
        self.populate_categories()

    def setup_ui(self):
        self.category_frame = ttk.Frame(self.root)
        self.category_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.app_frame = ttk.Frame(self.root)
        self.app_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.category_list = tk.Listbox(self.category_frame, width=30, bg="#2e2e2e", fg="white", selectbackground="#555")
        self.category_list.pack(fill="y", expand=True)
        self.category_list.bind("<<ListboxSelect>>", self.load_apps)

        ttk.Button(self.category_frame, text="Add Category", command=self.add_category).pack(fill="x", pady=2)
        ttk.Button(self.category_frame, text="Delete Category", command=self.delete_category).pack(fill="x", pady=2)

        self.app_list = ttk.Treeview(self.app_frame, columns=("name", "icon", "path", "desc"), show="headings")
        self.app_list.heading("name", text="Name")
        self.app_list.heading("icon", text="Icon")
        self.app_list.heading("path", text="Path")
        self.app_list.heading("desc", text="Description")
        self.app_list.pack(fill="both", expand=True)
        self.app_list.bind("<Double-1>", self.launch_app)

        btn_frame = ttk.Frame(self.app_frame)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Add App", command=self.add_app).pack(side="left", padx=5, pady=5)
        ttk.Button(btn_frame, text="Edit App", command=self.edit_app).pack(side="left", padx=5, pady=5)
        ttk.Button(btn_frame, text="Delete App", command=self.delete_app).pack(side="left", padx=5, pady=5)

    def populate_categories(self):
        self.category_list.delete(0, tk.END)
        for cat in self.data["categories"]:
            self.category_list.insert(tk.END, cat["name"])

    def load_apps(self, event=None):
        self.app_list.delete(*self.app_list.get_children())
        idx = self.category_list.curselection()
        if not idx:
            return
        category = self.data["categories"][idx[0]]
        for app in category["apps"]:
            icon_display = os.path.basename(app["icon"]) if app["icon"] else ""
            self.app_list.insert("", "end", values=(app["name"], icon_display, app["path"], app["description"]))

    def add_category(self):
        name = self.simple_input("Enter category name:")
        if not name:
            return
        icon = filedialog.askopenfilename(title="Select icon", filetypes=[("ICO files", "*.ico")])
        self.data["categories"].append({"name": name, "icon": icon, "apps": []})
        save_data(self.data)
        self.populate_categories()

    def delete_category(self):
        idx = self.category_list.curselection()
        if not idx:
            return
        del self.data["categories"][idx[0]]
        save_data(self.data)
        self.populate_categories()
        self.app_list.delete(*self.app_list.get_children())

    def add_app(self):
        idx = self.category_list.curselection()
        if not idx:
            messagebox.showinfo("Info", "Select a category first.")
            return
        cat = self.data["categories"][idx[0]]
        name = self.simple_input("App name:")
        if not name:
            return
        path = filedialog.askopenfilename(title="Select executable")
        if not path:
            return
        icon = filedialog.askopenfilename(title="Select icon", filetypes=[("ICO files", "*.ico")])
        desc = self.simple_input("Description:")
        app = {"name": name, "path": path, "icon": icon, "description": desc}
        cat["apps"].append(app)
        save_data(self.data)
        self.load_apps()

    def edit_app(self):
        cat_idx = self.category_list.curselection()
        app_item = self.app_list.focus()
        if not cat_idx or not app_item:
            messagebox.showinfo("Info", "Select an app to edit.")
            return

        app_index = self.app_list.index(app_item)
        app = self.data["categories"][cat_idx[0]]["apps"][app_index]

        popup = tk.Toplevel(self.root)
        popup.title("Edit App")
        popup.configure(bg="#2e2e2e")

        def make_label(text):
            return tk.Label(popup, text=text, bg="#2e2e2e", fg="white")

        make_label("Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_entry = tk.Entry(popup, bg="#333", fg="white", insertbackground="white")
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, app["name"])

        make_label("Path:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        path_var = tk.StringVar(value=app["path"])
        path_entry = tk.Entry(popup, textvariable=path_var, bg="#333", fg="white", insertbackground="white", width=40)
        path_entry.grid(row=1, column=1, padx=10, pady=5)

        def browse_path():
            file = filedialog.askopenfilename(title="Select executable")
            if file:
                path_var.set(file)

        ttk.Button(popup, text="Browse", command=browse_path).grid(row=1, column=2, padx=5, pady=5)

        make_label("Icon:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        icon_var = tk.StringVar(value=app["icon"])
        icon_entry = tk.Entry(popup, textvariable=icon_var, bg="#333", fg="white", insertbackground="white", width=40)
        icon_entry.grid(row=2, column=1, padx=10, pady=5)

        def browse_icon():
            file = filedialog.askopenfilename(title="Select icon", filetypes=[("ICO files", "*.ico")])
            if file:
                icon_var.set(file)

        ttk.Button(popup, text="Browse", command=browse_icon).grid(row=2, column=2, padx=5, pady=5)

        make_label("Description:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        desc_entry = tk.Entry(popup, bg="#333", fg="white", insertbackground="white")
        desc_entry.grid(row=3, column=1, padx=10, pady=5)
        desc_entry.insert(0, app["description"])

        def save_changes():
            app["name"] = name_entry.get()
            app["path"] = path_var.get()
            app["icon"] = icon_var.get()
            app["description"] = desc_entry.get()
            save_data(self.data)
            self.load_apps()
            popup.destroy()

        ttk.Button(popup, text="Save", command=save_changes).grid(row=4, column=0, columnspan=3, pady=10)

    def delete_app(self):
        cat_idx = self.category_list.curselection()
        app_idx = self.app_list.focus()
        if not cat_idx or not app_idx:
            return
        app_index = self.app_list.index(app_idx)
        del self.data["categories"][cat_idx[0]]["apps"][app_index]
        save_data(self.data)
        self.load_apps()

    def launch_app(self, event):
        item = self.app_list.focus()
        if not item:
            return
        cat_idx = self.category_list.curselection()[0]
        app_idx = self.app_list.index(item)
        path = self.data["categories"][cat_idx]["apps"][app_idx]["path"]
        try:
            subprocess.Popen(path)
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def simple_input(self, prompt):
        popup = tk.Toplevel(self.root)
        popup.title("Input")
        popup.configure(bg="#2e2e2e")
        tk.Label(popup, text=prompt, bg="#2e2e2e", fg="white").pack(padx=10, pady=10)
        entry = tk.Entry(popup, bg="#333", fg="white", insertbackground="white")
        entry.pack(padx=10, pady=5)
        entry.focus()
        result = []

        def confirm():
            result.append(entry.get())
            popup.destroy()

        ttk.Button(popup, text="OK", command=confirm).pack(pady=5)
        popup.wait_window()
        return result[0] if result else None

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = AppManager(root)
    root.mainloop()
