import requests
from bs4 import BeautifulSoup
import json

# The URL to start scraping from
start_url = "https://pureportal.coventry.ac.uk/en/organisations/eec-school-of-computing-mathematics-and-data-sciences-cmds/publications/"

# Send a GET request to the start URL
response = requests.get(start_url)
soup = BeautifulSoup(response.content, 'html.parser')

# List to store all publication details
publications = []

# Loop through each publication result on the main page
for result in soup.select('li.list-result-item'):
    publication_url = result.select_one('h3.title a')['href']
   
    # Send a GET request to the publication page
    pub_response = requests.get(publication_url)
    pub_soup = BeautifulSoup(pub_response.content, 'html.parser')

    # Extract the publication title
    title = pub_soup.select_one('div.introduction div.rendering h1 span').get_text(strip=True)

    # Extract authors with links
    authors = []
    for author in pub_soup.select('p.relations.persons a.link.person'):
        author_name = author.select_one('span').get_text(strip=True)
        author_link = author['href']
        authors.append({'name': author_name, 'profile_link': author_link})

    author_without_link = pub_soup.select_one('p.relations.persons ' )
    for content in author_without_link.contents:
        if isinstance(content, str):
            for name in content.split(','):
                if name.strip(' '):
                    authors.append({'name' :name.strip()})
        

    # Extract the publication year
    publication_year = pub_soup.select_one('tr.status span.date').get_text(strip=True)

    # Append publication details to the list
    publications.append({
        'title': title,
        'authors': authors,
        'publication_year': publication_year,
        'publication_link': publication_url
    })

# Save the publication details to a JSON file
with open('research1.json', 'w', encoding='utf-8') as f:
    json.dump(publications, f, ensure_ascii=False, indent=4)

print("Data has been saved to research1.json")
