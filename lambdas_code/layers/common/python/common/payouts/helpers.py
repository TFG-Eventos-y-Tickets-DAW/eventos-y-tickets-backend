def calculate_payout_fee_by_total_amount(amount):
    if amount <= 100:
        return round(amount * 0.05, 2)

    if amount <= 500:
        return round(amount * 0.10, 2)

    if amount <= 1000:
        return round(amount * 0.15, 2)

    return round(amount * 0.20, 2)
