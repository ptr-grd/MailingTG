
# -- Script settings -- #

# Confidential-Data
API_ID = 2637313 # Пример
API_HASH = '425trhetrgqrh3246bd0f7fa' # Пример

# Script behavior
MESSAGE_LIMIT_FOR_24H = 1000					# Лимит всех рассылаемых сообщений за 24 часа с аккаунта
NUMBER_MESSAGES_FOR_USER_IN_24H = 2 				# Количество присылаемых сообщений пользователю за 24 часа
SENDING_INTERVAL = 3						# Интервал (в сек) между отправкой сообщений

# Other settings
mailing_text_file = '../res/message-text.txt'			# Путь до файла с текстом сообщения
date_run_script_file = '../res/date-run.txt'			# Путь до файла с записью времени запуска
logs_file = '../res/data.log'					# Путь до файла с логами (запись пользователей, не получивших рассылку)
