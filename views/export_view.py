import customtkinter as ctk
from datetime import date, timedelta
from tkinter import filedialog

import database
from export import export_to_excel


class ExportView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(self, text="Export to Excel", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=10)

        # Date range
        date_row = ctk.CTkFrame(self, fg_color="transparent")
        date_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(date_row, text="From:").pack(side="left", padx=(0, 5))
        self.from_entry = ctk.CTkEntry(date_row, width=120, placeholder_text="YYYY-MM-DD")
        self.from_entry.pack(side="left", padx=(0, 15))
        self.from_entry.insert(0, (date.today().replace(day=1)).isoformat())

        ctk.CTkLabel(date_row, text="To:").pack(side="left", padx=(0, 5))
        self.to_entry = ctk.CTkEntry(date_row, width=120, placeholder_text="YYYY-MM-DD")
        self.to_entry.pack(side="left", padx=(0, 15))
        self.to_entry.insert(0, date.today().isoformat())

        # Employee filter
        emp_row = ctk.CTkFrame(self, fg_color="transparent")
        emp_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(emp_row, text="Employee:").pack(side="left", padx=(0, 5))
        self.emp_var = ctk.StringVar(value="All")
        emps = database.get_all_employees()
        names = ["All"] + [e.name for e in emps]
        self._emp_map = {e.name: e.id for e in emps}
        self.emp_menu = ctk.CTkOptionMenu(emp_row, variable=self.emp_var, values=names, width=200)
        self.emp_menu.pack(side="left")

        # Export button
        ctk.CTkButton(
            self, text="Export to Excel", width=200, height=40,
            font=ctk.CTkFont(size=15), command=self._do_export,
        ).pack(padx=10, pady=20)

        self.msg = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13))
        self.msg.pack(padx=10)

    def _do_export(self):
        start = self.from_entry.get().strip()
        end = self.to_entry.get().strip()
        emp_name = self.emp_var.get()
        emp_id = self._emp_map.get(emp_name)

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"working_hours_{start}_to_{end}.xlsx",
        )
        if not filepath:
            return

        try:
            export_to_excel(filepath, start, end, emp_id)
            self.msg.configure(text=f"Exported to {filepath}", text_color="green")
        except Exception as e:
            self.msg.configure(text=f"Error: {e}", text_color="red")
