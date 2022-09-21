Ссылка на [проект](https://github.com/KenKi2002/Auth_sprint_1)

## Работа с проектом

### Запуск приложения локально
1. Установить зависимости командой
    ```$ poetry install```
2. Создать файл конфигурации ```.env``` в корне проекта и заполнить его согласно ```example.env ```
3. Загрузить приложение в переменную окружения командой
    ```$ export FLASK_APP=main.py```
4. Создать администратора командой
    ```$ flask create_sudo <username> <email> <password>```
5. Заполнить БД данными командой
    ```$ flask create_sudo create_tables```
6. Проект запускается командой
    ```$ python3 src/wsgi.py```
7. Перейти к документации по url: ```http://localhost:5000/swagger/ ```

### Запуск приложения в docker
1. Создать файл конфигурации ```.env``` в корне проекта и заполнить его согласно ```example.env ```
2. Запустить контейнер командой
    ```$ docker-compose -f docker-compose.yml up -d --build```
3. Перейти к документации по url: ```http://localhost:5000/swagger/ ```


