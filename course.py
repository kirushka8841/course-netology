import requests
import json
from tqdm import tqdm
import datetime as dt
import time
from settings import token_ya, token_vk

class VK:
    
    
    def __init__(self, access_token, version, user_ids, count = 5):
        self.access_token = access_token
        self.version = version
        self.user_ids = user_ids
        self.count = count


    def get_user(self):
        url = 'https://api.vk.com/method/users.get'
        get_user_params = {
            'user_ids': self.user_ids,
            'access_token': self.access_token,
            'version': self.version,
            'count': self.count
        }
        response = requests.get(url, get_user_params)
        json_response = response.json()
        return json_response

    
    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'album_id': 'profile',
            'photo_sizes': '1',
            'extended': '1',
            'count': self.count
        }
        res = requests.get(url, params).json()
        return res


class YandexDisk:
    
    
    def __init__(self, token, list_photos):
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
        response = requests.get(upload_url, headers=self.get_headers(), params=params)
        return response.json()['href']
    

    def create_folder(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        path = input('Введите название новой папки\n')
        params = {'path': path}
        response = requests.put(upload_url, headers=self.get_headers(), params=params)
        if response.status_code == 409:
            check_folder_exists = input('Такая папка уже существует, продолжить загрузку в эту папку? Y/N\n').lower()
            if check_folder_exists == 'N':
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
    

class Main:
    def save_photo(self, user_ids, count):
        res = VK(token_vk, 5.131, user_ids, count).get_photo()
        list_photos = []
        list_likes = []
        time.sleep(0.3)
        date_photo = dt.date.today().strftime('%d.%m.%Y')
        print(res)
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
    user_id = input('Введите id пользователя\n')
    count_photos = input('Введите количество скачиваемых фото\n')
    YandexDisk.upload(token_ya, Main().save_photo(user_id, count_photos))
# '473860275'