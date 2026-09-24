"""Console entry point for the Multi-Management System."""
from student_manager import RecordManager, StudentManager

MODULES = {
    "1": ("Student Management", StudentManager(), ("student_id", "name", "age", "course", "email")),
    "2": ("Library Management", RecordManager("data/books.json", ("book_id", "title", "author", "quantity"), "book_id"), ("book_id", "title", "author", "quantity")),
    "3": ("Inventory Management", RecordManager("data/items.json", ("item_id", "item_name", "category", "quantity", "price"), "item_id"), ("item_id", "item_name", "category", "quantity", "price")),
}

def is_student(manager): return isinstance(manager, StudentManager)
def all_records(manager): return manager.all_students() if is_student(manager) else manager.all()
def find(manager, key): return manager.find_by_id(key) if is_student(manager) else manager.find(key)
def add(manager, data): return manager.add_student(data) if is_student(manager) else manager.add(data)
def update(manager, key, data): return manager.update_student(key, data) if is_student(manager) else manager.update(key, data)
def delete(manager, key): return manager.delete_student(key) if is_student(manager) else manager.delete(key)

def collect(fields, existing=None):
    result = {}
    for field in fields:
        current = f" [{existing[field]}]" if existing else ""
        entered = input(f"{field.replace('_', ' ').title()}{current}: ").strip()
        result[field] = entered or (existing[field] if existing else "")
    return result

def show(items, fields):
    if not items: print("\nNo records found."); return
    print("\n" + " | ".join(field.replace("_", " ").title() for field in fields))
    print("-" * 90)
    for item in items: print(" | ".join(str(item[field]) for field in fields))

def run_module(title, manager, fields):
    id_field = fields[0]
    while True:
        print(f"\n--- {title} ---\n1. Add  2. View all  3. Search  4. Update  5. Delete  0. Back")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1": add(manager, collect(fields)); print("Record added successfully.")
            elif choice == "2": show(all_records(manager), fields)
            elif choice == "3": show(manager.search(input("Search term: ")), fields)
            elif choice == "4":
                key = input(f"{id_field.replace('_', ' ').title()} to update: "); old = find(manager, key)
                if not old: raise ValueError("Record was not found.")
                update(manager, key, collect(fields, old)); print("Record updated successfully.")
            elif choice == "5":
                key = input(f"{id_field.replace('_', ' ').title()} to delete: ")
                if input("Confirm deletion (y/n): ").lower() == "y": delete(manager, key); print("Record deleted successfully.")
            elif choice == "0": return
            else: print("Please choose a valid option.")
        except ValueError as error: print(f"Error: {error}")

def main():
    while True:
        print("\n========== MULTI-MANAGEMENT SYSTEM ==========\n1. Student Management\n2. Library Management\n3. Inventory Management\n0. Exit")
        selection = input("Choose a module: ").strip()
        if selection == "0": print("Goodbye!"); break
        if selection in MODULES: run_module(*MODULES[selection])
        else: print("Please choose a valid module.")

if __name__ == "__main__": main()
