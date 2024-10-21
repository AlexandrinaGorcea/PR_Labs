import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
import datetime
import chardet  # detect encodings such as UTF-8, ISO-8859-1, Shift-JIS

# tcp - Transmission Control Protocol - exchange messages over a network
# ssl - Secure Sockets Layer encryption-based Internet security protocol
# tls - Transport Layer Security


# func that does request with tcp
def send_https_request(host, path):
    context = ssl.create_default_context()
    # port 443 - default port for HTTPS
    with socket.create_connection((host, 443)) as sock:  # connection to the server using tcp
        #  regular socket turns into a secure ssl socket
        with context.wrap_socket(sock, server_hostname=host) as secure_sock:
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            secure_sock.sendall(request.encode())

            response = b""
            while True:
                chunk = secure_sock.recv(4096)
                if not chunk:
                    break
                response += chunk

    # Split headers and body
    headers, _, body = response.partition(b'\r\n\r\n')

    # Detect encoding
    detected = chardet.detect(body)
    encoding = detected['encoding'] or 'utf-8'  # Default to utf-8 if detection fails

    try:
        return body.decode(encoding)
    except UnicodeDecodeError:
        # If decoding fails, try with 'iso-8859-1' as a fallback
        return body.decode('iso-8859-1')


def custom_json_serialize(data):
    if isinstance(data, dict):
        return '{' + ','.join(f'"{k}":{custom_json_serialize(v)}' for k, v in data.items()) + '}'
    elif isinstance(data, list):
        return '[' + ','.join(custom_json_serialize(item) for item in data) + ']'
    elif isinstance(data, str):
        return f'"{data}"'
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, bool):
        return str(data).lower()
    elif data is None:
        return 'null'
    else:
        raise TypeError(f"Object of type {type(data)} is not JSON serializable")


def xml_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"',
                                                                                                               "&quot;")


def custom_xml_serialize(data, root_tag='root'):
    def to_xml(item, tag):
        if isinstance(item, dict):
            return f"<{tag}>" + ''.join(to_xml(v, k) for k, v in item.items()) + f"</{tag}>"
        elif isinstance(item, list):
            return ''.join(to_xml(i, 'item') for i in item)
        else:
            return f"<{tag}>{xml_escape(str(item))}</{tag}>"

    return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{to_xml(data, root_tag)}"


url = 'https://makeup.md/categorys/3/'
host = 'makeup.md'
path = '/categorys/3/'

MDL_TO_EUR = 20


def get_additional_details(product_url):
    if product_url == "N/A":
        return {
            'year': "N/A",
            'gama_de_produse': "N/A",
            'volume': "N/A"
        }

    product_path = product_url.split(host)[1]
    product_html = send_https_request(host, product_path)
    product_soup = BeautifulSoup(product_html, 'html.parser')

    year = product_soup.find('strong', string='Data lansării:').next_sibling.strip() if product_soup.find('strong',
                                                                                                          string='Data lansării:') else "N/A"
    gama_de_produse = product_soup.find('strong', string='Gama de produse:').next_sibling.strip() if product_soup.find(
        'strong', string='Gama de produse:') else "N/A"
    volume = product_soup.find('strong', string='Volum:').next_sibling.strip() if product_soup.find('strong',
                                                                                                    string='Volum:') else "N/A"

    return {
        'year': year,
        'gama_de_produse': gama_de_produse,
        'volume': volume
    }


html_content = send_https_request(host, path)
soup = BeautifulSoup(html_content, 'html.parser')
products = []
product_items = soup.find_all('li', {'data-id': True})

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

    if link != "N/A":
        additional_details = get_additional_details(link)
    else:
        additional_details = {
            'year': "N/A",
            'gama_de_produse': "N/A",
            'volume': "N/A"
        }

    products.append({
        'title': title,
        'name': name,
        'price': price,
        'link': link,
        'year': additional_details.get('year', "N/A"),
        'gama_de_produse': additional_details.get('gama_de_produse', "N/A"),
        'volume': additional_details.get('volume', "N/A")
    })

products_converted = list(
    map(lambda p: {**p, 'price': p['price'] / MDL_TO_EUR if isinstance(p['price'], int) else "N/A"}, products))

filtered_products = list(
    filter(lambda p: p['price'] != "N/A" and p['link'] != "N/A" and p['title'] != "N/A", products_converted))

total_price = reduce(lambda total, p: total + p['price'], filtered_products, 0)

timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

final_data = {
    'filtered_products': filtered_products,
    'total_price': total_price,
    'timestamp': timestamp
}

print(f"Filtered Products (as of {timestamp}):")
for product in final_data['filtered_products']:
    print(f"Title: {product['title']}")
    print(f"Name: {product['name']}")
    print(f"Price (EUR): {product['price']:.2f}")
    print(f"Year: {product['year']}")
    print(f"Gama de produse: {product['gama_de_produse']}")
    print(f"Volume: {product['volume']}")
    print(f"Link: {product['link']}")
    print("\n")

print(f"\nTotal Price of Filtered Products: {total_price:.2f} EUR")
print(f"Timestamp: {final_data['timestamp']}")

json_output = custom_json_serialize(final_data)
print("\nJSON Output:")
print(json_output)

xml_output = custom_xml_serialize(final_data, 'data')
print("\nXML Output:")
print(xml_output)