import pandas as pd


def read_excel(excel_file_path: str) -> tuple:
    df = pd.read_excel(excel_file_path)
    link = df['Link'].values
    first_name = df['first_name'].values
    last_name = df['last_name'].values
    title = df['title'].values
    description = df['description'].values
    category = df['category'].values
    services = df['services'].values
    features = df['features'].values
    minimal_price = df['minimal_price'].values
    payment_method = df['payment_method'].values
    type_choice = df['type_choice'].values
    time_of_work = df['time_of_work'].values
    phone = df['phone'].values
    country = df['country'].values
    region = df['region'].values
    city = df['city'].values
    lat = df['lat'].values
    lng = df['lng'].values
    images = df['images'].values
    df_len = len(df)
    return (
        link, first_name, last_name, title, description, category, services, features, minimal_price, payment_method,
        type_choice, time_of_work, phone, country, region, city, lat, lng, images, df_len
    )


def fill_database() -> None:
    link, first_name, last_name, title, description, category, services, features, minimal_price, payment_method, \
    type_choice, time_of_work, phone, country, region, city, lat, lng, images, df_len = read_excel('./excel/flagma.xlsx')
    iter = 0
    while iter <= df_len:
        try:
            print(iter)
            print(link[iter])
            print(first_name[iter])
            print(title[iter])
            print(description[iter])
            print(category[iter])
            print(services[iter])
            print(features[iter])
            print(minimal_price[iter])
            print(payment_method[iter])
            print(type_choice[iter])
            print(time_of_work[iter])
            print(phone[iter])
            print(country[iter])
            print(region[iter])
            print(city[iter])
            print(lat[iter])
            print(lng[iter])
            print(images[iter])
            iter += 1
        except IndexError as e:
            print('Error', e)


def main() -> None:
    fill_database()


if __name__ == '__main__':
    main()
