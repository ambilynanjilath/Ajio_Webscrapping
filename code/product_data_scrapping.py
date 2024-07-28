import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random

# Define file paths
input_csv_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/product_urls.csv'
output_csv_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/final_products_data.csv'
user_agent_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/filtered_user_agents.txt'
checkpoint_file = '/home/user/Documents/Datahut_Internship/Example_Usage_UserAgentFilter/data/checkpoint.txt'

# Function to extract JSON-LD data
def extract_json_ld(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all script tags with type 'application/ld+json'
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    # Extract JSON-LD data from the scripts
    json_ld_data = []
    for script in json_ld_scripts:
        try:
            # Load the JSON data
            data = json.loads(script.string)
            json_ld_data.append(data)
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            print("Error decoding JSON-LD data.")
    
    return json_ld_data

# Function to extract specific data from JSON-LD
def extract_product_details(json_ld_data):
    product_details = []
    
    for data in json_ld_data:
        # Adjust the keys based on your actual JSON-LD structure
        try:
            # Assuming that the data contains 'name', 'brand', and 'offers' with 'price' fields
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

# Function to get a random user agent
def get_random_user_agent(file_path):
    with open(file_path, 'r') as f:
        user_agents = [line.strip() for line in f if line.strip()]
    return random.choice(user_agents) if user_agents else None

# Function to get the start index from checkpoint file
def get_checkpoint_index(file_path):
    try:
        with open(file_path, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

# Function to set the checkpoint index
def set_checkpoint_index(file_path, index):
    with open(file_path, 'w') as f:
        f.write(str(index))

# Read URLs from CSV and scrape data
def scrape_urls(input_csv_file, output_csv_file, user_agent_file, checkpoint_file):
    # Get the starting index from the checkpoint file
    start_index = get_checkpoint_index(checkpoint_file)
    
    # Open the input CSV file
    with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        urls = [row['Product URL'] for row in reader]
    
    # Open the output CSV file
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['Product URL', 'name', 'brand name', 'price']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Scrape data for each URL
        for index, url in enumerate(urls[start_index:], start=start_index):
            print(f"Scraping {url} (Index: {index})")
            
            user_agent = get_random_user_agent(user_agent_file)
            if not user_agent:
                print("No user agents found.")
                break
            
            headers = {
                'User-Agent': user_agent,
                'Cookie': 'TS01ac9890=01ef61aed0147b48a50fa29df653c7d2de032c074616ff0e08c5f5d3e09e7f779e1fb132c036faae117f2856b6700b40d582817ee7; TS01de1f4a=01ef61aed00ef36ae1ae6aad28f66be5f542cd77b416ff0e08c5f5d3e09e7f779e1fb132c0bd3bcdc75f8efc4fe4c9c60701ce022b9638238d2b99454ce61b18ccc45d1bf050b57849d11a41634475baf62125339f53e3c77494c86d80e988e660669e092d; V=201; ADRUM_BT=R:0|i:4822|g:251ab504-4735-4cf0-a5c2-40d7c1a864d57025489|e:175|n:customer1_be12de70-87be-45ee-86d9-ba878ff9a400'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                json_ld_data = extract_json_ld(response.text)
                product_details = extract_product_details(json_ld_data)
                
                # Write data to the CSV file
                for details in product_details:
                    row = {'Product URL': url, **details}
                    writer.writerow(row)
            else:
                print(f"Failed to retrieve the page at {url}. Status code: {response.status_code}")
            
            # Save the current index in the checkpoint file
            set_checkpoint_index(checkpoint_file, index)
            
            # Add a random delay
            delay = round(random.uniform(3, 6), 1)
            print(f"Waiting for {delay} seconds...")
            time.sleep(delay)

# Run the scraping function
scrape_urls(input_csv_file, output_csv_file, user_agent_file, checkpoint_file)
