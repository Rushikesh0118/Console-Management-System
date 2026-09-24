"""Tabbed Tkinter UI for the Multi-Management System."""
import tkinter as tk
from tkinter import messagebox, ttk
from student_manager import RecordManager, StudentManager

class ManagementTab(ttk.Frame):
    def __init__(self, parent, manager, fields):
        super().__init__(parent, padding=15)
        self.manager, self.fields = manager, fields
        self.values = {f: tk.StringVar() for f in fields}; self.query = tk.StringVar()
        self.build(); self.refresh()
    def student(self): return isinstance(self.manager, StudentManager)
    def all(self): return self.manager.all_students() if self.student() else self.manager.all()
    def find(self, key): return self.manager.find_by_id(key) if self.student() else self.manager.find(key)
    def build(self):
        form = ttk.LabelFrame(self, text="Record details", padding=10); form.pack(fill="x")
        for i, field in enumerate(self.fields):
            ttk.Label(form, text=field.replace("_", " ").title()).grid(row=0, column=i, sticky="w", padx=4)
            ttk.Entry(form, textvariable=self.values[field], width=18).grid(row=1, column=i, sticky="ew", padx=4, pady=(3, 8)); form.columnconfigure(i, weight=1)
        actions = ttk.Frame(form); actions.grid(row=2, column=0, columnspan=len(self.fields), sticky="w")
        for label, method in (("Add", self.add), ("Update Selected", self.update), ("Delete Selected", self.delete), ("Clear", self.clear)):
            ttk.Button(actions, text=label, command=method).pack(side="left", padx=4)
        bar = ttk.Frame(self); bar.pack(fill="x", pady=12)
        ttk.Label(bar, text="Search:").pack(side="left")
        search = ttk.Entry(bar, textvariable=self.query, width=35); search.pack(side="left", padx=7); search.bind("<KeyRelease>", lambda event: self.refresh())
        self.count = ttk.Label(bar); self.count.pack(side="right")
        self.table = ttk.Treeview(self, columns=self.fields, show="headings")
        for field in self.fields:
            self.table.heading(field, text=field.replace("_", " ").title()); self.table.column(field, width=140, anchor="w")
        self.table.pack(fill="both", expand=True); self.table.bind("<<TreeviewSelect>>", self.load)
    def refresh(self):
        for item in self.table.get_children(): self.table.delete(item)
        data = self.manager.search(self.query.get()) if self.query.get() else self.all()
        for record in data: self.table.insert("", "end", values=[record[f] for f in self.fields])
        self.count.config(text=f"{len(data)} record(s)")
    def clear(self):
        for value in self.values.values(): value.set("")
        self.table.selection_remove(self.table.selection())
    def load(self, event=None):
        chosen = self.table.selection()
        if chosen:
            record = self.find(self.table.item(chosen[0], "values")[0])
            for field in self.fields: self.values[field].set(str(record[field]))
    def add(self):
        try:
            data = {f: v.get() for f, v in self.values.items()}
            (self.manager.add_student if self.student() else self.manager.add)(data)
            self.clear(); self.refresh(); messagebox.showinfo("Success", "Record added successfully.")
        except ValueError as error: messagebox.showerror("Error", str(error))
    def update(self):
        chosen = self.table.selection()
        if not chosen: messagebox.showwarning("Select a record", "Select a record first."); return
        try:
            data = {f: v.get() for f, v in self.values.items()}; old_key = self.table.item(chosen[0], "values")[0]
            (self.manager.update_student if self.student() else self.manager.update)(old_key, data)
            self.clear(); self.refresh(); messagebox.showinfo("Success", "Record updated successfully.")
        except ValueError as error: messagebox.showerror("Error", str(error))
    def delete(self):
        chosen = self.table.selection()
        if not chosen: messagebox.showwarning("Select a record", "Select a record first."); return
        key = self.table.item(chosen[0], "values")[0]
        if messagebox.askyesno("Confirm deletion", f"Delete {key}?"):
            (self.manager.delete_student if self.student() else self.manager.delete)(key); self.clear(); self.refresh()

def main():
    app = tk.Tk(); app.title("Multi-Management System"); app.geometry("1050x620"); app.minsize(850, 500)
    ttk.Label(app, text="Multi-Management System", font=("Arial", 20, "bold")).pack(anchor="w", padx=18, pady=(15, 0))
    ttk.Label(app, text="Manage students, library books, and inventory from one place.").pack(anchor="w", padx=18, pady=(0, 12))
    tabs = ttk.Notebook(app); tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    tabs.add(ManagementTab(tabs, StudentManager(), ("student_id", "name", "age", "course", "email")), text="Students")
    tabs.add(ManagementTab(tabs, RecordManager("data/books.json", ("book_id", "title", "author", "quantity"), "book_id"), ("book_id", "title", "author", "quantity")), text="Library")
    tabs.add(ManagementTab(tabs, RecordManager("data/items.json", ("item_id", "item_name", "category", "quantity", "price"), "item_id"), ("item_id", "item_name", "category", "quantity", "price")), text="Inventory")
    app.mainloop()
if __name__ == "__main__": main()
