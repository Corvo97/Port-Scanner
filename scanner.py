'''-------------------------------
Simple Python TCP Port scaner
----------------------------------
By: dev.corvo
Discord: dev.corvo
GitHub: https://github.com/Corvo97

--------------------------------'''

import socket
import argparse
import datetime
import threading
import ipaddress


# Custom exception for invalid range
class RangeError(Exception):
    def __init__(self, range):
        super().__init__(f'Invalid range {range}')


# Custom exception for invalid address
class AddressError(Exception):
    def __init__(self, address):
        super().__init__(f'Address "{address}" not found.')


def screen(func: callable) -> None:
    """
    Decorator function to display execution time and scan result.

    Args:
    - func (callable): The function to be decorated.

    Returns:
    - None
    """
    def wrapper(address: str, scan_range: list) -> any:
        print('Please wait...')
        start = datetime.datetime.now()
        if func(address, scan_range):
            for r in func(address, scan_range): print(f'{r} Open')
        else: print('No open ports')
        print(f'Done! ({(datetime.datetime.now() - start).total_seconds()} seconds)')
    return wrapper


def host_check(address: str) -> str:
    """
    Check if the provided address is a valid IP address or resolves to a valid.

    Args:
    - address (str): The address to be checked.

    Returns:
    - str: The validated IP address.
    """
    try:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise AddressError(address)
    except ValueError:
        try:
            return socket.gethostbyname(address)
        except socket.gaierror:
            raise AddressError(address)
    return address


def port_list(s_range: list) -> list:
    """
    Generates a list of ports based on the provided range.

    Args:
    - s_range (List[str]): The range of ports (1 - 65535).

    Returns:
    - List[int]: List of ports.
    """
    match len(s_range):
        case 1:
            return [int(s_range[0])]
        case 2:
            return [p for p in range(int(s_range[0]), int(s_range[1]) + 1)]
        case _:
            raise RangeError(s_range)


@screen
def scan_ports(address: str, scan_range: list) -> str:
    """
    Scans ports in the specified range for the given address.

    Args:
    - address (str): Target address.
    - scan_range (List[int]): Range of ports to scan.

    Returns:
    - List[int]: List of open ports.
    """
    open_ports = []
    def scan_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((address, port))
            open_ports.append(port)
        except ConnectionRefusedError: pass
        except socket.timeout: pass
        except: pass
        finally: sock.close()

    threads = []
    for r in scan_range:
        thread = threading.Thread(target=scan_port, args=(r, ))
        threads.append(thread)
        thread.start()
    for thread in threads: thread.join()
    return open_ports


def main() -> None:
    """
    Main function to parse command line arguments and initiate the port scanning.
    
    Returns:
    - None
    """
    parser = argparse.ArgumentParser(description='Simple Port scaner')
    parser.add_argument('address', help='Server address')
    parser.add_argument('range', help='Port or range (1 - 65535)')
    args = parser.parse_args()

    try:
        if host_check(args.address):
            scan_ports(args.address, port_list(args.range.split('-')))

    except ValueError: print('Int numbers only.')
    except RangeError as e: print(e)
    except AddressError as e: print(e)


if __name__ == '__main__':
    main()
