import boto3
from datetime import timedelta
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
)


def format_aws_error(error):
    """Return an actionable message for common AWS SDK errors."""

    if isinstance(error, NoCredentialsError):
        return (
            "AWS credentials were not found. Configure them with "
            "'aws configure', an AWS profile, environment variables, "
            "or an IAM role."
        )

    if isinstance(error, PartialCredentialsError):
        return (
            "AWS credentials are incomplete. Check the selected AWS "
            "profile or environment variables."
        )

    if isinstance(error, EndpointConnectionError):
        return (
            "Could not connect to AWS Cost Explorer. Check your internet "
            "connection, proxy settings, and AWS endpoint access."
        )

    if isinstance(error, ClientError):
        details = error.response.get("Error", {})
        code = details.get("Code", "Unknown AWS error")
        message = details.get("Message", "No additional details provided.")

        if code in {"AccessDeniedException", "UnauthorizedException"}:
            return (
                "Access to Cost Explorer was denied. The AWS user or role "
                "needs the ce:GetCostAndUsage permission."
            )

        return f"AWS Cost Explorer returned {code}: {message}"

    return str(error)


def get_aws_cost_data(start_dt, end_dt):
    """
    Retrieve daily AWS billing data from Cost Explorer.
    """

    # AWS Cost Explorer uses YYYY-MM-DD
    start = start_dt.strftime("%Y-%m-%d")

    # End date is exclusive, so add one day
    api_end = (
        end_dt + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    ce = boto3.client(
        "ce",
        region_name="us-east-1"
    )

    print("\nRetrieving AWS billing information...")

    request = {
        "TimePeriod": {
            "Start": start,
            "End": api_end
        },
        "Granularity": "DAILY",
        "Metrics": ["UnblendedCost"],
        "GroupBy": [
            {
                "Type": "DIMENSION",
                "Key": "SERVICE"
            },
            {
                "Type": "DIMENSION",
                "Key": "RECORD_TYPE"
            }
        ]
    }

    # Cost Explorer can split grouped data across multiple pages. Merge
    # groups by date so no service or record type is omitted from the report.
    results_by_date = {}
    next_page_token = None

    while True:
        if next_page_token:
            request["NextPageToken"] = next_page_token

        response = ce.get_cost_and_usage(**request)

        for day in response.get("ResultsByTime", []):
            date = day["TimePeriod"]["Start"]
            combined_day = results_by_date.setdefault(
                date,
                {
                    "TimePeriod": day["TimePeriod"],
                    "Groups": []
                }
            )
            combined_day["Groups"].extend(day.get("Groups", []))

        next_page_token = response.get("NextPageToken")
        if not next_page_token:
            break

    return {
        "ResultsByTime": [
            results_by_date[date]
            for date in sorted(results_by_date)
        ]
    }
