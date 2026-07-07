import socket
from flask import Flask, request, abort

app = Flask(__name__)

hostname = None
ip_address = None
as_ip = None
as_port = None


@app.route('/register', methods=['PUT'])
def register():
    global hostname, ip_address, as_ip, as_port

    data = request.json
    if not data or 'hostname' not in data or 'ip' not in data or 'as_ip' not in data or 'as_port' not in data:
        abort(400)  # bad request

    hostname = data['hostname']
    ip_address = data['ip']
    as_ip = data['as_ip']
    as_port = int(data['as_port'])

    try:
        register_with(hostname, ip_address, as_ip, as_port)
    except Exception as e:
        return str(e), 500

    return "Registration successful", 201


@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    if not hostname or not ip_address or not as_ip or not as_port:
        abort(500)

    number = request.args.get('number')
    if not number:
        abort(400)

    try:
        number = int(number)
    except ValueError:
        abort(400)

    try:
        fib_number = calc_fibonacci(number)
    except ValueError as e:
        return str(e), 400

    return str(fib_number), 200


def register_with(hostname, ip_address, as_ip, as_port):
    dns_message = f"TYPE=A\nNAME={hostname}\nVALUE={ip_address}\nTTL=103"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(dns_message.encode(), (as_ip, as_port))


def calc_fibonacci(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    if n == 1:
        return 1

    fib_sequence = [0, 1]
    for i in range(2, n + 1):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[-1]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
