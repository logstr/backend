def cents_to_dollars(cents):
    """
    Convert cents to dollar amount
    :param cents: Amount in cents
    :type cents: int
    :return: float
    """
    return round(cents / 100.0, 2)

def dollars_to_cents(dollars):
    """
    Convert dollar amount to cents
    :param cents: Amount in cents
    :type cents: int
    :return: float
    """
    return int(dollars * 100)