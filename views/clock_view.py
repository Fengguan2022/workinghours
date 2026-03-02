import customtkinter as ctk

import database


class ClockView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Back button
        back_btn = ctk.CTkButton(
            self, text="< Back", width=80, fg_color="transparent",
            text_color=("gray10", "gray90"), hover_color=("gray80", "gray30"),
            command=self.app.show_main_menu,
        )
        back_btn.pack(anchor="nw", padx=10, pady=10)

        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        self._show_pin_entry()

    def _show_pin_entry(self):
        for w in self.center.winfo_children():
            w.destroy()

        title = ctk.CTkLabel(
            self.center, text="Enter Your PIN",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(pady=(0, 20))

        self.pin_entry = ctk.CTkEntry(
            self.center, width=200, height=45, font=ctk.CTkFont(size=20),
            placeholder_text="4-digit PIN", show="*", justify="center",
        )
        self.pin_entry.pack(pady=10)
        self.pin_entry.bind("<Return>", lambda e: self._lookup_pin())
        self.pin_entry.focus()

        submit_btn = ctk.CTkButton(
            self.center, text="Submit", width=200, height=40,
            font=ctk.CTkFont(size=16), command=self._lookup_pin,
        )
        submit_btn.pack(pady=10)

        self.msg_label = ctk.CTkLabel(
            self.center, text="", font=ctk.CTkFont(size=14), text_color="red",
        )
        self.msg_label.pack(pady=5)

    def _lookup_pin(self):
        pin = self.pin_entry.get().strip()
        if not pin:
            self.msg_label.configure(text="Please enter your PIN.")
            return

        emp = database.get_employee_by_pin(pin)
        if emp is None:
            self.msg_label.configure(text="Invalid PIN. Please try again.")
            self.pin_entry.delete(0, "end")
            return

        self._show_clock_action(emp)

    def _show_clock_action(self, emp):
        for w in self.center.winfo_children():
            w.destroy()

        last_event = database.get_last_event(emp.id)
        is_clocked_in = last_event is not None and last_event.event_type == "IN"

        greeting = ctk.CTkLabel(
            self.center, text=f"Hello, {emp.name}!",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        greeting.pack(pady=(0, 10))

        if is_clocked_in:
            status_text = "Status: Clocked IN"
            status_color = "#2ecc71"
            btn_text = "Clock Out"
            event_type = "OUT"
        else:
            status_text = "Status: Clocked OUT"
            status_color = "#e74c3c"
            btn_text = "Clock In"
            event_type = "IN"

        status = ctk.CTkLabel(
            self.center, text=status_text,
            font=ctk.CTkFont(size=16), text_color=status_color,
        )
        status.pack(pady=5)

        # Show today's hours
        today_hours = database.calc_today_hours(emp.id)
        hours_label = ctk.CTkLabel(
            self.center, text=f"Today's hours: {today_hours:.2f} hrs",
            font=ctk.CTkFont(size=14),
        )
        hours_label.pack(pady=5)

        action_btn = ctk.CTkButton(
            self.center, text=btn_text, width=200, height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2ecc71" if event_type == "IN" else "#e74c3c",
            hover_color="#27ae60" if event_type == "IN" else "#c0392b",
            command=lambda: self._do_clock(emp, event_type),
        )
        action_btn.pack(pady=20)

        another_btn = ctk.CTkButton(
            self.center, text="Different Employee", width=160,
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            command=self._show_pin_entry,
        )
        another_btn.pack()

    def _do_clock(self, emp, event_type):
        database.clock_event(emp.id, event_type)
        self._show_confirmation(emp, event_type)

    def _show_confirmation(self, emp, event_type):
        for w in self.center.winfo_children():
            w.destroy()

        action = "clocked IN" if event_type == "IN" else "clocked OUT"
        msg = ctk.CTkLabel(
            self.center, text=f"{emp.name}\nSuccessfully {action}!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2ecc71" if event_type == "IN" else "#e74c3c",
        )
        msg.pack(pady=20)

        today_hours = database.calc_today_hours(emp.id)
        hours_label = ctk.CTkLabel(
            self.center, text=f"Today's total: {today_hours:.2f} hrs",
            font=ctk.CTkFont(size=16),
        )
        hours_label.pack(pady=5)

        done_btn = ctk.CTkButton(
            self.center, text="Done", width=200, height=40,
            font=ctk.CTkFont(size=16), command=self._show_pin_entry,
        )
        done_btn.pack(pady=20)
