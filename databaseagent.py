# Evgeny Ovsov

'''
MongoDB wrapper for exact business-logic.
- Add client
- Verify code
- Check attempts to register email twice
'''

import sys
import random
import time

from pymongo import MongoClient

import config
import mailagent


def get_time():
    '''
    Little util for formatting time
    :return: date and time as string
    '''
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())


class DatabaseAgent:
    '''
    Agent for using database (MongoDB)
    All calls must be made like DatabaseAgent.get().somefuction()
    '''

    _instance = None

    @staticmethod
    def get():
        '''
        Something kinda sigleton pattern.
        :return: DatabaseAgent()
        '''
        if DatabaseAgent._instance is None:
            DatabaseAgent._instance = DatabaseAgent()
        return DatabaseAgent._instance

    def __init__(self):
        try:
            self.__agent = MongoClient(
                config.MONGO['address'],
                config.MONGO['port']
            )[config.MONGO['base']][config.MONGO['collection']]
            print(f'MONGODB CONNECTED. WE HAVE {self.__agent.count_documents({})} RECORDS')
        except Exception as e:
            print(f"Something wrong with mongo!\n{e}\nExit!", file=sys.stderr)
            exit(-1)  # If database is not available - server is useless

    def __str__(self):
        return str(config.MONGO)  # When print directly object of class - print info about connection

    def _generate_code(self):
        '''
        Generate random code and send it into email.
        :return: code
        :type return: str
        '''

        code = str()
        for i in range(0, 6):
            char = 58
            while 57 < char < 65:
                char = random.randint(48, 90)
            code = f'{code}{chr(char)}'

        for each in ['JERK', 'DUMB', 'ASS', 'SUCK', 'FAG']:
            if each in code:
                code = self._generate_code()

        return code

    def register_client(self, email, file, name='Unknown'):
        '''
        Add new client into database and get them code
        :param email: email of client
        :param file: what file client requested
        :param name: name of client. Using in e-mails
        :return: Nothing
        '''

        code = self._generate_code()
        mailagent.MailAgent.get().send_mail('code', email, code, name=name)
        self.__agent.insert_one({'datetime': get_time(),
                                 'name': name,
                                 'email': email,
                                 'file': file,
                                 'code': code,
                                 'status': 'code sent'})

    def validate_code(self, email, code):
        '''
        Check code received from client
        :param email: email of client
        :param code: code which client was typed in
        :return: True if code was right and False if client trying to cheat us
        '''

        client = self.__agent.find_one({'email': email})
        if client and client['code'] == code:
            self.__agent.update_one({'email': email},
                                    {"$set": {"status": "link received"}})
            return True
        return False

    def is_registered(self, email):
        '''
        Do we already know this email?

        :param email: email of client
        :return True if we already know this email, otherwise False
        '''

        return self.__agent.find_one({'email': email}) is not None

    def get_file(self, email):
        '''
        What file client wanted?
        :param email: email of client
        :return: real name of file which client requested
        '''

        try:
            return self.__agent.find_one({'email': email})["file"]
        except Exception:
            return None


if __name__ != '__main__':  # when imported
    print(f"MONGODB INIT: {DatabaseAgent.get()}")  # instantly init agent to detect errors as soon as possible
else:
    print("This module can't be used as independent executable.")
