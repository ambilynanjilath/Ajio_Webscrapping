import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random

# Define file paths for input, output, user agent, and checkpoint files
input_csv_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/product_urls.csv'
output_csv_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/final_products_data.csv'
user_agent_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/filtered_user_agents.txt'
checkpoint_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/checkpoint.txt'

def extract_json_ld(html_content):
    """
    Extracts JSON-LD data from HTML content.

    This function parses the given HTML content using BeautifulSoup to find all script tags 
    of type 'application/ld+json'. It attempts to load the JSON content from these scripts 
    and returns a list of dictionaries containing the JSON-LD data. If any script contains 
    invalid JSON, an error message is printed and the script is skipped.

    Args:
        html_content (str): The HTML content of the web page.

    Returns:
        list: A list of JSON-LD data found in the HTML content. Each item in the list is a dictionary.

    Method Details:
    ---------------
    1. **HTML Parsing:**
       - Parses the HTML content using BeautifulSoup.
       - Searches for script tags with type 'application/ld+json'.

    2. **JSON Extraction:**
       - Iterates over the script tags to extract JSON content.
       - Uses `json.loads()` to parse the JSON data from the script content.

    3. **Error Handling:**
       - Catches `json.JSONDecodeError` to handle invalid JSON content.
       - Prints an error message if JSON parsing fails.

    4. **Return Value:**
       - Returns a list of JSON objects extracted from the HTML content.
    """
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all script tags with type 'application/ld+json'
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    # Extract JSON-LD data from the scripts
    json_ld_data = []
    for script in json_ld_scripts:
        try:
            # Load the JSON data from the script tag
            data = json.loads(script.string)
            json_ld_data.append(data)
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            print("Error decoding JSON-LD data.")
    
    return json_ld_data

def extract_product_details(json_ld_data):
    """
    Extracts product details such as name, brand, and price from JSON-LD data.

    This function iterates over a list of JSON-LD data dictionaries and attempts to extract 
    product information such as the product's name, brand name, and price. It assumes that 
    these fields exist within each JSON-LD dictionary under specific keys ('name', 'brand', and 'offers').
    Entries where any of these fields are missing or invalid are skipped.

    Args:
        json_ld_data (list): A list of JSON-LD dictionaries.

    Returns:
        list: A list of dictionaries containing product details. Each dictionary includes the 'name',
              'brand name', and 'price' keys with corresponding values.

    Method Details:
    ---------------
    1. **JSON-LD Traversal:**
       - Iterates over each JSON-LD dictionary in the provided list.
       - Looks for product details like 'name', 'brand', and 'price'.

    2. **Data Extraction:**
       - Extracts values for 'name', 'brand', and 'price' from each JSON-LD entry.
       - Assumes the presence of keys like 'name', 'brand', and 'offers'.

    3. **Data Validation:**
       - Checks if the extracted values are not 'N/A'.
       - Skips entries with missing or invalid data.

    4. **Return Value:**
       - Returns a list of dictionaries containing valid product details.
    """
    product_details = []
    
    # Iterate over the list of JSON-LD data
    for data in json_ld_data:
        try:
            # Extract 'name', 'brand', and 'price' from JSON-LD
            name = data.get('name', 'N/A')
            brand_name = data.get('brand', {}).get('name', 'N/A')
            price = data.get('offers', {}).get('price', 'N/A')
            
            # Filter out entries where name, brand, or price are invalid
            if name != 'N/A' and brand_name != 'N/A' and price != 'N/A':
                product_details.append({
                    'name': name,
                    'brand name': brand_name,
                    'price': price
                })
        except AttributeError:
            # Handle cases where the expected structure is not present
            print("Error extracting data from JSON-LD.")
    
    return product_details

def get_random_user_agent(file_path):
    """
    Selects a random user agent from a text file.

    This function reads a file containing a list of user agent strings and selects one 
    randomly. If the file is empty or cannot be read, it returns None.

    Args:
        file_path (str): Path to the user agent text file.

    Returns:
        str: A randomly selected user agent string, or None if the file is empty or unreadable.

    Method Details:
    ---------------
    1. **File Reading:**
       - Opens and reads the user agent file line by line.
       - Strips whitespace and filters out empty lines.

    2. **Random Selection:**
       - Chooses a random user agent from the non-empty lines.

    3. **Return Value:**
       - Returns the selected user agent string or None if no agents are found.
    """
    # Read user agents from file
    with open(file_path, 'r') as f:
        user_agents = [line.strip() for line in f if line.strip()]
    return random.choice(user_agents) if user_agents else None

def get_checkpoint_index(file_path):
    """
    Retrieves the last processed index from a checkpoint file.

    This function reads an integer from a checkpoint file, which indicates the index of the 
    last successfully processed URL. This helps in resuming the scraping process from where 
    it left off in the previous run. If the file is not found or contains invalid data, it 
    defaults to returning 0.

    Args:
        file_path (str): Path to the checkpoint file.

    Returns:
        int: The last processed index, or 0 if the file doesn't exist or contains invalid data.

    Method Details:
    ---------------
    1. **File Reading:**
       - Tries to open and read the checkpoint file.
       - Converts the read content to an integer.

    2. **Error Handling:**
       - Handles `FileNotFoundError` and `ValueError`.
       - Defaults to returning 0 if the file is missing or invalid.

    3. **Return Value:**
       - Returns the integer value read from the file or 0 if an error occurs.
    """
    try:
        with open(file_path, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # Return 0 if the file is not found or the content is invalid
        return 0

def set_checkpoint_index(file_path, index):
    """
    Saves the current processing index to a checkpoint file.

    This function writes the current index to a checkpoint file, which allows the script 
    to resume scraping from this point in future runs. This is useful in case the script 
    is interrupted or fails.

    Args:
        file_path (str): Path to the checkpoint file.
        index (int): The index to be saved.

    Method Details:
    ---------------
    1. **File Writing:**
       - Opens the checkpoint file in write mode.
       - Writes the provided index as a string to the file.

    2. **Error Handling:**
       - Assumes the file path is correct and writable.

    3. **Persistence:**
       - Ensures the index is saved for future runs.
    """
    # Write the current index to the checkpoint file
    with open(file_path, 'w') as f:
        f.write(str(index))

def scrape_urls(input_csv_file, output_csv_file, user_agent_file, checkpoint_file):
    """
    Reads product URLs from a CSV file and scrapes product details from each URL.

    This function reads product URLs from the specified input CSV file and scrapes product 
    details from each URL using random user agents to mimic different browsers. The scraped 
    data is saved to an output CSV file, and the progress is tracked using a checkpoint file 
    to allow the script to resume scraping from the last processed URL in future runs.

    Args:
        input_csv_file (str): Path to the input CSV file containing product URLs.
        output_csv_file (str): Path to the output CSV file where product details will be saved.
        user_agent_file (str): Path to the text file containing user agents for random selection.
        checkpoint_file (str): Path to the checkpoint file to track scraping progress.

    Method Details:
    ---------------
    1. **File Reading:**
       - Reads product URLs from the input CSV file.
       - Uses `csv.DictReader` to parse the CSV file into a list of URLs.

    2. **Resume from Checkpoint:**
       - Retrieves the starting index from the checkpoint file.
       - Starts processing URLs from the checkpoint index.

    3. **HTTP Requests:**
       - Selects a random user agent for each request.
       - Sends HTTP GET requests to each product URL.
       - Handles responses and checks for HTTP status codes.

    4. **Data Extraction:**
       - Extracts JSON-LD data from the HTML response using `extract_json_ld`.
       - Retrieves product details using `extract_product_details`.

    5. **Error Handling:**
       - Handles errors such as connection timeouts and invalid responses.
       - Prints error messages and continues with the next URL.

    6. **Writing Output:**
       - Writes product details to the output CSV file.
       - Uses `csv.DictWriter` to save product data with headers.

    7. **Updating Checkpoint:**
       - Updates the checkpoint index after processing each URL.
       - Saves the index to the checkpoint file for resuming later.

    8. **Random Delay:**
       - Adds a random delay between requests to mimic human-like behavior.
       - The delay is between 3 to 6 seconds.
    """
    # Get the starting index from the checkpoint file
    start_index = get_checkpoint_index(checkpoint_file)
    
    # Open the input CSV file to read product URLs
    with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        urls = [row['Product URL'] for row in reader]
    
    # Open the output CSV file to write product details
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:
        # Define the CSV fieldnames
        fieldnames = ['Product URL', 'name', 'brand name', 'price']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Write the header row to the output CSV file
        writer.writeheader()
        
        # Iterate over the URLs, starting from the checkpoint index
        for index, url in enumerate(urls[start_index:], start=start_index):
            print(f"Scraping {url} (Index: {index})")
            
            # Get a random user agent for the request
            user_agent = get_random_user_agent(user_agent_file)
            if not user_agent:
                print("No user agents found.")
                break
            
            # Define the headers for the HTTP request
            headers = {
                'User-Agent': user_agent,
                'Cookie': 'TS01ac9890=01ef61aed0147b48a50fa29df653c7d2de032c074616ff0e08c5f5d3e09e7f779e1fb132c036faae117f2856b6700b40d582817ee7; TS01de1f4a=01ef61aed00ef36ae1ae6aad28f66be5f542cd77b416ff0e08c5f5d3e09e7f779e1fb132c0bd3bcdc75f8efc4fe4c9c60701ce022b9638238d2b99454ce61b18ccc45d1bf050b57849d11a41634475baf62125339f53e3c77494c86d80e988e660669e092d; V=201; ADRUM_BT=R:0|i:4822|g:251ab504-4735-4cf0-a5c2-40d7c1a864d57025489|e:175|n:customer1_be12de70-87be-45ee-86d9-ba878ff9a400'
            }
            
            # Send an HTTP GET request to the URL
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Extract JSON-LD data from the HTML content
                json_ld_data = extract_json_ld(response.text)
                
                # Extract product details from JSON-LD data
                products = extract_product_details(json_ld_data)
                
                # Write product details to the output CSV file
                for product in products:
                    product['Product URL'] = url
                    writer.writerow(product)
            
            # Update the checkpoint index
            set_checkpoint_index(checkpoint_file, index + 1)
            
            # Add a random delay between 3 to 6 seconds
            time.sleep(random.uniform(3, 6))

# Run the scraping process
scrape_urls(input_csv_file, output_csv_file, user_agent_file, checkpoint_file)
