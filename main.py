import requests
from bs4 import BeautifulSoup

url = 'https://makeup.md/categorys/3/'

response = requests.get(url)

if response.status_code == 200:
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    products = []
    product_items = soup.find_all('li', {'data-id': True})

    for item in product_items:
        title_tag = item.find('a', class_='simple-slider-list__name')
        title = title_tag.text if title_tag else "N/A"

        name_tag = item.find('div', class_='simple-slider-list__description')
        name = name_tag.text if name_tag else "N/A"

        price_tag = item.find('span', class_='price_item')
        price = price_tag.text if price_tag else "N/A"

        link_tag = item.find('a', class_='simple-slider-list__image')
        link = link_tag['href'] if link_tag else "N/A"

        products.append({
            'title': title,
            'name': name,
            'price': price,
            'link': 'https://makeup.md' + link
        })

    for product in products:
        print(f"Title: {product['title']}")
        print(f"Name: {product['name']}")
        print(f"Price: {product['price']} MDL")
        print(f"Link: {product['link']}")
        print("\n")
else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")