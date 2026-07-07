import socket
import json
import threading

DNS_FILE = "dns_records.json"
LOCK = threading.Lock()


def register_dns_record(data):
    with LOCK:
        try:
            with open(DNS_FILE, 'r') as file:
                dns_records = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            dns_records = {}
        dns_records[data['NAME']] = {'VALUE': data['VALUE'], 'TTL': data['TTL']}
        with open(DNS_FILE, 'w') as file:
            json.dump(dns_records, file)


def registration_request(data):
    register_dns_record(data)


def dns_query(data):
    with LOCK:
        try:
            with open(DNS_FILE, 'r') as file:
                dns_records = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            dns_records = {}

    requested_record = dns_records.get(data['NAME'])
    if requested_record:
        dns_response = (
            f"TYPE=A\n"
            f"NAME={data['NAME']}\n"
            f"VALUE={requested_record['VALUE']}\n"
            f"TTL={requested_record['TTL']}"
        )
    else:
        dns_response = "TYPE=ERROR\nMESSAGE=NOT_FOUND"
    return dns_response


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('0.0.0.0', 53533))
        print("Authoritative Server is running on UDP port 53533...")

        while True:
            data, addr = udp_socket.recvfrom(1024)
            try:
                lines = data.decode().splitlines()
                if not lines:
                    continue

                header_key, header_value = lines[0].split('=', 1)

                if header_key != 'TYPE':
                    print("Malformed request, missing TYPE header:", lines)
                    continue

                if header_value == 'A':
                    registration_data = dict(
                        line.split('=', 1) for line in lines[1:] if '=' in line
                    )
                    registration_request(registration_data)
                    print("Registration successful:", registration_data)

                elif header_value == 'DNS Query':
                    query_data = dict(
                        line.split('=', 1) for line in lines[1:] if '=' in line
                    )
                    dns_response = dns_query(query_data)
                    udp_socket.sendto(dns_response.encode(), addr)
                    print("DNS Query response sent to", addr, ":", dns_response)

                else:
                    print("Unknown request type:", header_value)

            except Exception as e:
                print("Error handling request from", addr, ":", e)


if __name__ == '__main__':
    main()
