# HTTP Proxy Server

A simple HTTP proxy server implemented in Python.  
Supports caching, URL blocking, and traceroute functionality.

## Description

This project is a Python-based HTTP proxy server that allows you to intercept and forward HTTP requests from clients to target servers.  
It is the final project of **Data Communication Networks** course.

**Key capabilities:**

- **Forward HTTP requests**: Acts as a middleman between clients and servers.
- **Cache responses**: Stores server responses in memory to speed up repeated requests.
- **Block specific URLs**: Can block access to unwanted URLs by loading them from `blocked_urls.txt`.
- **Custom blocked page**: Shows a custom HTML page (`access_denied.html`) when a blocked URL is requested.
- **Traceroute utility**: Perform network traceroute to any target host to inspect the route packets take.
- **Multi-threaded**: Handles multiple clients concurrently using threads.
- **Interactive CLI**: Start/stop the proxy, load/clear blocked URLs, clear cache, or run traceroute via a command-line interface.

---

## Project Files

- `proxy_server.py` — Main Python server
- `report.pdf` — Project report
- `blocked_urls.txt` — Optional list of URLs to block
- `access_denied.html` — HTML page displayed for blocked URLs
- `README.md` — This file

---

## How to Run

1. Open terminal in the project folder.
2. Run the server:

```bash
python proxy.py
