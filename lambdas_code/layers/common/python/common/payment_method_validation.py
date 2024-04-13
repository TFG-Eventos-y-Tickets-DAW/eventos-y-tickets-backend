from common.constants.payment_methods import FREE, PAYPAL, SUPPORTED_PAYMENT_METHODS


def validate_payment_method(payment_method, payment_method_details):
    if payment_method not in SUPPORTED_PAYMENT_METHODS:
        return False, "The payment method provided is not supported."

    # No additional validation required for PayPal or FREE orders.
    if payment_method == PAYPAL or payment_method == FREE:
        return True, ""

    # If we reach here, then the payment method is CREDIT
    card_number = payment_method_details.get("cardNumber")
    expiry = payment_method_details.get("expiry")
    cvv = payment_method_details.get("cvv")
    cardholder = payment_method_details.get("cardholderName")

    if not card_number or not expiry or not cvv or not cardholder:
        return (
            False,
            "Please provide the necessary card details: `cardNumber`, `expiry`, `cvv`, `cardholderName`.",
        )

    if not is_luhn_valid(card_number):
        return False, "The card numbers doesn't seem to be right."

    return True, ""


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0
