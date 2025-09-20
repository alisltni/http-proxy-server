'''
This project is the final project of Data Networks course in
spring semester of 2025 at Sharif University of Technology.
------------------------------------------------------------
Student name: Ali Soltani
Student ID: 403203449
E-mail: alisoltani1600@gmail.com
Instructor: Dr. Mohammad Reza Pakravan
'''

import socket
import threading
from urllib.parse import urlparse
import sys
import subprocess

# Constants
LOCAL_IP = "127.0.0.1"
LISTENING_PORT = 8080
DEFAULT_HTTP_PORT = 80

class ProxyServer():
    def __init__(self, local_ip=LOCAL_IP, listening_port=LISTENING_PORT, max_connections=100):
        self.local_ip = local_ip
        self.listening_port = listening_port
        self.max_connections = max_connections
        self.default_http_port = DEFAULT_HTTP_PORT
        self.packet_size = 4 * 1024 # 4 KB
        self.time_out = 10
        self.short_time_out = 2
        self.blocked_urls = []
        self.cache_memory = {}
        self.sock = None
        self.is_running = False
        
    def start(self):
        # Start Proxy Server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.local_ip, self.listening_port))
        self.sock.listen(self.max_connections)
        self.is_running = True

        print(f"[+] Proxy server started listening on {self.local_ip}:{self.listening_port}\n")

        try:
            while self.is_running:
                client_conn, client_addr = self.sock.accept()
                print(f"[+] Connection from {client_addr}")
                threading.Thread(target=self.handle_requests, args=(client_conn, client_addr), daemon=True).start()
        except OSError:
            pass  # Socket likely closed in stop()
        finally:
            self.stop()
            print("\n[+] Proxy server stopped.")

    def stop(self):
        # Stop Proxy Server
        if self.sock:
            self.is_running = False
            self.sock.close()           

    def handle_requests(self, client_conn, client_addr):
        remote_sock = None
        try:
            client_conn.settimeout(self.time_out)
            request = client_conn.recv(self.packet_size)
            if not request:
                return

            request_str = request.decode(errors='ignore')
            first_line = request_str.split('\r\n')[0]
            method, url, _ = first_line.split()

            # Check if URL is blocked
            if any(blocked in url for blocked in self.blocked_urls):
                print(f"[!] Blocked URL requested: {url}")
                with open("access_denied.html", "r", encoding="utf-8") as f:
                        html = f.read()

                response = (
                    "HTTP/1.1 403 Forbidden\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(html.encode())}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    f"{html}"
                )
                client_conn.sendall(response.encode())
                return

            # Parse host and port
            o = urlparse(url)
            host_name = o.hostname or '/'
            port = o.port or self.default_http_port

            # Check if the request is cached
            if url in self.cache_memory:
                response_data = self.cache_memory[url]
                for data in response_data:
                    client_conn.sendall(data)

                print(f"[+] Request from {client_addr} handled successfully using cache.")


            else:   
                # Connect to target server
                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # remote_sock.settimeout(self.time_out)
                remote_sock.connect((host_name, port))

                # Send request to server
                remote_sock.sendall(request)
                # print("Send request to server - 1")

                # Stream response to client
                response_data = []
                remote_sock.settimeout(self.short_time_out)  # short recv timeout
                while True:
                    try:
                        data = remote_sock.recv(self.packet_size)
                        # print("Receive data from server - 2")
                        if not data:
                            break
                        client_conn.sendall(data)
                        response_data.append(data)
                    except socket.timeout:
                        print("Receive timed out - assuming end of response")
                        break 

                
                print(f"[+] Request from {client_addr} handled successfully")

                # Cache the data
                self.cache_memory[url] = response_data 
            

        except Exception as e:
            print(f"[!] Error handling request from {client_addr}: {e}")
        finally:
            if remote_sock:
                remote_sock.close()
            client_conn.close()


    def block_url(self, block):
        if block:
            try:
                with open("blocked_urls.txt", "r") as f:
                    # Read and strip whitespace (e.g., newlines), ignore empty lines
                    self.blocked_urls = [line.strip() for line in f if line.strip()]
                print(f"[+] Blocked URLs loaded:")
                for url in self.blocked_urls:
                    print(url)
            except FileNotFoundError:
                print("[!] Blocked_urls.txt not found. No URLs blocked.")
                self.blocked_urls = []
        else:
            self.blocked_urls = []
            print("[+] Block URLs cleared.")
        

class Traceroute:
    def __init__(self, target=None, hop=None):
        self.target = target
        self.hop = hop

    def set_values(self, target, hop):
        self.target = target.strip()
        self.hop = hop

    def run(self):
        # print(f"[+] Tracingrout to {self.target} over a maximum of {self.hop} hops.")
        command = f"tracert -h {self.hop} {self.target}"

        try:
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"[!] Traceroute failed: {e}")


if __name__ == '__main__':

    proxy = ProxyServer()
    tracer = Traceroute()
    proxy_thread = None

    print("Enter your command:")

    while True:
        try:
            cmd = input(">> ")

            if cmd == 'Start Proxy':
                if proxy_thread and proxy_thread.is_alive():
                    print("[!] Proxy is already running.")
                else:
                    proxy_thread = threading.Thread(target=proxy.start, daemon=True)
                    proxy_thread.start()
                    print("[+] Proxy server started.")

            elif cmd == 'Stop Proxy':
                if proxy.is_running:
                    proxy.stop()
                else:
                    print("[!] Proxy is not running.")

            elif cmd == 'Load Blocked URLs':
                proxy.block_url(True)

            elif cmd == 'Clear Blocked URLs':
                proxy.block_url(False)

            elif cmd == 'Clear Cache':
                proxy.cache_memory.clear()
                print("[+] Cach cleared.")             

            elif cmd == 'Run traceroute':
                target = input("Enter target: ")
                hop = input("Enter number of hops: ")
                tracer.set_values(target, hop)
                tracer.run()

            else:
                print("[!] Invalid command.")

        except KeyboardInterrupt:
            print("\n[!] Keyboard interrupt received.")
            if proxy.is_running:
                proxy.stop()
            break


