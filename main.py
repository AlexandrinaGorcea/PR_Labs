import requests
from bs4 import BeautifulSoup


url = 'https://makeup.md/categorys/3/'


# get additional details from product's individual page
def get_additional_details(product_url):
    if product_url == "N/A":
        return {
            'year': "N/A",
            'gama_de_produse': "N/A",
            'volume': "N/A"
        }

    product_response = requests.get(product_url)
    if product_response.status_code == 200:
        product_soup = BeautifulSoup(product_response.text, 'html.parser')

        # Extract 'year', 'Gama de produse', and 'volume' from the product page using 'string' instead of 'text'
        year = product_soup.find('strong', string='Data lansării:').next_sibling.strip() if product_soup.find('strong',
                                                                                                              string='Data lansării:') else "N/A"
        gama_de_produse = product_soup.find('strong',
                                            string='Gama de produse:').next_sibling.strip() if product_soup.find(
            'strong', string='Gama de produse:') else "N/A"
        volume = product_soup.find('strong', string='Volum:').next_sibling.strip() if product_soup.find('strong',
                                                                                                        string='Volum:') else "N/A"

        return {
            'year': year,
            'gama_de_produse': gama_de_produse,
            'volume': volume
        }
    else:
        return {
            'year': "N/A",
            'gama_de_produse': "N/A",
            'volume': "N/A"
        }


# request to main page
response = requests.get(url)
if response.status_code == 200:
    # get content
    html_content = response.text

    # BeautifulSoup is used to parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    product_items = soup.find_all('li', {'data-id': True})  # Get all product list items with data-id

    for item in product_items:
        title_tag = item.find('a', class_='simple-slider-list__name')
        title = title_tag.text.strip() if title_tag else "N/A"

        name_tag = item.find('div', class_='simple-slider-list__description')
        name = name_tag.text.strip() if name_tag else "N/A"

        price_tag = item.find('span', class_='price_item')
        if price_tag:

            price = ''.join(filter(str.isdigit, price_tag.text))
            price = int(price) if price.isdigit() else "N/A"
        else:
            price = "N/A"

        link_tag = item.find('a', class_='simple-slider-list__image')
        link = 'https://makeup.md' + link_tag['href'] if link_tag else "N/A"

        # only call get_additional_details if is found a valid link
        if link != "N/A":
            additional_details = get_additional_details(link)
        else:
            additional_details = {
                'year': "N/A",
                'gama_de_produse': "N/A",
                'volume': "N/A"
            }

        # dictionary with product details
        products.append({
            'title': title,
            'name': name,
            'price': price,
            'link': link,
            'year': additional_details.get('year', "N/A"),
            'gama_de_produse': additional_details.get('gama_de_produse', "N/A"),
            'volume': additional_details.get('volume', "N/A")
        })


    for product in products:
        print(f"Title: {product['title']}")
        print(f"Name: {product['name']}")
        print(f"Price: {product['price']} MDL")
        print(f"Year: {product['year']}")
        print(f"Gama de produse: {product['gama_de_produse']}")
        print(f"Volume: {product['volume']}")
        print(f"Link: {product['link']}")
        print("\n")
else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
