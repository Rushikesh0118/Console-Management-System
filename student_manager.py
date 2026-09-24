"""Core data-management logic for the Student Management System."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class StudentManager:
    """Manage student records stored in a local JSON file."""

    REQUIRED_FIELDS = ("student_id", "name", "age", "course", "email")
    EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, data_file: str | Path = "data/students.json") -> None:
        self.data_file = Path(data_file)
        self.students: list[dict[str, Any]] = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if not self.data_file.exists():
            return []
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                records = json.load(file)
            return records if isinstance(records, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(self.students, file, indent=4, ensure_ascii=False)

    @classmethod
    def validate(cls, record: dict[str, Any]) -> dict[str, Any]:
        """Return a cleaned record or raise ValueError when input is invalid."""
        cleaned = {field: str(record.get(field, "")).strip() for field in cls.REQUIRED_FIELDS}
        missing = [field.replace("_", " ").title() for field, value in cleaned.items() if not value]
        if missing:
            raise ValueError(f"Required field(s): {', '.join(missing)}.")
        if not cleaned["age"].isdigit() or not 3 <= int(cleaned["age"]) <= 120:
            raise ValueError("Age must be a number between 3 and 120.")
        if not cls.EMAIL_PATTERN.match(cleaned["email"]):
            raise ValueError("Enter a valid email address.")
        cleaned["student_id"] = cleaned["student_id"].upper()
        cleaned["name"] = " ".join(word.capitalize() for word in cleaned["name"].split())
        cleaned["course"] = " ".join(word.capitalize() for word in cleaned["course"].split())
        cleaned["age"] = int(cleaned["age"])
        return cleaned

    def all_students(self) -> list[dict[str, Any]]:
        return sorted(self.students, key=lambda student: student["student_id"])

    def find_by_id(self, student_id: str) -> dict[str, Any] | None:
        normalized_id = student_id.strip().upper()
        return next((s for s in self.students if s["student_id"] == normalized_id), None)

    def add_student(self, record: dict[str, Any]) -> dict[str, Any]:
        student = self.validate(record)
        if self.find_by_id(student["student_id"]):
            raise ValueError("A student with this ID already exists.")
        self.students.append(student)
        self._save()
        return student

    def update_student(self, student_id: str, record: dict[str, Any]) -> dict[str, Any]:
        existing = self.find_by_id(student_id)
        if not existing:
            raise ValueError("Student ID was not found.")
        student = self.validate(record)
        if student["student_id"] != existing["student_id"] and self.find_by_id(student["student_id"]):
            raise ValueError("A student with the new ID already exists.")
        existing.update(student)
        self._save()
        return existing

    def delete_student(self, student_id: str) -> None:
        student = self.find_by_id(student_id)
        if not student:
            raise ValueError("Student ID was not found.")
        self.students.remove(student)
        self._save()

    def search(self, query: str) -> list[dict[str, Any]]:
        query = query.strip().casefold()
        if not query:
            return self.all_students()
        return [
            student for student in self.all_students()
            if query in student["student_id"].casefold()
            or query in student["name"].casefold()
            or query in student["course"].casefold()
            or query in student["email"].casefold()
        ]

    def course_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for student in self.students:
            summary[student["course"]] = summary.get(student["course"], 0) + 1
        return dict(sorted(summary.items()))


class RecordManager:
    """Reusable JSON-backed CRUD manager for library and inventory records."""

    def __init__(self, data_file: str | Path, fields: tuple[str, ...], id_field: str) -> None:
        self.data_file, self.fields, self.id_field = Path(data_file), fields, id_field
        self.records: list[dict[str, Any]] = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if not self.data_file.exists(): return []
        try:
            with self.data_file.open(encoding="utf-8") as file: return json.load(file)
        except (OSError, json.JSONDecodeError): return []

    def _save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as file: json.dump(self.records, file, indent=4)

    def clean(self, record: dict[str, Any]) -> dict[str, Any]:
        cleaned = {field: str(record.get(field, "")).strip() for field in self.fields}
        if any(not value for value in cleaned.values()): raise ValueError("Every field is required.")
        for field in ("quantity", "price"):
            if field in cleaned:
                try:
                    number = float(cleaned[field])
                    if number < 0: raise ValueError
                    cleaned[field] = int(number) if field == "quantity" else round(number, 2)
                except ValueError: raise ValueError(f"{field.title()} must be a positive number.") from None
        cleaned[self.id_field] = cleaned[self.id_field].upper()
        return cleaned

    def all(self): return sorted(self.records, key=lambda r: str(r[self.id_field]))
    def find(self, key): return next((r for r in self.records if str(r[self.id_field]).upper() == key.strip().upper()), None)
    def search(self, query):
        query = query.strip().casefold()
        return [r for r in self.all() if not query or any(query in str(v).casefold() for v in r.values())]
    def add(self, record):
        cleaned = self.clean(record)
        if self.find(cleaned[self.id_field]): raise ValueError("This ID already exists.")
        self.records.append(cleaned); self._save(); return cleaned
    def update(self, old_key, record):
        existing = self.find(old_key)
        if not existing: raise ValueError("Record was not found.")
        cleaned = self.clean(record); duplicate = self.find(cleaned[self.id_field])
        if duplicate and duplicate is not existing: raise ValueError("This ID already exists.")
        existing.update(cleaned); self._save(); return existing
    def delete(self, key):
        existing = self.find(key)
        if not existing: raise ValueError("Record was not found.")
        self.records.remove(existing); self._save()
