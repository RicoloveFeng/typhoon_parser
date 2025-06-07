import socket
import sys


def send_request(message, host='localhost', port=18100,):
    """向服务器发送请求并接收响应"""
    if not message:
        return ""
    try:
        # 创建套接字并连接到服务器
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))

            # 发送消息到服务器
            client_socket.send(message.encode('utf-8'))

            # 接收服务器响应
            response = client_socket.recv(4096).decode('utf-8')
            print(f"服务器响应: {response}")
            return response

    except Exception as e:
        return message
