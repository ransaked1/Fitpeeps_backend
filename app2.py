import json
from pprint import pprint
import random
from statistics import mean
from flask import Flask, app, request
from flask_restful import Api, Resource, reqparse
from stayup import keep_alive
from threading import Thread

app = Flask('')

json_path = "./data/Activity.json"

def json_reader(file_obj):
	user_list = []
	all_user_list = []
	with open(file_obj, 'r', encoding='utf-8') as f:  # открыли файл с данными
		text = json.load(f)  # загнали все, что получилось в переменную
	for txt in text:  # создали цикл, который будет работать построчно
		all_user_list.append(txt['UserId'])
	user_list = set(all_user_list)
	tmp = {}
	for user in user_list:
		tmp[user] = {}
		flag = 0
		it = 0
		tmp[user]['Activity'] = {}
		tmp[user]['Sleep'] = {}
		tmp[user]['Food'] = {}
		for txt in text:
			const_keys = ['Gender', 'Age']
			keys = ['ActivityTime', 'BasicActivity', 'RecognizedActivity', 'ScreenshotFindingsJson', 'ActivityDetails']
			if txt['UserId'] == user:
				if flag == 0:
					tmp[user]['AboutUser'] = {}
					for const_k in const_keys:
						tmp[user]['AboutUser'][const_k] = txt[const_k]
					tmp[user]['AboutUser']['NormalSteps'] = random.randint(1000, 30000)
					flag = 1

				tmp[user]['Activity'][it] = {}
				for k in keys:
					tmp[user]['Activity'][it][k] = str(txt[k])
				it += 1
				for i in range(5):
					tmp[user]['Sleep'][i] = random.uniform(0, 15)
				for i in range(5):
					tmp[user]['Food'][i] = random.uniform(10, 1000)

		tmp[user]['Percentages'] = {}
		all_sleep = []
		all_steps = []
		all_kcal = []
		all_burn_kcal = []

		for i in tmp[user]['Sleep'].keys():
			all_sleep.append(tmp[user]['Sleep'][i])
		tmp[user]['Percentages']['Sleep'] = round((mean(all_sleep) / 8) * 100, 2)

		count = 0
		for i in tmp[user]['Activity'].keys():
			if tmp[user]['Activity'][i]['ScreenshotFindingsJson'] != 'None':
				tm = json.loads(tmp[user]['Activity'][i]['ScreenshotFindingsJson'])
				if tm.get('Steps') is not None:
					all_steps.append(tm.get('Steps'))
					count += 1
				if tm.get('Calories') is not None:
					all_burn_kcal.append(tm.get('Calories'))

		if count > 0:
			tmp[user]['Percentages']['Steps'] = round(mean(all_steps) / tmp[user]['AboutUser']['NormalSteps'] * 100, 2)
		else:
			tmp[user]['Percentages']['Steps'] = 0

		for i in tmp[user]['Food'].keys():
			all_kcal.append(tmp[user]['Food'][i])

		tmp[user]['Percentages']['Food'] = round((sum(all_kcal) - sum(all_burn_kcal)), 2)
	return tmp

def find_user(file_obj, name):
	tmp = json_reader(file_obj)
	return tmp[name]

@app.route('/get')
def home():
    return json_reader(json_path)

@app.route('/get/user')
def user():
  id = request.args.get("id")
  return find_user(json_path, id)

def run():
  app.run(host='0.0.0.0',port=8080)

def start_server():
    t = Thread(target=run)
    t.start()

start_server()