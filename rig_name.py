import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from prettytable import PrettyTable
from workers_dict import actual_dict

# Начало работы скрипта
start = datetime.now()

#Запрашивает данные с API, обрабатывает ответ и преобразует его в JSON-формат.
url = 'https://api.aleo1.to/v1/wallets/aleo1tsp6nujt6hhl4uv5ya4rhrkf0h8jf0j22lj3n2xtgede07hr05yq3ag986'
request = requests.get(url)
soup = BeautifulSoup(request.text, 'lxml')
text = soup.find('body').find('p').text

text = json.loads(text)

#Создает список майнеров, собирает информацию о хэшрейте, IP-адресах, хостнеймах и видеокартах.
miner_len = len(text['miners'])
info_list = []
info_dict = {}
hash_rate = 0
balance = text['balance']['total']

for i in range(miner_len):
    info_dict = {'ip': text['miners'][i]['ip'], 'hashrate': text['miners'][i]['hashrate'], 'hostname': text['miners'][i]['hostname'], 'gpu': []}
    info_list.append(info_dict)

card_dict = {}

for i in range(miner_len):
    for num in text['miners'][i]['hardware']['gpu']:
        info_list[i]['gpu'].append(num['model'])
        if num['model'] not in card_dict:
            card_dict[num['model']] = 1
        else:
            card_dict[num['model']] += 1 

# Определение количества видеокарт каждой модели
index_list = []

for item in info_list:
    for value in actual_dict.values():
        if item['hostname'] in value['hostname']:
            if item['ip'] not in value['ip']:
                value['ip'].append(item['ip'])
            value['actual_miners'].append(item['hostname'])
            value['hashrate'] += item['hashrate']
            value['gpu'].append(item['gpu'])
            index_list.append(item)
            hash_rate += item['hashrate']
        
# Сравнение полученных данных о майнерах с заранее определенным списком майнеров
for item in index_list:
    info_list.remove(item)        

print('')
if info_list:
    print('+----------+------------+----------+\n| Майнер(ы) которых нет в списках  |')
    not_in_list = ['hostname', 'hashrate', 'ip']
    miners_not_in_list = []

    colums = len(not_in_list)
    table = PrettyTable(not_in_list)

    vak = {}

    for item in info_list:
        miners_not_in_list.append(item['hostname'])
        miners_not_in_list.append(round(item['hashrate'], 2))
        miners_not_in_list.append(item['ip'])

    td_data = miners_not_in_list[:]

    while td_data:
        table.add_row(td_data[:3])
        td_data = td_data[3:]

    print(table)
    print(' ')

# Формирование таблицы с майнерами, которые отсутствуют в списке
th = ['Telegram', 'Обязательный хэш', 'Актуальный хэш', 'Разница']
td = []
counter = 0
for values in actual_dict.values():
    td.append(values['username'])
    td.append(values['c/s'])
    td.append(round(values['hashrate'], 2))
    td.append(round(values['hashrate'] - values['c/s'], 2))
    counter += values['hashrate'] - values['c/s']

colums = len(th)
table2 = PrettyTable(th)
td_data = td[:]

while td_data:
    table2.add_row(td_data[:4])
    td_data = td_data[4:]

print(table2)

sum_v = 0

# Подсчет количества видеокарт каждого майнера
for value in actual_dict.values():
    sum_s = 0
    #print('\n' + '-'*50)
    #print(f"{value['username']} текущие видео карты: ", end='')
    for item in value['gpu']:
        for gpu in item:
            #print(f'{gpu}, ', end='')
            sum_v += 1
            sum_s += 1
    #print('\nКол-во карт: {}'.format(sum_s))

# Вывод различных показателей для каждого майнера
print(f"\nРазница между обязательным/актуальным: {round(counter, 2)}\nОбщий хэшрейт: {round(hash_rate, 2)}\nКол-во устройств майнеров: {miner_len} \nКол-во токенов в пуле: {round(balance, 2)}\n[+] За последний час: {text['balance']['change_1h']} \n[+] За последние 24 часа: {text['balance']['change_24h']}\nОбщее кол-во видеокарт: {sum_v}\n")

for key, value in actual_dict.items():
    for item in value['actual_miners']:
        value['hostname'].remove(item)

# Вывод информации о майнерах, которые не работают сейчас
for value in actual_dict.values():
    if value['hostname']:
        print(f" >>>>>> {value['username']} this miner(s) not working now - {value['hostname']}")

# Вывод времени выполнения скрипта
end = datetime.now()

print(f'\nВремя выполнения скрипта: {end-start}')

# Вывод общего количества видеокарт каждой модели
# for key, value in card_dict.items():
#      print(f"Модель: {key}. Кол-во штук: {value}")