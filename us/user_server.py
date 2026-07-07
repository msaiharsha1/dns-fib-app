import socket
from flask import Flask, request, abort
import requests

app = Flask(__name__)


@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    if not all([hostname, fs_port, number, as_ip, as_port]):
        abort(400)

    try:
        ip_address = resolve_hostname(hostname, as_ip, int(as_port))
    except Exception as e:
        return str(e), 500

    try:
        fibonacci_number = query_server(ip_address, fs_port, number)
    except Exception as e:
        return str(e), 500

    return str(fibonacci_number), 200


def resolve_hostname(hostname, as_ip, as_port, timeout=3):
    """Ask the Authoritative Server for the IP of `hostname` over UDP."""
    query_message = f"TYPE=DNS Query\nNAME={hostname}"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.settimeout(timeout)
        udp_socket.sendto(query_message.encode(), (as_ip, as_port))
        try:
            data, _ = udp_socket.recvfrom(1024)
        except socket.timeout:
            raise Exception(f"Timed out resolving hostname {hostname}")

    response = data.decode()
    fields = dict(line.split('=', 1) for line in response.splitlines() if '=' in line)

    if fields.get('TYPE') != 'A' or 'VALUE' not in fields:
        raise Exception(f"Failed to resolve hostname {hostname}: {response}")

    return fields['VALUE']


def query_server(ip_address, fs_port, number):
    response = requests.get(f'http://{ip_address}:{fs_port}/fibonacci?number={number}')
    if response.status_code != 200:
        raise Exception(f"Failed to get Fibonacci number from server {ip_address}: {response.text}")
    return response.text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
