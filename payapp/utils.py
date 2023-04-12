
def convert_currency(currency1, currency2, amount):
    # Define conversion rates
    conversion_rates = {
        'USD': {'EURO': 0.83, 'GBP': 0.72},
        'EURO': {'USD': 1.21, 'GBP': 0.87},
        'GBP': {'USD': 1.39, 'EURO': 1.15}
    }

    # Check if both currencies are valid and conversion rate is available
    if currency1 in conversion_rates and currency2 in conversion_rates[currency1]:
        # Convert currency
        converted_amount = amount * conversion_rates[currency1][currency2]
        return converted_amount
    else:
        return None


def convert_to_float(str_value):
    try:
        float_value = float(str_value)
        return float_value
    except ValueError:
        return None
