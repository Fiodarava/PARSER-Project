import csv
from bs4 import BeautifulSoup
import requests

HOST = 'https://www.millwood.by'  # домен, который парсим
URL = 'https://millwood.by/catalog/mebel_loft/obedennye_i_zhurnalnye_stoly/'  # url страницы, которую парсим
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'

}  # заголовки
CSV = 'tables.csv'  # файл для сохранения требуемого текста
PAGENATION = 2  # количество страниц пагинации


def get_html(url, params=''):
    """

    Accessing the page to get the content of the page, html
    :param url: address of a unique resource on the Internet | str
    :param params: additional parameters if needed |
    :return: request response (page content)| class 'requests.models.Response'
    """

    response_ = requests.get(url, headers=HEADERS, params=params)
    return response_


def get_urls(html):
    """

    Getting a list of URLs of all products displayed on the page.
    :param html: request response (page content) | class 'requests.models.Response'
    :return: list of URLs | list
    """

    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('div', class_='item_block col-4')
    urls = []
    for item in items:
        urls.append(HOST + item.find('div', class_='item-title').find('a').get('href'))
    return urls


def get_content(html):
    """

    Getting a list with an element: a dictionary with the text of the necessary information from the product page. Each element of the dictionary is the given information about the product.
    :param html: request response (page content) | class 'requests.models.Response'
    :return: list with product information | list
    """

    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find('div', class_='container')
    tables = []
    tables.append(
        {
            'title': items.find('h1').get_text(strip=True),
            'link_img': HOST + items.find('div', class_='offers_img wof').find('img').get('src'),
            'product_description': items.find('div', class_='detail_text').get_text(strip=True).replace("\xa0", " "),

        }
    )
    return tables


def save_content(tables, path):
    """

    Creation of a csv file and saving product information to a text file in accordance with the column headings.
    :param tables: list to add to file | list
    :param path: Name of csv file | str
    :return: info text saved in file
    """

    with open(path, 'w', newline='', encoding="cp1251", errors="ignore") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['название', 'ссылка на картинку', 'описание продукта'])
        for table in tables:
            writer.writerow([table['title'], table['link_img'], table['product_description']])


def parser(url=URL, pagenation=PAGENATION):
    """

    collection on the manufacturer's website of certain information about the product from the product catalog section and saving the data text to a csv file.
    :param url: address of a unique resource on the Internet | str
    :param pagenation: number of pages in the selected directory section | int
    :return: info text saved in file
    """

    html = get_html(URL)
    if html.status_code == 200:
        list_urls = []
        for page in range(1, PAGENATION + 1):
            print(f'Parse page: {page}')
            html = get_html(URL, params={'PAGEN_1':page})
            list_urls.extend(get_urls(html))
        tables = []
        for url_ in list_urls:
            content = get_content(get_html(url_))
            tables.extend(content)
        save_content(tables, CSV)
    else:
        print('Error')


parser()
