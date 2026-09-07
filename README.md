# AWS Cost Explorer API — Billing Report Generator

A Python tool that pulls AWS billing data from the **Cost Explorer API** (via Boto3)
for a chosen date range and generates a formatted **PDF billing report**, with an
optional breakdown of usage vs. credits vs. taxes/refunds.

## Features

- Prompts for a billing period (`DD-MM-YYYY` format) with date validation
- Retrieves daily cost data grouped by **service** and **record type**
  (Usage, Credit, Tax, Refund, etc.) via `GetCostAndUsage`
- Two reporting modes:
  - **Usage only** — just the usage cost, no credits/taxes/refunds
  - **With credits** — full breakdown: usage, credits, usage+credits (net),
    other charges, and total AWS cost
- Console summary printed immediately after retrieval
- PDF report with:
  1. Billing period
  2. Cost summary (total/usage/credits/net, depending on mode)
  3. Service-wise cost breakdown
  4. Daily cost breakdown
  5. Currency
  6. Other charges (taxes, refunds, etc.) when credit mode is on
- Handles Cost Explorer pagination so no service/date is silently dropped
- AWS credentials are never hardcoded — resolved via Boto3's standard
  credential chain (`aws configure`, environment variables, or an IAM role)

## Project structure

```
.
├── main.py                   # Entry point — orchestrates the whole flow
├── utils.py                  # Date input/validation, mode prompt, money formatting
├── aws_cost_explorer.py      # Boto3 Cost Explorer client + paginated data retrieval
├── aws_cost_processor.py     # Splits raw CE data into usage/credit/other, computes totals
├── pdf_report_generator.py   # Builds the PDF report with reportlab
├── requirements.txt
└── reports/                  # Generated PDF reports land here
```

## Requirements

- Python 3.8+
- An AWS account with Cost Explorer enabled (Billing and Cost Management
  console → Cost Explorer — this is a one-time, free toggle)
- An IAM user/role with the `ce:GetCostAndUsage` permission

## Installation

```bash
git clone https://github.com/PrayogReddy/AWS_Cost_Explorer_API.git
cd AWS_Cost_Explorer_API
pip install -r requirements.txt
```

## AWS credentials

Credentials are **never** stored in the code. Set them up using any standard
Boto3 method, for example:

```bash
aws configure
```

This writes to `~/.aws/credentials` and `~/.aws/config`, which Boto3 reads
automatically. Environment variables (`AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`) or an IAM role (EC2/ECS/Lambda) also work with no
code changes.

## Usage

```bash
python main.py
```

You'll be prompted for:

1. **Start date** — `DD-MM-YYYY`
2. **End date** — `DD-MM-YYYY`
3. **Include credit data in the report? (y/n)**
   - `n` → usage-only report (simpler, just the usage cost)
   - `y` → full report with credits, net cost, and other charges broken out

Example:

```
AWS Billing Report Generator
------------------------------
Enter start date (DD-MM-YYYY): 01-08-2026
Enter end date (DD-MM-YYYY): 31-08-2026
Include credit data in the report? (y/n): y

Retrieving AWS billing information...

=======================================================
             AWS BILLING SUMMARY
=======================================================
Billing Period : 01-08-2026 to 31-08-2026
Usage Cost     : USD 0.70
Total AWS Cost: USD 0.74
Credits        : USD 0.00
Usage + Credits: USD 0.70
=======================================================

PDF generated successfully.
Location: reports/aws_billing_2026-08-01_to_2026-08-31_with_credits_20260903_140501_123456.pdf
```

The PDF is saved under `reports/`, named with the billing period, report
mode, and a timestamp so repeated runs never overwrite each other.

## Notes on the numbers

- All figures come from Cost Explorer's `UnblendedCost` metric, grouped by
  `SERVICE` and `RECORD_TYPE`.
- **Usage** = cost from actual resource usage.
- **Credit** = promotional/support credits applied (normally shown as a
  negative amount).
- **Total AWS Cost** = usage + credits + taxes + refunds + any other record
  type Cost Explorer returns — this is the true bottom-line figure.
- Small recurring charges (e.g. a Route 53 hosted zone fee) can be
  recognized by AWS on a single date rather than spread evenly across the
  billing period — a $0 day next to a higher one isn't a bug.
- The Cost Explorer API costs $0.01 per paginated request, separate from
  the AWS usage it's reporting on.

## Limitations / possible extensions

- Dates are entered manually each run; no `--start`/`--end` CLI flags yet.
- No support for `AmortizedCost` (which spreads recurring fees evenly
  across days) — currently `UnblendedCost` only.
- No multi-account / consolidated billing support.
