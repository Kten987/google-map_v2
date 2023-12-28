from botasaurus import request as rq, bt
from botasaurus.cache import DontCache
import requests
from time import sleep

FAILED_DUE_TO_CREDITS_EXHAUSTED = "FAILED_DUE_TO_CREDITS_EXHAUSTED"
FAILED_DUE_TO_NOT_SUBSCRIBED = "FAILED_DUE_TO_NOT_SUBSCRIBED"
FAILED_DUE_TO_UNKNOWN_ERROR = "FAILED_DUE_TO_UNKNOWN_ERROR"

def update_credits():
    """
    Update the credits used by incrementing the value stored in the local storage.

    This function retrieves the current value of 'credits_used' from the local storage,
    increments it by 1, and then updates the value in the local storage.

    Parameters:
        None

    Returns:
        None
    """
    credits_used = bt.LocalStorage.get_item("credits_used", 0)
    bt.LocalStorage.set_item("credits_used", credits_used + 1)

def do_request(data, retry_count=3):
    """
    Perform a request to scrape social details from a website.

    This function takes in the data containing the website URL, place ID, and API key.
    It sends a request to the website-contacts-scraper API to scrape the social details.
    If the request is successful, it updates the credits used and returns the scraped data.
    If the request fails due to credits exhaustion, rate limit, or other errors, it returns an error message.

    Parameters:
        data (dict): The data containing the website URL, place ID, and API key.
        retry_count (int): The number of retries allowed for the request. Default is 3.

    Returns:
        dict: The scraped social details or an error message.
    """
    place_id = data["place_id"]
    website = data["website"]
    key = data["key"]

    if retry_count == 0:
        print(f"Failed to get Social details for {website}, after 3 retries")
        return DontCache(None)

    url = "https://website-contacts-scraper.p.rapidapi.com/scrape-contacts"
    querystring = {"query": website, "match_email_domain": "false"}
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "website-contacts-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()
    if response.status_code == 200:
        update_credits()

        final = response_data.get('data', [None])[0]
        
        if "pinterest" not in final:
            final["pinterest"] = None

        final["phones"] = final["phone_numbers"]
        
        del final["phone_numbers"]
        del final["domain"]
        del final["query"]

        return {
            "place_id": place_id,
            "data": final,
            "error": None
        }
    else: 
        message = response_data.get("message", "")
        if "exceeded the MONTHLY quota" in message:
            return  DontCache({
                "place_id": place_id,
                "data":  None,
                "error":FAILED_DUE_TO_CREDITS_EXHAUSTED
            })
        elif "exceeded the rate limit per second for your plan" in message or "many requests" in message:
            sleep(2)
            return do_request(data, retry_count - 1)
        elif "You are not subscribed to this API." in message:
            return DontCache({
                "place_id": place_id,
                "data": None,
                "error": FAILED_DUE_TO_NOT_SUBSCRIBED
            })

        print(f"Error: {response.status_code}", response_data)
        return  DontCache({
            "place_id": place_id,
            "data":  None,
            "error":FAILED_DUE_TO_UNKNOWN_ERROR
        })

@rq(
    close_on_crash=True,
    output=None,
)
def perform_scrape_social(reqs, data):
    """
    Perform the scraping of social details using the 'do_request' function.

    This function is decorated with the 'rq' decorator from the 'botasaurus' library.
    It takes in the 'reqs' and 'data' parameters and calls the 'do_request' function to perform the scraping.
    The result is returned without any output.

    Parameters:
        reqs: The request object.
        data: The data containing the website URL, place ID, and API key.

    Returns:
        None
    """
    return do_request(data)

@rq(
    close_on_crash=True,
    output=None,
)
def perform_scrape_social_pro(reqs, data):
    """
    Perform the scraping of social details using the 'do_request' function.

    This function is decorated with the 'rq' decorator from the 'botasaurus' library.
    It takes in the 'reqs' and 'data' parameters and calls the 'do_request' function to perform the scraping.
    The result is returned without any output.

    Parameters:
        reqs: The request object.
        data: The data containing the website URL, place ID, and API key.

    Returns:
        None
    """
    return do_request(data)

def is_free():
    """
    Check if the credits used is within the free limit.

    This function checks the value of 'credits_used' from the local storage.
    If the value is less than the free credits plus 10, it returns True.
    Otherwise, it returns False.

    Parameters:
        None

    Returns:
        bool: True if within the free limit, False otherwise.
    """
    FREE_CREDITS_PLUS_10 = 60
    credits_used = bt.LocalStorage.get_item("credits_used", 0)
    return credits_used < FREE_CREDITS_PLUS_10

def scrape_social(social_data, cache):
    """
    Scrape social details based on the provided data.

    This function takes in the social data and cache parameters.
    It checks if the scraping should be performed using the free or pro version.
    It then calls the respective 'perform_scrape_social' function to perform the scraping.

    Parameters:
        social_data (dict): The data containing the website URL, place ID, and API key.
        cache: The cache object.

    Returns:
        The result of the scraping.
    """
    free = is_free()
    if free:
        return perform_scrape_social(social_data, cache=cache)
    else:
        return perform_scrape_social_pro(social_data, cache=cache)
