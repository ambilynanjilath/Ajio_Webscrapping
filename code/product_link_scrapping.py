import requests
import csv

# Base API URL
api_url_template = (
    "https://www.ajio.com/api/category/83?"
    "currentPage={page}&pageSize=45&format=json&query=%3Arelevance&sortBy=relevance"
    "&curated=true&curatedid=clothing-4461-75481&gridColumns=3&facets=&advfilter=true"
    "&platform=Desktop&showAdsOnNextPage=true&is_ads_enable_plp=true&displayRatings=true"
)

# Base URL for constructing full product URLs
base_url = "https://www.ajio.com"

def extract_product_urls(api_url):
    """
    Extracts product URLs from the given API URL.

    This function sends a GET request to the provided API URL to retrieve product data in JSON format.
    It then parses the JSON response to extract the URLs of the products. Each URL is constructed 
    by appending the path from the API response to a base URL. If the API request fails, it prints an
    error message and returns an empty list.

    Args:
        api_url (str): The full API URL to request product data from.

    Returns:
        list: A list of full product URLs extracted from the API response. Each URL is constructed
              by appending the product path obtained from the API to the base URL. If the API request
              fails, an empty list is returned.

    Method Steps:
    1. Send a GET request to the specified `api_url` using the `requests.get` method.
    2. Check if the HTTP response status code is 200 (indicating success).
    3. If the request is successful, parse the JSON content from the response using `response.json()`.
    4. Initialize an empty list `product_urls` to store the full product URLs.
    5. Iterate through the list of products obtained from the JSON response.
    6. For each product, extract the product path URL using `product.get("url")`.
    7. If the product path URL is valid, concatenate it with the `base_url` to form the full URL.
    8. Append the full URL to the `product_urls` list.
    9. Return the list of full product URLs.
    10. If the HTTP response status code is not 200, print an error message indicating the failure 
        and return an empty list.
    """

    # Send a GET request to the API endpoint
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract product URLs
        product_urls = []
        for product in data.get("products", []):
            product_url = product.get("url")
            if product_url:
                # Construct the full URL and add to the list
                full_url = base_url + product_url
                product_urls.append(full_url)

        return product_urls
    else:
        print(f"Failed to retrieve data from {api_url}")
        return []

# Extract URLs from pages 1 to 6
all_product_urls = []
for page in range(1, 7):
    api_url = api_url_template.format(page=page)
    product_urls = extract_product_urls(api_url)
    all_product_urls.extend(product_urls)

# Save the extracted URLs to a CSV file
csv_file = "/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/product_urls.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Product URL"])
    for url in all_product_urls:
        writer.writerow([url])

print(f"Extracted URLs have been saved to {csv_file}")
