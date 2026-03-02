import database
from app import WorkingHoursApp


def main():
    database.init_db()
    app = WorkingHoursApp()
    app.mainloop()


if __name__ == "__main__":
    main()
