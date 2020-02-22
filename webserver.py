# Evgeny Ovsov

'''
WSS-server wis SSL support by Evgeny Ovsov

Basic functional:
 - Process wss connections
 - Register client in database
 - Verify client's email (6-digit code)
 - Send temporary download-link to verified clients
'''

import os
import asyncio
import json
import ssl
import pathlib
import time

import websockets

import config
import databaseagent
import digitaloceanagent


def get_time():
    '''
    Little util for formatting time
    :return: date and time as string
    '''
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())


def read_json(data: str):
    '''
    Try to parse JSON
    :param data: string was sent from front-end
    :return: dict or None
    '''
    try:
        dictionary = json.loads(data)
        return dictionary
    except (json.JSONDecodeError, TypeError):
        return None


async def process_request(websocket, data):
    '''
    Main logic of server here. Decision making based on request data.
    :param websocket: (auto) connection with client
    :param parsed json from request
    :return: None
    '''

    if data['type'] == 'register':
        if data['content'] == 'file':
            if data['sign'] in config.FILES_MAP:
                email = data['metadata'].split('Email: ')[-1]
                if not databaseagent.DatabaseAgent.get().is_registered(email):
                    name = data['metadata'].replace("Name: ", "").split('\n')[0]
                    databaseagent.DatabaseAgent.get().register_client(email, config.FILES_MAP[data['sign']], name=name)
                    await websocket.send('{"response":"registered"}')
                else:
                    await websocket.send('{"response":"denied"}')
        else:
            await websocket.send("What are you waiting for?")
    elif data['type'] == 'code':
        email = data['metadata'].split("Email: ")[-1]
        code = data['metadata'].replace("Code: ", "")[:6]
        if databaseagent.DatabaseAgent.get().is_registered(email) and databaseagent.DatabaseAgent.get().validate_code(email, code):
            url = digitaloceanagent.DigitalOceanAgent.get().get_url(filename=databaseagent.DatabaseAgent.get().get_file(email))
            await websocket.send("{\"response\":\"link\", \"content\":\"" + (url if url is not None else "error") + "\"}")
            print("{\"response\":\"link\", \"content\":\"" + (url if url is not None else "error") + "\"}")
        else:
            await websocket.send('{"response":"wrong code"}')
    else:
        await websocket.send("Don't even try!")


async def listen(websocket):
    '''
    Preprocessing of request. If request is not like JSON, we will not event pay attention
    :param websocket: (auto) connection with client
    :param path: (auto)
    :return: None
    '''
    while True:
        try:
            recv = await websocket.recv()
            print(f'{get_time()}: Request from {websocket.remote_address[0]} <- {recv}')
            data = read_json(recv)
            if data:
                await process_request(websocket, data)
            else:
                return
        except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError):
            pass

async def server(websocket, path):
    '''
    This is async method, which will run new async-thread when previous busy
    :param websocket: (auto)
    :param path: (auto)
    :return: None
    '''
    while True:
        await listen(websocket)


async def coroutine():
    '''
    Some simple background task. Many of these can be created.
    :return: Nothing
    '''

    while True:
        await asyncio.sleep(60)


if __name__ == '__main__':
    if os.environ.get("DEBUG") is not None:
        print(" --- DEBUG MODE --- ")
        INSTANCE = websockets.serve(server  , "127.0.0.1", 1337)
    else:
        SSL = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        CERT = config.SSL['cert']
        KEY = config.SSL['key']
        SSL.load_cert_chain(certfile=CERT, keyfile=KEY)

        INSTANCE = websockets.serve(server, "*", 1337, ssl=SSL)

    asyncio.get_event_loop().run_until_complete(INSTANCE)
    asyncio.get_event_loop().create_task(coroutine())

    asyncio.get_event_loop().run_forever()
