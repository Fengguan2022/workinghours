import customtkinter as ctk
from datetime import date, timedelta

import database
from views.export_view import ExportView


class AdminView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=5)

        title = ctk.CTkLabel(
            top, text="Admin Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.pack(side="left", padx=10)

        logout_btn = ctk.CTkButton(
            top, text="Logout", width=80, fg_color="#e74c3c",
            hover_color="#c0392b", command=self.app.show_main_menu,
        )
        logout_btn.pack(side="right", padx=10)

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_team = self.tabview.add("Team Members")
        self.tab_records = self.tabview.add("Time Records")
        self.tab_export = self.tabview.add("Export")
        self.tab_settings = self.tabview.add("Settings")

        self._build_team_tab()
        self._build_records_tab()
        self._build_export_tab()
        self._build_settings_tab()

    # ===== Team Members Tab =====
    def _build_team_tab(self):
        # Add employee form
        form = ctk.CTkFrame(self.tab_team)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Add Employee", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row, text="Name:").pack(side="left", padx=(0, 5))
        self.emp_name_entry = ctk.CTkEntry(row, width=200)
        self.emp_name_entry.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row, text="PIN (4 digits):").pack(side="left", padx=(0, 5))
        self.emp_pin_entry = ctk.CTkEntry(row, width=100)
        self.emp_pin_entry.pack(side="left", padx=(0, 15))

        add_btn = ctk.CTkButton(row, text="Add", width=80, command=self._add_employee)
        add_btn.pack(side="left")

        self.team_msg = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=13))
        self.team_msg.pack(anchor="w", padx=10, pady=(0, 10))

        # Employee list
        self.team_list_frame = ctk.CTkScrollableFrame(self.tab_team)
        self.team_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._refresh_team_list()

    def _add_employee(self):
        name = self.emp_name_entry.get().strip()
        pin = self.emp_pin_entry.get().strip()
        if not name:
            self.team_msg.configure(text="Name is required.", text_color="red")
            return
        if not pin or len(pin) != 4 or not pin.isdigit():
            self.team_msg.configure(text="PIN must be exactly 4 digits.", text_color="red")
            return
        # Check unique PIN
        existing = database.get_employee_by_pin(pin)
        if existing:
            self.team_msg.configure(text=f"PIN already used by {existing.name}.", text_color="red")
            return
        database.add_employee(name, pin)
        self.emp_name_entry.delete(0, "end")
        self.emp_pin_entry.delete(0, "end")
        self.team_msg.configure(text=f"Added {name}.", text_color="green")
        self._refresh_team_list()

    def _refresh_team_list(self):
        for w in self.team_list_frame.winfo_children():
            w.destroy()

        employees = database.get_all_employees(include_inactive=True)
        if not employees:
            ctk.CTkLabel(self.team_list_frame, text="No employees yet.").pack(pady=20)
            return

        # Header
        header = ctk.CTkFrame(self.team_list_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))
        for text, w in [("Name", 200), ("PIN", 80), ("Status", 80), ("Actions", 200)]:
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(weight="bold"), width=w).pack(side="left", padx=5)

        for emp in employees:
            row = ctk.CTkFrame(self.team_list_frame, fg_color=("gray92", "gray17"))
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=emp.name, width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=emp.pin, width=80).pack(side="left", padx=5)
            status_text = "Active" if emp.active else "Inactive"
            status_color = "green" if emp.active else "red"
            ctk.CTkLabel(row, text=status_text, width=80, text_color=status_color).pack(side="left", padx=5)

            if emp.active:
                ctk.CTkButton(
                    row, text="Deactivate", width=90, fg_color="#e67e22", hover_color="#d35400",
                    command=lambda eid=emp.id: self._toggle_employee(eid, False),
                ).pack(side="left", padx=3)
            else:
                ctk.CTkButton(
                    row, text="Activate", width=90, fg_color="#2ecc71", hover_color="#27ae60",
                    command=lambda eid=emp.id: self._toggle_employee(eid, True),
                ).pack(side="left", padx=3)

            ctk.CTkButton(
                row, text="Edit", width=60,
                command=lambda eid=emp.id: self._edit_employee_dialog(eid),
            ).pack(side="left", padx=3)

    def _toggle_employee(self, emp_id, activate):
        if activate:
            database.activate_employee(emp_id)
        else:
            database.deactivate_employee(emp_id)
        self._refresh_team_list()

    def _edit_employee_dialog(self, emp_id):
        emp = database.get_employee_by_id(emp_id)
        if not emp:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Employee")
        dialog.geometry("350x220")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Edit Employee", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ctk.CTkLabel(dialog, text="Name:").pack(anchor="w", padx=20)
        name_entry = ctk.CTkEntry(dialog, width=250)
        name_entry.pack(padx=20, pady=(0, 10))
        name_entry.insert(0, emp.name)

        ctk.CTkLabel(dialog, text="PIN (4 digits):").pack(anchor="w", padx=20)
        pin_entry = ctk.CTkEntry(dialog, width=250)
        pin_entry.pack(padx=20, pady=(0, 10))
        pin_entry.insert(0, emp.pin)

        msg = ctk.CTkLabel(dialog, text="", text_color="red")
        msg.pack()

        def save():
            new_name = name_entry.get().strip()
            new_pin = pin_entry.get().strip()
            if not new_name:
                msg.configure(text="Name required.")
                return
            if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
                msg.configure(text="PIN must be 4 digits.")
                return
            # Check PIN unique (allow same if unchanged)
            existing = database.get_employee_by_pin(new_pin)
            if existing and existing.id != emp_id:
                msg.configure(text=f"PIN used by {existing.name}.")
                return
            database.update_employee(emp_id, new_name, new_pin)
            dialog.destroy()
            self._refresh_team_list()

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    # ===== Time Records Tab =====
    def _build_records_tab(self):
        filters = ctk.CTkFrame(self.tab_records, fg_color="transparent")
        filters.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(filters, text="Employee:").pack(side="left", padx=(0, 5))
        self.record_emp_var = ctk.StringVar(value="All")
        self.record_emp_menu = ctk.CTkOptionMenu(filters, variable=self.record_emp_var, values=["All"], width=180)
        self.record_emp_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(filters, text="From:").pack(side="left", padx=(0, 5))
        self.record_from = ctk.CTkEntry(filters, width=110, placeholder_text="YYYY-MM-DD")
        self.record_from.pack(side="left", padx=(0, 15))
        self.record_from.insert(0, (date.today() - timedelta(days=30)).isoformat())

        ctk.CTkLabel(filters, text="To:").pack(side="left", padx=(0, 5))
        self.record_to = ctk.CTkEntry(filters, width=110, placeholder_text="YYYY-MM-DD")
        self.record_to.pack(side="left", padx=(0, 15))
        self.record_to.insert(0, date.today().isoformat())

        ctk.CTkButton(filters, text="Search", width=80, command=self._search_records).pack(side="left")

        self.records_frame = ctk.CTkScrollableFrame(self.tab_records)
        self.records_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._refresh_employee_menu()
        self._search_records()

    def _refresh_employee_menu(self):
        emps = database.get_all_employees()
        names = ["All"] + [e.name for e in emps]
        self.record_emp_menu.configure(values=names)
        self._emp_map = {e.name: e.id for e in emps}

    def _search_records(self):
        for w in self.records_frame.winfo_children():
            w.destroy()

        self._refresh_employee_menu()

        start = self.record_from.get().strip()
        end = self.record_to.get().strip()
        emp_name = self.record_emp_var.get()
        emp_id = self._emp_map.get(emp_name)

        entries = database.get_entries_in_range(start, end, emp_id)

        if not entries:
            ctk.CTkLabel(self.records_frame, text="No records found.").pack(pady=20)
            return

        # Header
        header = ctk.CTkFrame(self.records_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))
        for text, w in [("Employee", 180), ("Event", 60), ("Timestamp", 180), ("", 80)]:
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(weight="bold"), width=w).pack(side="left", padx=5)

        emp_cache = {}
        for entry in entries:
            if entry.employee_id not in emp_cache:
                e = database.get_employee_by_id(entry.employee_id)
                emp_cache[entry.employee_id] = e.name if e else "Unknown"

            row = ctk.CTkFrame(self.records_frame, fg_color=("gray92", "gray17"))
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=emp_cache[entry.employee_id], width=180, anchor="w").pack(side="left", padx=5)
            color = "#2ecc71" if entry.event_type == "IN" else "#e74c3c"
            ctk.CTkLabel(row, text=entry.event_type, width=60, text_color=color,
                         font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=entry.timestamp, width=180).pack(side="left", padx=5)
            ctk.CTkButton(
                row, text="Delete", width=70, fg_color="#e74c3c", hover_color="#c0392b",
                command=lambda eid=entry.id: self._delete_entry(eid),
            ).pack(side="left", padx=5)

    def _delete_entry(self, entry_id):
        database.delete_time_entry(entry_id)
        self._search_records()

    # ===== Export Tab =====
    def _build_export_tab(self):
        ExportView(self.tab_export).pack(fill="both", expand=True)

    # ===== Settings Tab =====
    def _build_settings_tab(self):
        frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Change password
        ctk.CTkLabel(frame, text="Change Admin Password", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        pw_row = ctk.CTkFrame(frame, fg_color="transparent")
        pw_row.pack(fill="x", pady=5)

        ctk.CTkLabel(pw_row, text="New Password:").pack(side="left", padx=(0, 5))
        self.new_pw_entry = ctk.CTkEntry(pw_row, width=200, show="*")
        self.new_pw_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(pw_row, text="Change", width=80, command=self._change_password).pack(side="left")

        self.pw_msg = ctk.CTkLabel(frame, text="")
        self.pw_msg.pack(anchor="w", pady=5)

        # Overtime threshold
        ctk.CTkLabel(frame, text="Overtime Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(30, 10))

        ot_row = ctk.CTkFrame(frame, fg_color="transparent")
        ot_row.pack(fill="x", pady=5)

        ctk.CTkLabel(ot_row, text="Overtime threshold (hours/day):").pack(side="left", padx=(0, 5))
        self.ot_entry = ctk.CTkEntry(ot_row, width=80)
        self.ot_entry.pack(side="left", padx=(0, 10))
        self.ot_entry.insert(0, str(database.get_overtime_threshold()))

        ctk.CTkButton(ot_row, text="Save", width=80, command=self._save_overtime).pack(side="left")

        self.ot_msg = ctk.CTkLabel(frame, text="")
        self.ot_msg.pack(anchor="w", pady=5)

    def _change_password(self):
        new_pw = self.new_pw_entry.get()
        if len(new_pw) < 4:
            self.pw_msg.configure(text="Password must be at least 4 characters.", text_color="red")
            return
        database.change_admin_password("admin", new_pw)
        self.new_pw_entry.delete(0, "end")
        self.pw_msg.configure(text="Password changed successfully.", text_color="green")

    def _save_overtime(self):
        try:
            hours = float(self.ot_entry.get())
            if hours <= 0:
                raise ValueError
        except ValueError:
            self.ot_msg.configure(text="Enter a valid number of hours.", text_color="red")
            return
        database.set_overtime_threshold(hours)
        self.ot_msg.configure(text="Overtime threshold saved.", text_color="green")
