import time
import requests
from pprint import pprint
import json
import os
import datetime
from tqdm import tqdm

# with open('token.txt', 'r') as file_object:
#     token = file_object.read().strip()
os.chdir(r'C:\Users\Елена\OneDrive\Рабочий стол\курсовая')
token = open('token.txt')
token_ya = open('token_ya.txt')


class VK:
    
    def __init__(self, token, user_ids, version=5.131, count=5):
       self.count = count
       self.user_ids = user_ids
       self.version = version
       self.token = token
    
    def users_info(self, user_ids):
        URL = 'https://api.vk.com/method/users.get'
        user_params = {
                'user_ids': user_ids 
            }
        res = requests.get(URL, params=user_params).json()
        return res

    def get_photos():
        # user_info = self.users_info(self.user_ids)
        # name = f"{user_info['response'][0]['first_name']} {user_info['response'][0]['last_name']}"
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': input('Введите id пользователя\n'),
            'album_id': 'profile',
            'photo_sizes': '1',
            'extended': '1',
            'access_token': token,
            'v': 5.131,
            'count': 5
        }
        res = requests.get(url, params = params)
        res = res.json()
        if res['response']['count'] == 0:
            print(f'У пользователя нет фото')
        list_photos = []
        list_likes = []
        for foto in res['response']['items']:
            time.sleep(0.3)
            date_photo = datetime.datetime.fromtimestamp(foto['date']).strftime('%Y-%m-%d')
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


class YandexDisk:

    def __init__(self, list_photos):
        self.token = token
        self.list_photos = list_photos

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": path, "overwrite": "true"}
        response = requests.get(upload_url, headers=self.get_headers, params=params)
        return response.json()['href']
    
    def create_folder(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        path = input('Введите название новой папки\n')
        params = {'path': path}
        response = requests.put(upload_url, headers=self.get_headers(), params=params)
        if response.status_code == 409:
            check_folder_exists = input('Такая папка уже существует, продолжить загрузку в эту папку? Y/N\n').lower()
            if check_folder_exists == 'n':
                exit()
        return path

    def upload(self):
        list_photos_for_json = []
        path = self.create_folder()
        for photo in tqdm(self.list_photos):
            file_name = photo['file_name']
            size = photo['size']
            link_for_upload = photo['max_size_link']
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {'path': f'/{path}/' + file_name + '.jpg', 'url': link_for_upload}
            response = requests.post(upload_url, params=params, headers=self.get_headers())

            if response.status_code != 202:
                print('Ошибка загрузки')
            list_photos_for_json.append(
                {
                    'file_name': file_name,
                    'size': size
                }
            )
        with open('Result.json', 'w') as file:
            json.dump(list_photos_for_json, file)
        print('Загружено')

if __name__ == '__main__':
    count_photos = input('Введите количество скачиваемых фото\n')
    # YandexDisk(token_ya, get_photos(user_id, count_photos).upload())
    # YandexDisk(VK.get_photos(token)).upload()
    # ya.upload(VK.get_photos(token))
    uploader_ya = YandexDisk(token_ya)
    uploader_vk = VK.get_photos()
    uploader_ya.upload(uploader_vk)
    
# '473860275'