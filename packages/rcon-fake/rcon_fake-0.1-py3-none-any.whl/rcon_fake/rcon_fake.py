from threading import Thread

import socket
import struct


class RCON:
    __handler = None
    __server = None
    __connections = []

    __SERVERDATA_AUTH = 3
    __SERVERDATA_AUTH_RESPONSE = 2
    __SERVERDATA_EXECCOMMAND = 2
    __SERVERDATA_RESPONSE_VALUE = 0

    def __init__(self, host="0.0.0.0", port=19132, password=None):
        self.__host = host
        self.__port = port
        self.__password = password

    def set_handler(self, handler):
        self.__handler = handler

    def start(self, threading=True):
        if self.__server:
            return
        self.__connections.clear()
        if threading:
            Thread(target=self.__run).start()
        else:
            self.__run()

    def stop(self):
        if self.__server is None:
            return
        for conn in self.__connections.copy():
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        self.__server.close()
        self.__server = None

    def __run(self):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__host, self.__port))
        self.__server.listen()
        while True:
            try:
                conn, addr = self.__server.accept()
                Thread(target=self.__session, args=(conn,)).start()
            except Exception:
                break

    def __session(self, conn):
        self.__connections.append(conn)
        authorized = False
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                request_id, request_type, payload = self.__parse_packet(data)
                if request_type == self.__SERVERDATA_AUTH:
                    if not self.__password or payload == self.__password:
                        authorized = True
                        conn.sendall(self.__construct_packet(request_id, self.__SERVERDATA_AUTH_RESPONSE, ""))
                    else:
                        conn.sendall(self.__construct_packet(-1, self.__SERVERDATA_AUTH_RESPONSE, ""))
                elif request_type == self.__SERVERDATA_EXECCOMMAND and (not self.__password or authorized):
                    try:
                        response = self.__handler(payload) if self.__handler else ""
                        response = response if response else ""
                    except Exception:
                        response = ""
                    conn.sendall(self.__construct_packet(request_id, self.__SERVERDATA_RESPONSE_VALUE, response))
                else:
                    conn.sendall(self.__construct_packet(request_id, self.__SERVERDATA_RESPONSE_VALUE, ""))
            except Exception:
                break
        conn.close()
        self.__connections.remove(conn)

    @staticmethod
    def __parse_packet(data):
        packet_size = struct.unpack('<i', data[:4])[0]
        request_id = struct.unpack('<i', data[4:8])[0]
        request_type = struct.unpack('<i', data[8:12])[0]
        payload = data[12:packet_size + 2].decode('utf-8').rstrip('\x00')
        return request_id, request_type, payload

    @staticmethod
    def __construct_packet(request_id, response_type, payload):
        payload_bytes = payload.encode('utf-8') + b'\x00\x00'
        packet_size = len(payload_bytes) + 8
        return struct.pack('<iii', packet_size, request_id, response_type) + payload_bytes
