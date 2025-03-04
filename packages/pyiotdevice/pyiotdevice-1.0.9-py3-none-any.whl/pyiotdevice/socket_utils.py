import logging
import socket

from .custom_exceptions import CommunicationErrorException, InvalidDataException

_LOGGER = logging.getLogger(__name__)

# Define default port for ac communication
DEFAULT_PORT = 15914

def check_not_found_case(response: str) -> bool:
    """
    Check if the response indicates a 'not found' case.

    Args:
        response (str): The HTTP response string.

    Returns:
        bool: True if the response does not contain "404 Not Found", False otherwise.
    """
    return "404 Not Found" not in response

def send_http_request(ip_address: str, port: int = DEFAULT_PORT, request_str: str = "", timeout: int = 20):
    """
    Send an HTTP request over a TCP connection and return the parsed response.

    Args:
        ip_address (str): The IP address of the server.
        port (int): The port to connect to.
        request_str (str): The HTTP request string.
        timeout (int): The connection timeout in seconds (default is 20).

    Returns:
        tuple: A tuple containing the headers (str) and body (str) of the HTTP response.

    Raises:
        InvalidDataException: If the response contains a 404 status code or has an invalid format.
        Exception: For other unexpected errors during the connection or response handling.
    """
    try:
        # Open a TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            _LOGGER.debug(f"Connecting to {ip_address}:{port}...")
            client.connect((ip_address, port))

            # Send the HTTP request
            logging.debug("Sending request...")
            client.sendall(request_str.encode('utf-8'))

            # Receive the response
            _LOGGER.debug("Receiving response...")
            response_data = client.recv(1024).decode('utf-8')

        # Check if the response indicates a "not found" case
        if not check_not_found_case(response_data):
            _LOGGER.error("Received 404 Not Found in response.")
            raise InvalidDataException()

        # Parse the response
        response_parts = response_data.split("\r\n\r\n")
        if len(response_parts) < 2:
            _LOGGER.error("Invalid HTTP response format.")
            raise InvalidDataException()

        headers, body = response_parts[0], response_parts[1]
        # logging.debug(f"Headers: {headers}")
        # logging.debug(f"Body: {body}")

        return headers, body

    except socket.timeout:
        _LOGGER.error(f"Connection to {ip_address}:{port} timed out.")
        raise
    except Exception as e:
        _LOGGER.error(f"Error sending request to {ip_address}:{port}: {e}")
        raise
