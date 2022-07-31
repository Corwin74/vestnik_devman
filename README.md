# Учебный проект "Отправляем уведомления о проверке работ"

Данный телеграм-бот служит для оперативного уведомления об изменении статуса, отправленных на проверку работ в рамках учебных курсов на сайте [dvmn.org](https://dvmn.org/)
## Как установить
Для начала работы необходимо:

- Получить токен с сайта [dvmn.org](https://dvmn.org/api/docs/)
- Cоздать бота в Telegram
- Узнать свой id в телеграмм (можно узнать, написав боту @userinfobot)
- Скопировать репозиторий к себе на компьютер:
```
git clone git@github.com:Corwin74/vestnik_devman.git
```
Далее, в корневой папке проекта необходимо создать файл `.env` и записать в него настройки в виде:
```
TLGM_BOT_TOKEN= токен Вашего бота в телеграм
DVMN_API_TOKEN= Ваш токен dvmn
TLGM_CHAT_ID= Ваш id телеграмм
```
Затем используйте `pip` для установки зависимостей. Рекомендуется использовать отдельное виртуальное окружение.  
[Инструкция по установке виртуального окружения](https://dvmn.org/encyclopedia/pip/pip_virtualenv/)
```
pip install -r requirements.txt
```
## Запуск и использование
Для запуска бота необходимо ввести команду:
```
python bot.py
```
Бот оповестит Вас, как только произойдут какие-либо изменения в Ваших работах.
## Deploy на VPS под Linux
Необходимо на VPS выполнить все шаги описанные выше.  
Для того, чтобы запускать нашего бота при старте системы автоматически, воспользуемся системным менеджером `systemd`.  
Создадим файл `bot.service` в директории `/etc/systemd/system` :
```
$ sudo touch /etc/systemd/system/bot.service
```
Затем откроем его:
```
$ sudo nano /etc/systemd/system/bot.service
```
и вставим следующее содержимое и сохраняем файл:
```
[Unit]
Description=Telegram bot %name%
After=syslog.target
After=network.target

[Service]
Type=simple
User=root
# замените на свой путь к каталогу, где находится `bot.py`
WorkingDirectory=/home/user/vestnik_devman/
# замените на свои пути к виртуальному окружению и папке с ботом
ExecStart=/home/envs/tlgm_env/bin/python3 /home/user/vestnik_devman/bot.py
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```
в консоли выполним:
```
# перечитываем конфигурацию 
# (обнаружит файл `bot.service`)
$ sudo systemctl daemon-reload

# подключаем демон `bot.service`
$ sudo systemctl enable bot

# запускаем демон `bot.service`
$ sudo systemctl start bot

# смотрим статус демона `bot.service`
$ sudo systemctl status bot
```
Теперь перезапустить/остановить телеграмм-бота можно системными командами Linux:
```
# перезапуск
$ sudo systemctl restart bot

# остановка
$ sudo systemctl stop bot

# запуск после остановки
$ sudo systemctl start bot
```
Логи бота можно просмотреть командой:
```
$sudo journalctl -u bot.service
```
## Цель проекта
Код написан в образовательных целях на онлайн-курсе [dvmn.org](https://dvmn.org/).
