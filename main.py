from datetime import datetime

from utils import get_billing_dates, get_report_mode, format_money
from aws_cost_explorer import get_aws_cost_data, format_aws_error
from aws_cost_processor import process_cost_data
from pdf_report_generator import create_pdf_report


def display_summary(start, end, billing_data, include_credits):
    """
    Display only the important billing information.
    """

    currency = billing_data["currency"]

    usage = billing_data["total_usage"]

    print("\n" + "=" * 55)
    print("             AWS BILLING SUMMARY")
    print("=" * 55)

    print(f"Billing Period : {start} to {end}")
    print(f"Usage Cost     : {currency} {format_money(usage)}")

    if include_credits:
        credit = billing_data["total_credit"]
        net = billing_data["net_cost"]
        total = billing_data["total_cost"]
        print(f"Total AWS Cost: {currency} {format_money(total)}")
        print(f"Credits        : {currency} {format_money(credit)}")
        print(f"Usage + Credits: {currency} {format_money(net)}")

    print("=" * 55)


def main():

    print("\nAWS Billing Report Generator")
    print("-" * 30)

    # Get dates
    start, end, start_dt, end_dt = get_billing_dates()
    include_credits = get_report_mode()

    # Retrieve AWS data
    try:
        response = get_aws_cost_data(
            start_dt,
            end_dt
        )

    except Exception as e:
        print("\nFailed to retrieve AWS billing information.")
        print(f"Error: {format_aws_error(e)}")
        return

    # Process data
    billing_data = process_cost_data(response)

    # Display important information only
    display_summary(
        start,
        end,
        billing_data,
        include_credits
    )

    # Generate PDF
    report_mode = "with_credits" if include_credits else "usage_only"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    pdf_file = (
        "reports/"
        f"aws_billing_{start_dt:%Y-%m-%d}_to_{end_dt:%Y-%m-%d}_"
        f"{report_mode}_{timestamp}.pdf"
    )

    try:
        create_pdf_report(
            start,
            end,
            billing_data,
            pdf_file,
            include_credits
        )

        print("\nPDF generated successfully.")
        print(f"Location: {pdf_file}")

    except Exception as e:
        print("\nFailed to generate PDF.")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
