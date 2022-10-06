Ссылка на [проект](https://github.com/KenKi2002/Auth_sprint_1)  
Ссылка на [AsyncAPI](https://github.com/KenKi2002/Async_API_sprint_1)

## Работа с проектом

### Запуск приложения локально
1. Установить зависимости командой
    ```$ poetry install```
2. Создать файл конфигурации ```.env``` в корне проекта и заполнить его согласно ```example.env ```
3. Загрузить приложение в переменную окружения командой
    ```$ export FLASK_APP=main.py```
4. Выполнить миграции командой
    ```$ flask db upgrade```
5. Создать администратора командой
    ```$ flask create_sudo <username> <email> <password>```
6. Заполнить БД данными командой
    ```$ flask create_sudo create_tables```
7. Проект запускается командой
    ```$ python3 src/wsgi.py```
8. Перейти к документации по url: ```http://localhost:5000/swagger/ ```

### Запуск приложения в docker
1. Создать файл конфигурации ```.env``` в корне проекта и заполнить его согласно ```example.env ```
2. Запустить контейнер командой
    ```$ docker-compose -f docker-compose.prod.yml up -d --build```

### Запуск тестов
1. Создать файл конфигурации ```.env``` в корне проекта и заполнить его согласно ```example.env ```
2. Запустить контейнер командой
    ```$ docker-compose -f docker-compose.test.yml up -d --build```
