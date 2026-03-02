import customtkinter as ctk

from views.clock_view import ClockView
from views.login_view import LoginView
from views.admin_view import AdminView


class WorkingHoursApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Working Hours Tracker")
        self.geometry("800x600")
        self.minsize(700, 500)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.current_view = None
        self.show_main_menu()

    def clear_view(self):
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

    def show_main_menu(self):
        self.clear_view()
        self.current_view = MainMenuView(self.container, self)
        self.current_view.pack(fill="both", expand=True)

    def show_clock_view(self):
        self.clear_view()
        self.current_view = ClockView(self.container, self)
        self.current_view.pack(fill="both", expand=True)

    def show_login_view(self):
        self.clear_view()
        self.current_view = LoginView(self.container, self)
        self.current_view.pack(fill="both", expand=True)

    def show_admin_view(self):
        self.clear_view()
        self.current_view = AdminView(self.container, self)
        self.current_view.pack(fill="both", expand=True)


class MainMenuView(ctk.CTkFrame):
    def __init__(self, parent, app: WorkingHoursApp):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Center content
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            center, text="Working Hours Tracker",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(pady=(0, 40))

        clock_btn = ctk.CTkButton(
            center, text="Clock In / Out", width=250, height=50,
            font=ctk.CTkFont(size=18),
            command=self.app.show_clock_view,
        )
        clock_btn.pack(pady=10)

        admin_btn = ctk.CTkButton(
            center, text="Admin Login", width=250, height=50,
            font=ctk.CTkFont(size=18),
            fg_color="#555555", hover_color="#333333",
            command=self.app.show_login_view,
        )
        admin_btn.pack(pady=10)
