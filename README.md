# Ajio Product Data Scraping

## Project Overview
The Ajio Product Data Scraper is a Python-based tool designed to scrape product details from the Ajio website. It extracts product URLs from Ajio's API and fetches product information such as name, brand, and price from these URLs. The data is saved into a CSV file for further analysis or usage.

## Features

- **User Agent Filtering:** Filters user agents to ensure that only those that can access the website are used.
- **Product URL Extraction:** Extracts product URLs from Ajio's API and saves them to a CSV file.
- **Product Data Scraping:** Scrapes product details like name, brand, and price from the extracted product URLs.
- **Checkpoint System:** Supports resuming the scraping process using a checkpoint system to track progress.

## Prerequisites

To run this project, you need the following:

- Python 3.6 or higher
- Required Python libraries - requests,beautifulsoup,time,random,csv,UserAgentFilter
      

## Project Structure

- **`user_agent_filtering.py`**: Filters user agents that can successfully access a specific website.
- **`product_link_scraping.py`**: Extracts product URLs from Ajio's API and saves them to a CSV file.
- **`product_data_scraping.py`**: Scrapes product details from each product URL and saves the data to a CSV file.

 
