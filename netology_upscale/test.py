import datetime
import time
import requests

UPSCALING_URL = 'http://127.0.0.1:5000/upscaling/'
UPSCALED_URL = 'http://127.0.0.1:5000/upscaled/'

def upload_image():
    try:
        response = requests.post(UPSCALING_URL, files={'file': open('lama_300px.png', 'rb')})
        response.raise_for_status()
        data = response.json()
        return data['file_name'], data['task_id']
    except Exception as e:
        print(f'Произошла ошибка при загрузке изображения: {e}')
        return None, None

def check_task_status(task_id):
    while True:
        try:
            response = requests.get(f'{UPSCALING_URL}{task_id}/')
            response.raise_for_status()
            data = response.json()
            status = data['status']
            print(f'Статус задачи: {status}')
            if status != 'PENDING':
                return status
            time.sleep(10)
        except Exception as e:
            print(f'Произошла ошибка при проверке статуса задачи: {e}')
            return None

def download_processed_image(file_name):
    try:
        response = requests.get(f'{UPSCALED_URL}{file_name}/')
        response.raise_for_status()
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print('Обработанное изображение успешно загружено.')
    except Exception as e:
        print(f'Произошла ошибка при загрузке обработанного изображения: {e}')

def main():
    start_time = datetime.datetime.now()

    print('Запускаем метод POST для загрузки изображения...')
    file_name, task_id = upload_image()
    if file_name is None or task_id is None:
        return

    print(f'Изображение успешно загружено. Имя файла: {file_name}, ID задачи: {task_id}')

    print('\nЗапускаем метод GET для проверки статуса выполнения задачи...')
    status = check_task_status(task_id)
    if status is None:
        return

    print('\nЗапускаем метод GET для загрузки обработанного изображения...')
    download_processed_image(file_name)

    print(f'\nЗатраченное время: {datetime.datetime.now() - start_time}')

if __name__ == "__main__":
    main()
