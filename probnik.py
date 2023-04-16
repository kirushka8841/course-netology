from tqdm import tqdm
import json
import requests
import datetime as dt


class VK:
    def __init__(self, token_vk, version, user_id, count):
        self.token_vk = token_vk
        self.version = version
        self.user_id = user_id
        self.count = count

    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token_vk,
            'v': self.version,
            'owner_id': self.user_id,
            'album_id': 'profile',
            'rev': 1,
            'count': self.count,
            'photo_sizes': 1,
            'extended': 1
        }
        req = requests.get(url=url, params=params)
        res = req.json()
        if 'error' in res:
            raise Exception(res['error']['error_msg'])
        return res


class YandexDisk:
    @staticmethod
    def get_headers(token_ya):
        return {'Authorization': 'OAuth {}'.format(token_ya)}

    def create_folder(self, folder_name, token_ya):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers(token_ya)
        params = {'path': folder_name}
        req = requests.put(url, headers=headers, params=params)
        req.raise_for_status() # добавил проверку на возникновение ошибки в запросе
        if req.status_code == 409:
            check_folder_exists = input('Такая папка уже существует, продолжить загрузку в эту папку? Y/N\n').lower()
            if check_folder_exists == 'N':
                exit()
        return req.json()

    def upload(self, token_ya, photos):
        folder_name = input('Введите название новой папки\n')
        self.create_folder(folder_name, token_ya)
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers(token_ya)
        results = []
        for photo in tqdm(photos):
            link_for_upload = photo['max_size_link']
            response = requests.post(url=url, headers=headers, params={'path': f"/{folder_name}/{photo['file_name']}", 'url':link_for_upload})
            response.raise_for_status() # добавил проверку на возникновение ошибки в запросе
            print(response.json())
            results.append(response.json())
        with open('Result.json', 'w') as file:
            json.dump(results, file)
        print('Загружено')
        return results


class Main:
    def save_photo(self, user_ids, count):
        res = VK(token_vk, 5.131, user_ids, count).get_photo()
        list_photos = []
        list_likes = []
        date_photo = dt.date.today().strftime('%d.%m.%Y')
        if 'error' in res:
            raise Exception(res['error']['error_msg']) # обработка ошибки в случае ее возникновения.
        for foto in res['response']['items']:
            if foto['likes']['count'] in list_likes:
                list_photos.append(
                    {
                        'file_name': f"{foto['likes']['count']} - {date_photo}.jpg",
                        'size': foto['sizes'][-1]['type'],
                        'max_size_link': foto['sizes'][-1]['url']
                    }
                )
            else:
                list_photos.append(
                    {
                        'file_name': f"{foto['likes']['count']}.jpg",
                        'size': foto['sizes'][-1]['type'],
                        'max_size_link': foto['sizes'][-1]['url']
                    }
                )
                list_likes.append(foto['likes']['count'])
        return list_photos


if __name__ == '__main__':
    token_vk = input('Введите токен VK\n')
    user_id = input('Введите id пользователя\n')
    count_photos = input('Введите количество скачиваемых фото\n')
    token_ya = input('Введите токен Яндекс диска\n')
    try:
        YandexDisk().upload(token_ya, Main().save_photo(user_id, count_photos))
    except Exception as e:
        print(f"Ошибка: {e}")
        # 473860275
