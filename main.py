import time
import random
import requests

from lxml import etree
from xlwt import Workbook
from xlutils.copy import copy
from xlrd import open_workbook
from datetime import datetime
from bs4 import BeautifulSoup

from settings import (
    FLAGMA_LINKS,
    NINJA_API_KEY,
    REGION_DICT,
    TYPE_OF_CHOICES,
    MONEY_VALUE_MODELS,
    NAME_LIST,
    LAST_NAME_LIST
)


class FlagmaParser:
    links_iteration = 0
    row_iteration = 1
    file_name = 'flagma_dataset.xls'
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    cur_date = datetime.now().strftime('%m_%d_%Y')

    def run_script(self, links_list):
        self.create_excel(self.file_name)
        for cat_link_dict in links_list:
            for k in cat_link_dict.keys():
                category = k
                link = cat_link_dict[k]
                print('Key: ', k)
                print("Value: ", cat_link_dict[k])
            links_list = self.get_data(url=link)
            self.read_adverts_file(self.links_iteration, self.row_iteration, links_list, category)
            self.links_iteration += 1

    def get_data(self, url: str) -> list:
        page_number = 0
        links_list = []
        while page_number < 10:
            print(url + f'page-{page_number}')
            response = self.session.get(url=url + f'page-{page_number}', headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            for link in soup.select('.page-list-item .header a'):
                time.sleep(1)
                links_list.append(link.get('href'))
            if soup.select("li.next a[onclick^='goToPage']"):
                print("Have next")
            else:
                page_number = 10
            page_number += 1
        print('Amount of link: ', len(links_list))
        return links_list

    def parse_advert(self, url: str, category: str, requests=None) -> None:
        response = self.session.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            search_link = soup.select('.bread-crumbs .search-link')[0].text.strip()
        except:
            search_link = soup.select(".bread-crumbs [itemprop='itemListElement'] a span")[-1 - 1].text.strip()
        service = soup.select(".bread-crumbs [itemprop='itemListElement'] a span")[-1].text.strip()
        title = etree.HTML(str(soup)).xpath('//div[@class="card-m"]//h1')[0].text.strip()
        date = etree.HTML(str(soup)).xpath('//div[@class="contacts-block"]//span')[0].text.strip().split(' ')
        if date[1] == 'січня' and date[1] == 'лютого' and date[2] != '2022,':
            return
        try:
            price = soup.select(".price-block [itemprop='price']")[0].text.strip()
            price_cur = soup.select(".price-block [itemprop='priceCurrency']")[0].text.strip()
            price_unit = soup.select(".price-block .price-unit")[0].text.strip()
            price_final = f'{price}|{price_cur}|{price_unit}'
        except:
            price_final = 'Цена по запросу'
        description = self.replace_chars(soup.find('div', id='description').text.strip())
        try:
            contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]')[0].text.strip()
        except:
            contact_name = etree.HTML(str(soup)).xpath('//div[@class="user-name"]/span')[0].text.strip()
        company_info = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
            0].text.strip()
        company_geo = etree.HTML(str(soup)).xpath("//div[@class='contacts-block']//div[@class='company-info']//span")[
            1].text.strip().split(',')[0]
        photo_list = self.save_photo(soup.select('.card-m .small-photos-block img'))
        phone_list = self.get_phones(soup.select('a.tel'))

        regions_dict = REGION_DICT
        names_list = NAME_LIST
        last_name_list = LAST_NAME_LIST
        type_choices = TYPE_OF_CHOICES
        money_value_models = MONEY_VALUE_MODELS
        payment_method = "CASH_OR_CARD"
        country, region, lng, lat = self.get_city_country_region_lng_lat(company_geo, regions_dict)
        if country == "UA":
            country = 'Україна'
            user_f_name, user_l_name = self.get_user_names(contact_name, names_list, last_name_list)
            min_price, money_value, type_choice, time_of_work = self.prices(
                price_final, type_choices, money_value_models)

            phone = '+38' + str(phone_list[0])
            description = description + '\n' + "Це оголошення було взято з сайту flagma.ua"
            self.write_data_to_excel(
                file_name=self.file_name,
                iter=self.row_iteration,
                link=url,
                first_name=user_f_name,
                last_name=user_l_name,
                title=title,
                category=category,
                features=company_info,
                minimal_price=min_price,
                payment_method=payment_method,
                money_value=money_value,
                type_choice=type_choice,
                time_of_work=time_of_work,
                phone=phone,
                country=country,
                region=region,
                city=company_geo,
                lat=lat,
                lng=lng,
                images=photo_list,
                description=description,
                services=None,
            )
            self.row_iteration += 1

    def read_adverts_file(self, iter: int, row_iteration: int, link_list: list, category: str) -> None:
        for link in link_list:
            time.sleep(random.randint(1, 2))
            print(f'------------------ Iteration №{iter} ------------------')
            self.parse_advert(url=link.strip(), category=category)
            iter += 1

    def get_user_names(self, contact_name: str, names_list: list, last_name_list: list) -> tuple:
        try:
            user_f_name, user_l_name = contact_name.split(' ')
        except:
            user_f_name, user_l_name = random.choices(names_list)[0], random.choices(last_name_list)[0]
        return user_f_name, user_l_name

    def prices(self, price_final: str, type_choices: dict, money_value_models: dict) -> tuple:
        # Price and type of work
        time_of_work = None
        if price_final == 'Цена по запросу':
            min_price, money_value, type_choice = 1000, 'UAH', 'PIECE'
        else:
            try:
                min_price, money_value_flagma, type_choice_flagma = price_final.split('|')
            except ValueError:
                min_price, money_value_flagma, type_choice_flagma = 1000, 'UAH', 'PIECE'

            type_choice = type_choices[type_choice_flagma]
            # Money Value
            try:
                money_value = money_value_models[money_value_flagma]
            except:
                money_value = 'UAH'

            # Minimal price
            if len(str(min_price)) == 0:
                min_price = 1000.0
            try:
                min_price = float(min_price.replace(" ", ""))
            except:
                min_price = float(min_price)

            if type_choice == 'CHANGE':
                time_of_work = 'EIGHT'
        return min_price, money_value, type_choice, time_of_work

    def get_city_country_region_lng_lat(self, company_geo: str, regions_dict: dict) -> tuple:
        api_key = NINJA_API_KEY
        api_url = f'https://api.api-ninjas.com/v1/geocoding?city={company_geo}&country=Україна'
        response = requests.get(api_url, headers={'X-Api-Key': api_key})
        if response.status_code == requests.codes.ok:
            res = response.json()[0]
            lat = res['latitude']
            lng = res['longitude']
            country = res['country']
            try:
                if 'state' in res:
                    region = regions_dict[res['state']]
                else:
                    region = 'Київська область'
            except KeyError as e:
                print(e, "Region dicts")
            print('lat', lat)
            print('lng', lng)
            print('city', company_geo)
            print('region', region)
        else:
            print("Error:", response.status_code, response.text)
            lat = None
            lng = None
            country = None
            region = None
        return country, region, lng, lat

    @staticmethod
    def create_excel(file_name: str) -> None:
        wb = Workbook()
        sheet = wb.add_sheet('Sheet 1')

        sheet.write(0, 0, 'Link')
        sheet.write(0, 1, 'first_name')
        sheet.write(0, 2, 'last_name')
        sheet.write(0, 3, 'title')
        sheet.write(0, 4, 'description')
        sheet.write(0, 5, 'category')
        sheet.write(0, 6, 'services')
        sheet.write(0, 7, 'features')
        sheet.write(0, 8, 'minimal_price')
        sheet.write(0, 9, 'payment_method')
        sheet.write(0, 10, 'money_value')
        sheet.write(0, 11, 'type_choice')
        sheet.write(0, 12, 'time_of_work')
        sheet.write(0, 13, 'phone')
        sheet.write(0, 14, 'country')
        sheet.write(0, 15, 'region')
        sheet.write(0, 16, 'city')
        sheet.write(0, 17, 'lat')
        sheet.write(0, 18, 'lng')
        sheet.write(0, 19, 'images')
        wb.save(file_name)

    @staticmethod
    def replace_chars(string_data) -> str:
        replace_list = ['×', ';', "\n", "  "]
        result = string_data
        for repl in replace_list:
            result = result.replace(repl, " ")
        return result

    @staticmethod
    def get_phones(phone_col: list) -> list:
        phones_list = []
        for phone in phone_col:
            phone_i = phone.text.replace(' ', '').replace('(', '').replace(')', '').replace('-', '').replace('+38', '')
            phones_list.append(phone_i)
        return phones_list

    @staticmethod
    def save_photo(photo_col: list) -> list:
        photo_links_list = []
        for photo in photo_col:
            photo_link = photo.get('src').replace('.jpg', '_big.jpg')
            photo_links_list.append(photo_link)
        return photo_links_list

    def write_data_to_excel(
            self,
            file_name: str,
            iter: int,
            link: str,
            first_name: str,
            last_name: str,
            title: str,
            description: str,
            category: str,
            features: str,
            minimal_price: str,
            payment_method: str,
            money_value: str,
            type_choice: str,
            time_of_work: str,
            phone: str,
            country: str,
            region: str,
            city: str,
            lat: float,
            lng: float,
            images: list,
            services: str = None,
    ) -> None:
        print(iter)
        row_index = iter
        rb = open_workbook(file_name, formatting_info=True)
        r_sheet = rb.sheet_by_index(0)
        wb = copy(rb)
        w_sheet = wb.get_sheet(0)
        images_list = ''
        if len(images) != 0:
            images_list = images

        w_sheet.write(row_index, 0, link)
        w_sheet.write(row_index, 1, first_name)
        w_sheet.write(row_index, 2, last_name)
        w_sheet.write(row_index, 3, title)
        w_sheet.write(row_index, 4, description)
        w_sheet.write(row_index, 5, category)
        w_sheet.write(row_index, 6, services)
        w_sheet.write(row_index, 7, features)
        w_sheet.write(row_index, 8, minimal_price)
        w_sheet.write(row_index, 9, payment_method)
        w_sheet.write(row_index, 10, money_value)
        w_sheet.write(row_index, 11, type_choice)
        w_sheet.write(row_index, 12, time_of_work)
        w_sheet.write(row_index, 13, phone)
        w_sheet.write(row_index, 14, country)
        w_sheet.write(row_index, 15, region)
        w_sheet.write(row_index, 16, city)
        w_sheet.write(row_index, 17, lat)
        w_sheet.write(row_index, 18, lng)
        w_sheet.write(row_index, 19, images)
        wb.save(file_name)


def main():
    fp = FlagmaParser()
    fp.run_script(FLAGMA_LINKS)


if __name__ == '__main__':
    main()
