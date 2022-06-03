import base64
import os
import random
import socket
import ssl
import json
import string

HOST = 'smtp.yandex.ru'
PORT = 465


user_name = ''
password = ''


def request(sock, req):
    sock.send((req + '\n').encode('utf8'))
    recv_data = sock.recv(65535).decode()
    return recv_data


def generate_boundary():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(40))


def create_message(config):
    boundary = generate_boundary()
    attachments, message, text = create_main_part(config)
    if attachments:
        message = add_attachments(boundary, config, message, text)
        return message
    elif text:
        return message + f'\n{fix_problems_with_points(text)}\n.'
    else:
        return message + '\n.'


def add_attachments(boundary, config, message, text):
    message += f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n\n'
    for attachment in config['attachments']:
        message = add_attachment(message, attachment, boundary)
    if text:
        message = add_plain_text(message, text, boundary)
    message += f'--{boundary}--\n.'
    return message


def create_main_part(config):
    attachments = config['attachments']
    text = config['text']
    message = 'From: lo1kek12345@yandex.ru\n'
    message += f'To: {", ".join(config["receivers"])}\n'
    message += f'Subject: {config["subject"]}\n'
    message += 'MIME-Version: 1.0\n'
    return attachments, message, text


def add_plain_text(message, text, boundary):
    message += f'--{boundary}\n'
    message += f'Content-Transfer-Encoding: 8bit\n'
    message += f'Content-Type: text/plain\n'
    message += f'\n{fix_problems_with_points(text)}\n'
    return message


def fix_problems_with_points(string: str):
    lines = string.splitlines()
    res = ''
    for line in lines:
        if line == '':
            res += '\n'
        elif line[0] == '.':
            res += '.' + line + '\n'
        else:
            res += line + '\n'
    return res


def get_file_mime_type(name):
    extension = name.split('.')[-1]
    if extension == 'jpg':
        return 'image/jpg'
    elif extension == 'png':
        return 'image/png'
    elif extension == 'pdf':
        return 'application/pdf'
    else:
        return '*/*'


def add_attachment(message, file_name, boundary):
    before = message
    try:
        mime_type = get_file_mime_type(file_name)
        message += f'--{boundary}\n'
        message += (f'Content-Disposition: attachment; \n\tfilename="{file_name}"\n' +
                    f'Content-Transfer-Encoding: base64\n' +
                    f'Content-Type: {mime_type}; \n\tname="{file_name}"\n\n')
        with open(os.path.join('attachments', file_name), 'rb') as file:
            message += fix_problems_with_points(base64.b64encode(file.read()).decode())
        message += '\n'
        return message
    except Exception:
        return before


def main():
    with open('config.json', 'rt', encoding='utf8') as file:
        config = json.loads(file.read())
    with open('text.txt', 'rt', encoding='utf8') as file:
        config['text'] = file.read()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client = ssl.wrap_socket(client)
        print(client.recv(1024))
        print(request(client, 'EHLO lo1kek12345@yandex.ru'))
        base64login = base64.b64encode(user_name.encode()).decode()

        base64password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))
        print(request(client, base64password))
        print(request(client, 'MAIL FROM:lo1kek12345@yandex.ru'))
        for receiver in config['receivers']:
            print(request(client, f'RCPT TO: {receiver}'))
        print(request(client, 'DATA'))
        print(request(client, create_message(config)))
        print(request(client, 'QUIT'))


if __name__ == '__main__':
    main()
