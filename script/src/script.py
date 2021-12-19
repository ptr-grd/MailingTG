#!/usr/bin/env python3

# --- Import of Modules --- #

import os
import time
import settings
import psycopg2
from pyrogram import Client
from datetime import datetime
# import logging

# --- General Script Logic --- #

general_counter = 0
list_of_users_received_messages = []
list_of_users_not_received_messages = []

def launchPermission():

	# Первый "нулевой" запуск
	if os.stat(settings.date_run_script_file).st_size == 1:
		run = True

	# Проверка времени
	else:
		with open(settings.date_run_script_file, 'r', encoding='utf-8') as file:
			last_run_time = file.read()

		last_run_time_dt = datetime.strptime(last_run_time, "%d-%m-%Y %H:%M:%S")
		time_difference = datetime.now() - last_run_time_dt
		
		# Прошло более 24 часов с последнего запуска
		if time_difference.days >= 1:
			run = True
			print('\n' + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
				f" | [INFO] Запуск скрипта")

		# Прошло менее 24 часов с последнего запуска
		else:
			run = False
			print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
				f" | [INFO] Скрипт не запущен. Не прошло 24 часа с последнего запуска.")
	return run

def main(app):

	current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

	# Чтение текста рассылки
	with open(settings.mailing_text_file, 'r', encoding='utf-8') as file:
		message_text = file.read()

	# Выполняем подключение к Postgres
	try:
		conn = psycopg2.connect(
			database='users_mtg_db',
			user='postgres',
			password='postgres',
			port='5432',
			host='dbpg-mtg')

		cur = conn.cursor()
		print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
			f" | [INFO] Подключение с БД установлено")

	except Exception as _ex:
		print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
			f" | [INFO] Нет соединения с БД:\n{_ex}")
		exit()

	# Шаблон вывода информации в консоль
	print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
  f" | [INFO] Текущие настройки: \n \n\
  Общий суточный лимит сообщений: {settings.MESSAGE_LIMIT_FOR_24H } сообщений\n\
  Суточный лимит сообщений для пользователя: {settings.NUMBER_MESSAGES_FOR_USER_IN_24H} сообщений\n\
  Интервал между отправкой сообщений: {settings.SENDING_INTERVAL} секунд\n")
	time.sleep(15)

	# Функция рассылки сообщений
	def sendMessage(user: str):

		global general_counter, list_of_users_received_messages

		# Запрос к БД: извлечение значений персонального счетчика пользователя
		try:
			query_n1 = f"SELECT count FROM users WHERE nickname = '{user}'"
			cur.execute(query_n1)

		except Exception as _ex:
			print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
				f" | [INFO] Не удалось извлечь данные о счетчиках:\n{_ex}")

		# Сверяем счетчики. Считаем сколько нужно отправить сообщений пользователю
		personal_counter = cur.fetchone()[0]
		factual_counter = settings.NUMBER_MESSAGES_FOR_USER_IN_24H - personal_counter

		# Отправка сообщений отдельному пользователю по суточному лимиту
		for count in range(factual_counter):

			# Явный выход из цикла, если достигли суточного лимита
			if general_counter == settings.MESSAGE_LIMIT_FOR_24H:

				print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
					f" | [INFO] Достигнут суточный лимит")
				break

			app.send_message(user, message_text)
			general_counter += 1

			# Запрос к БД: обновление персонального счетчика пользователя
			try:
				query_n2 = f"UPDATE users SET count = {count + 1} WHERE nickname = '{user}'"
				cur.execute(query_n2)
				conn.commit()

			except Exception as _ex:
				print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
					f" | [INFO] Не удалось обновить данные о счетчиках:\n{_ex}")

			time.sleep(settings.SENDING_INTERVAL)

	# Основной цикл скрипта
	with app:

		# Запрос к БД: извлечение никнеймов пользователей
		try:
			query_n3 = "SELECT nickname FROM users"
			cur.execute(query_n3)
			list_of_users = cur.fetchall()
			print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
				f" | [INFO] Получено {len(list_of_users)} записей из БД")

		except Exception as _ex:
			print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
				f" | [INFO] Не удалось извлечь данные о пользователях:\n{_ex}")

		print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
			f" | [INFO] ( --- Начало рассылки --- ) ")

		# Перебор полученных пользователей
		for user in list_of_users:

			try:
				sendMessage(user[0])
				list_of_users_received_messages.append(user[0])

			except Exception as _ex:
				print('\n' + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
					f" | [INFO] Не удалось извлечь данные о пользователях:\n{_ex}")
				list_of_users_not_received_messages.append(user[0])

		print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
			f" | [INFO] ( --- Конец рассылки --- ) ")

		# Очистка персональных счетчиков
		for user in list_of_users:

			# Запрос к БД: обнуление счетчика
			try:
				query_n4 = f"UPDATE users SET count = 0 WHERE nickname = '{user[0]}'"
				cur.execute(query_n4)
				conn.commit()

			except Exception as _ex:
				print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
					f"| [INFO] Не удалось обнулить персональные счетчики:\n{_ex}")

		print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
			f" | [INFO] Персональные счетчики были обнулены")

		# Запись времени запуска
		with open(settings.date_run_script_file, 'w', encoding='utf-8') as file:
			file.write(current_time)

		# Запись "битых" пользователей в файл 
		with open(settings.logs_file, 'a', encoding='utf-8') as file:

			for user in list_of_users_not_received_messages:
				file.write(user + '\n')

	conn.close()


if __name__ == '__main__':
	
	start_time = datetime.now()
	permission = launchPermission()
	app = Client('main', api_id=settings.API_ID, api_hash=settings.API_HASH)

	main(app) if permission else exit()

	end_time = datetime.now()
	total_time = end_time - start_time

	print('\n' + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
	f" | [INFO] Рассылка завершена. Всего сообщений: {general_counter}")

	print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
	f" | [INFO] {len(list_of_users_received_messages)} пользователей получили сообщения")

	print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + \
	" | [INFO] Итоговое время: " + str(total_time))
