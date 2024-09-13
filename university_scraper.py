from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import json
import os
import time

# Function to extract information from a single university page
def extract_university_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract university name
    name = soup.find('h1').text.strip() if soup.find('h1') else 'N/A'

    # Extract university logo URL
    logo_url = soup.find('img', alt='University Logo')['src'] if soup.find('img', alt='University Logo') else 'N/A'

    # Extract university type
    type = soup.find('td', text='Type').find_next_sibling('td').text.strip() if soup.find('td', text='Type') else 'N/A'

    # Extract university founded year
    founded_year = soup.find('td', text='Founded').find_next_sibling('td').text.strip() if soup.find('td', text='Founded') else 'N/A'

    # Extract university location
    location = {
        'country': soup.find('td', text='Country').find_next_sibling('td').text.strip() if soup.find('td', text='Country') else 'N/A',
        'state': soup.find('td', text='State').find_next_sibling('td').text.strip() if soup.find('td', text='State') else 'N/A',
        'city': soup.find('td', text='City').find_next_sibling('td').text.strip() if soup.find('td', text='City') else 'N/A',
    }

    # Extract university contact information
    contact = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'facebook' in href:
            contact['facebook'] = href
        elif 'twitter' in href:
            contact['twitter'] = href
        elif 'instagram' in href:
            contact['instagram'] = href
        elif 'linkedin' in href:
            contact['linkedin'] = href
        elif 'youtube' in href:
            contact['youtube'] = href

    # Extract phone number
    phone_number = soup.find('td', text='Phone').find_next_sibling('td').text.strip() if soup.find('td', text='Phone') else 'N/A'

    # Extract university official website URL
    contact['officialWebsite'] = soup.find('td', text='Website').find_next_sibling('td').find('a')['href'] if soup.find('td', text='Website') else 'N/A'

    # Create a dictionary with the extracted data
    university_data = {
        'name': name,
        'logoSrc': logo_url,
        'type': type,
        'establishedYear': founded_year,
        'location': location,
        'contact': contact
    }

    return university_data

# Main function to scrape universities from the listing page
def main():
    # Set up the Selenium WebDriver
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # URL to scrape
    main_url = "https://www.4icu.org/de/universities/"
    base_url = "https://www.4icu.org"

    # Open the URL in the browser
    driver.get(main_url)

    # Allow the page to fully load
    time.sleep(10)  # Increased sleep time for better loading

    # Get the page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Close the Selenium browser session
    driver.quit()

    # Find all university links
    university_urls = [base_url + a['href'] for a in soup.find_all('a', href=True) if 'university' in a['href']]

    # Debugging: Print the number of URLs found and sample URLs
    print(f"Extracted {len(university_urls)} university URLs")
    if len(university_urls) > 0:
        print(f"Sample URLs: {university_urls[:5]}")
    else:
        print("No university URLs found. Check the website structure or JavaScript loading.")

    # Create a directory to store the JSON files
    folder_name = "university_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Extract and save data for each university
    for url in university_urls:
        try:
            university_data = extract_university_data(url)
            filename = f"{folder_name}/{university_data['name'].replace('/', '_').replace(':', '-')}.json"
            
            # Save the data to a JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(university_data, f, indent=4)
            print(f"Saved data for {university_data['name']}")

        except Exception as e:
            print(f"Failed to process {url}: {e}")

# Run the main function
if __name__ == "__main__":
    main()
