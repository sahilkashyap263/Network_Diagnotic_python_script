import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import TCPServer
from unittest.mock import patch

from network_checks import dns_lookup, http_check, tcp_port_check, validate_host


class TestNetworkChecks(unittest.TestCase):
    def test_validate_host_strips_whitespace(self):
        self.assertEqual(validate_host("  example.com  "), "example.com")

    def test_validate_host_rejects_url_path(self):
        with self.assertRaises(ValueError):
            validate_host("example.com/path")

    @patch("network_checks.socket.getaddrinfo")
    def test_dns_lookup_returns_unique_addresses(self, mocked_getaddrinfo):
        mocked_getaddrinfo.return_value = [
            (2, 1, 6, "", ("203.0.113.10", 0)),
            (2, 1, 6, "", ("203.0.113.10", 0)),
        ]
        result = dns_lookup("example.test")
        self.assertEqual(result.status, "PASS")
        self.assertIn("203.0.113.10", result.details)
        self.assertIn("1 address", result.summary)

    def test_tcp_check_connects_to_local_listener(self):
        server = TCPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = tcp_port_check("127.0.0.1", server.server_address[1])
            self.assertEqual(result.status, "PASS")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_http_check_reads_local_server_response(self):
        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self):
                self.send_response(200)
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/health"
            result = http_check(url)
            self.assertEqual(result.status, "PASS")
            self.assertIn("200", result.summary)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)


if __name__ == "__main__":
    unittest.main()
