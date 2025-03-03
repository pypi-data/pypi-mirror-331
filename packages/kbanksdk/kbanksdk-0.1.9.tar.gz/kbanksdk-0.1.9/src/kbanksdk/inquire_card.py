import requests


def inquire_card(charge_id: str, api_key: str) -> dict | None:
    """
    Inquire about a card transaction using the K+ API

    Args:
        charge_id: The charge ID to inquire about

    Returns:
        dict: API response if successful, None if error occurs
    """
    if not charge_id:
        raise ValueError("Please enter a Charge ID")

    url = f"https://dev-kpaymentgateway-services.kasikornbank.com/card/v2/charge/{charge_id}"
    headers = {"x-api-key": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        error_msg = f"Failed to inquire transaction: {str(e)}"

    print(f"Error: {error_msg}")
    return None


if __name__ == "__main__":
    try:
        # Test with sample charge ID
        test_id = "chrg_test_2221188e085233bf14e569f6ef202e89c364d"
        print(f"Testing inquiry for charge ID: {test_id}")
        result = inquire_card(
            test_id, "skey_test_22211z50DsvnHyry6xCGGqSzNqUFfq8Cyg2P1"
        )

        if result:
            print("Inquiry successful:")
            print(result)
        else:
            print("Inquiry returned no results")
    except Exception as e:
        print(f"Test failed: {str(e)}")
