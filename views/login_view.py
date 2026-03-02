import customtkinter as ctk

import database


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        back_btn = ctk.CTkButton(
            self, text="< Back", width=80, fg_color="transparent",
            text_color=("gray10", "gray90"), hover_color=("gray80", "gray30"),
            command=self.app.show_main_menu,
        )
        back_btn.pack(anchor="nw", padx=10, pady=10)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            center, text="Admin Login",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(
            center, width=250, height=40, font=ctk.CTkFont(size=16),
            placeholder_text="Username",
        )
        self.username_entry.pack(pady=8)
        self.username_entry.insert(0, "admin")

        self.password_entry = ctk.CTkEntry(
            center, width=250, height=40, font=ctk.CTkFont(size=16),
            placeholder_text="Password", show="*",
        )
        self.password_entry.pack(pady=8)
        self.password_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.focus()

        login_btn = ctk.CTkButton(
            center, text="Login", width=250, height=40,
            font=ctk.CTkFont(size=16), command=self._login,
        )
        login_btn.pack(pady=15)

        self.msg_label = ctk.CTkLabel(
            center, text="", font=ctk.CTkFont(size=14), text_color="red",
        )
        self.msg_label.pack()

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if database.verify_admin(username, password):
            self.app.show_admin_view()
        else:
            self.msg_label.configure(text="Invalid username or password.")
            self.password_entry.delete(0, "end")
