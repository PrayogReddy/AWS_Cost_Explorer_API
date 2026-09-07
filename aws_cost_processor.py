from collections import defaultdict


def process_cost_data(response):
    """
    Process AWS Cost Explorer response.

    Separates:
    - Usage
    - Credit
    - Other record types, such as Tax and Refund

    Also calculates:
    - service-wise and daily totals
    - total usage
    - total credit
    - usage plus credits
    - other charges
    - total AWS cost
    """

    service_usage = defaultdict(float)
    service_credit = defaultdict(float)
    service_total = defaultdict(float)
    other_record_types = defaultdict(float)

    daily_usage = defaultdict(float)
    daily_credit = defaultdict(float)
    daily_total = defaultdict(float)

    currency = "USD"

    for day in response.get("ResultsByTime", []):

        date = day["TimePeriod"]["Start"]

        for group in day.get("Groups", []):

            service = group["Keys"][0]
            record_type = group["Keys"][1]

            cost = group["Metrics"]["UnblendedCost"]

            amount = float(cost["Amount"])
            currency = cost["Unit"]

            # Total cost includes every Cost Explorer record type,
            # including usage, credits, taxes, and refunds.
            service_total[service] += amount
            daily_total[date] += amount

            record_type = record_type.lower()

            if record_type == "usage":

                service_usage[service] += amount
                daily_usage[date] += amount

            elif record_type == "credit":

                service_credit[service] += amount
                daily_credit[date] += amount

            else:
                other_record_types[group["Keys"][1]] += amount

    total_usage = sum(
        service_usage.values()
    )

    total_credit = sum(
        service_credit.values()
    )

    total_cost = sum(
        service_total.values()
    )

    total_other = sum(
        other_record_types.values()
    )

    # Credits are normally negative.
    net_cost = total_usage + total_credit

    return {
        "service_usage": service_usage,
        "service_credit": service_credit,
        "service_total": service_total,
        "daily_usage": daily_usage,
        "daily_credit": daily_credit,
        "daily_total": daily_total,
        "other_record_types": other_record_types,
        "total_usage": total_usage,
        "total_credit": total_credit,
        "net_cost": net_cost,
        "total_other": total_other,
        "total_cost": total_cost,
        "currency": currency
    }
