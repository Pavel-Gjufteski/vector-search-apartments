import requests
from bs4 import BeautifulSoup
import math
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

url = "https://www.pazar3.mk/oglasi/zivealista/stanovi/skopje?PriceFrom=50000"
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")

if response.status_code ==200:
    print(f"Response is:{response.status_code}, You are good to go")
else:
    print(f"Response is: {response.status_code}, Try another method to scrape the website")

    
total_results = 2500


def get_all_pagination(total_results):
    total_pages =math.ceil(total_results/50)
    all_pages = []
    for page_number in range(1,total_pages+1):
        page_url_format =f"https://www.pazar3.mk/oglasi/zivealista/stanovi/skopje?Page={page_number}&PriceFrom=50000"
        print(f"Total number of all pages: {len(all_pages)}")
        all_pages.append(page_url_format)
    return all_pages

def get_all_suffixes_per_page(soup):
    all_ads = soup.find_all("a",class_="Link_vis")
    link_suffixes = []
    for ad in all_ads:
        suffix = ad.get("href")
        full_link = f"https://www.pazar3.mk/{suffix}"  
        link_suffixes.append(full_link)
    print(f"Total links found on this page: {len(link_suffixes)}")
    return link_suffixes

url = "https://www.pazar3.mk/oglas/zivealista/stanovi/prodazba/skopje/aerodrom/stan-od-80-m2-se-prodava-vo-novo-lisice/7291190"
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")
def parsed_data(soup):
    data_dict = {}

    try:
        data_dict["title"] = soup.find("h1", class_="ci-text-base").text.strip()
    except:
        data_dict["title"] = None

   
    try:
        price_class = soup.find_all("bdi", class_="new-price")
        for item in price_class:
            data_dict["price"] = item.find("span", class_="format-money-int")["value"]
    except:
        data_dict["price"] = None

    
    try:
        tags_area = soup.find("div", class_="tags-area")

        rooms = address = size = features = listing_type = listed_by = location = None

        if tags_area:
            tags = tags_area.find_all("a", class_="tag-item")
            for tag in tags:
                label = tag.find("span").get_text(strip=True).lower()
                value = tag.find("bdi").get_text(strip=True)

                if "број на соби" in label:
                    rooms = value
                elif "адреса" in label:
                    address = value
                elif "површина" in label:
                    size = value
                elif "за живеалиштето" in label:
                    features = value
                elif "вид на оглас" in label:
                    listing_type = value
                elif "огласено од" in label:
                    listed_by = value
                elif "локација" in label:
                    location = value

        data_dict["rooms"] = rooms
        data_dict["address"] = address
        data_dict["size"] = size
        data_dict["features"] = features
        data_dict["listing_type"] = listing_type
        data_dict["listed_by"] = listed_by
        data_dict["location"] = location

    except:
        data_dict["rooms"] = None
        data_dict["address"] = None
        data_dict["size"] = None
        data_dict["features"] = None
        data_dict["listing_type"] = None
        data_dict["listed_by"] = None
        data_dict["location"] = None

    return data_dict

def main():
    final_data = []

    all_pages = get_all_pagination(total_results)

    for page in all_pages:
        print(f"\nScraping pagination page: {page}")
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")

        all_suffixes = get_all_suffixes_per_page(soup)

        for index, direct_link in enumerate(all_suffixes, start=1):
            print(f"Parsing ad number {index}: {direct_link}")
            try:
                response = requests.get(direct_link)
                soup = BeautifulSoup(response.text, "html.parser")
                data = parsed_data(soup)
                final_data.append(data)
            except Exception as e:
                print(f"Failed to parse {direct_link}: {e}")

    df = pd.DataFrame(final_data)
    df.to_csv("pazar3_scraped_data_test.csv", index=False)
    print(df.isna().sum())
    df = df.dropna()  

if __name__ == "__main__":
    main()


    
    