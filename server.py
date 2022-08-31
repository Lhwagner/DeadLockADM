import threading
import socket

from resource import Board

clients = []


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = Board()

    try:
        server.bind(('10.13.14.219', 7777))
        server.listen()
    except socket.error:
        return print('It was not possible to start server!\n')

    while True:
        client, addr = server.accept()
        clients.append(client)
        thread = threading.Thread(target=messages_treatment, args=[client, r])
        thread.start()


def messages_treatment(client, r):
    while True:
        try:
            msg = client.recv(2048)
            print(f'message received: {str(msg)}')
            process_message(r, client, str(msg))
        except socket.error as e:
            print(f'Something went wrong, error {e}')
            delete_client(client)
            break


def process_message(r, client, msg):
    username = msg.split('-')[0]
    if 'request' in msg:
        if r.request_resource(client, username):
            broadcast('accepted', client)
        else:
            broadcast('somebody are using the board, wait your turn', client)
            broadcast(f'You are in the position {r.get_position()}, The waiting time is {int(r.get_position()) * 15} seconds', client)

    elif 'close' in msg:
        r.revoke_resource()
        broadcast('connection closed', client)

        if items := r.get_queue():
            print('Items na fila:')
            for idx, item in enumerate(items):
                print(str(item.get('username')))
                broadcast(f'You are in the position {idx}, The waiting time is {idx * 15} seconds', item.get('client'))

        if item := r.grant_resource():
            broadcast('accepted', item)


def broadcast(msg, client):
    for clientItem in clients:
        if clientItem == client:
            try:
                clientItem.send(msg.encode('utf-8'))
                break
            except Exception as e:
                print(e)
                delete_client(clientItem)


def delete_client(client):
    clients.remove(client)


main()
