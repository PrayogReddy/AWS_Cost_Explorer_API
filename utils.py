from datetime import datetime


def get_billing_dates():
    """
    Get billing dates from the user in DD-MM-YYYY format.
    """

    while True:
        try:
            start = input("Enter start date (DD-MM-YYYY): ")
            end = input("Enter end date (DD-MM-YYYY): ")

            start_dt = datetime.strptime(start, "%d-%m-%Y")
            end_dt = datetime.strptime(end, "%d-%m-%Y")

            if end_dt < start_dt:
                print("End date cannot be before start date.")
                continue

            return start, end, start_dt, end_dt

        except ValueError:
            print("Invalid date. Please use DD-MM-YYYY.")


def get_report_mode():
    """Ask whether the report should include credits and total-cost detail."""

    while True:
        mode = input(
            "Include credit data in the report? (y/n): "
        ).strip().lower()

        if mode in ("y", "yes"):
            return True

        if mode in ("n", "no"):
            return False

        print("Please enter y or n.")


def format_money(value):
    """
    Format cost values to two decimal places.
    """

    if abs(value) < 0.005:
        value = 0

    return f"{value:.2f}"
