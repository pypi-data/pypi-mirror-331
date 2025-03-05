import requests
import zipfile
import io

class QuanfluenceClient:
    """
    A Python client for interacting with the Quanfluence Gateway APIs.
    This class includes methods for signing up, signing in, verifying users, and managing devices.
    """

    def __init__(self):
        """
        Initializes the API client with the base URL.

        :param base_url: The base URL of the Quanfluence Gateway API.
        """
        self.base_url = "http://quan-gateway.ap-south-1.elasticbeanstalk.com"
        self.access_token = None

    def signin(self, username, password):
        """
        Authenticates a user and retrieves an access token.

        :param username: The username of the user.
        :param password: The password of the user.
        :return: The API response with the access token.
        """
        url = f"{self.base_url}/api/clients/signin"
        payload = {
            "username": username,
            "password": password,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json().get("data")
            self.access_token = data["token"]
        return response.json()

    def create_device(self, title, description, type, public_ipv4_address = None, private_ipv4_address = None, iters = 100, runs = 5, alpha = 1.0, beta = 1.0, beta_decay = 0.99, noise_stdev = 0.1, runtime = 0, trials = 1):
        """
        Creates a new device configuration.

        :param title: The title of the device.
        :param description: The description of the device.
        :param type: The type of the device (local or remote).
        :param public_ipv4_address: The public IPv4 address of the device.
        :param private_ipv4_address: The private IPv4 address of the device.
        :param iters: The number of iterations for the device.
        :param runs: The number of runs for the device.
        :param alpha: The alpha parameter for the device.
        :param beta: The beta parameter for the device.
        :param beta_decay: The beta decay parameter for the device.
        :param noise_stdev: The noise standard deviation for the device.
        :param runtime: The runtime for the device.
        :return: The API response.
        """
        url = f"{self.base_url}/api/devices"
        headers = self._get_auth_headers()
        device_details = {
            "title": title,
            "description": description,
            "type": type,
            "public_ipv4_address": public_ipv4_address,
            "private_ipv4_address": private_ipv4_address,
            "iters": iters,
            "runs": runs,
            "alpha": alpha,
            "beta": beta,
            "beta_decay": beta_decay,
            "noise_stdev": noise_stdev,
            "runtime": runtime,
            "trials": trials,
        }
        response = requests.post(url, json=device_details, headers=headers)
        return response.json().get("data")

    def get_device(self, device_id):
        """
        Retrieves details of a specific device.

        :param device_id: The ID of the device to retrieve.
        :return: The API response.
        """
        url = f"{self.base_url}/api/devices/{device_id}"
        headers = self._get_auth_headers()
        response = requests.get(url, headers=headers)
        resp = response.json()
        if resp.get("status") == "success":
            return resp.get("data")
        else:
            raise Exception(resp.get("message"))

    def update_device(self, device_id, updates):
        """
        Updates details of an existing device.

        :param device_id: The ID of the device to update.
        :param updates: A dictionary with updated details.
        :return: The API response.
        """
        url = f"{self.base_url}/api/devices/{device_id}"
        headers = self._get_auth_headers()
        response = requests.put(url, json=updates, headers=headers)
        return response.json().get("data")
    
    def upload_device_qubo(self, device_id, filepath):
        """
        Uploads a QUBO file to a specific device.

        :param device_id: The ID of the device to upload the QUBO.
        :param filename: The filename of the QUBO file.
        :return: The API response.
        """
        url = f"{self.base_url}/api/devices/{device_id}/qubo/upload"
        headers = self._get_auth_headers()
        files = {'file': open(filepath, 'rb')}
        response = requests.post(url, files=files, headers=headers)
        return response.json().get("data")
    
    def execute_device_qubo_input(self, device_id, qubo):
        """
        Executes a QUBO on a specific device.

        :param device_id: The ID of the device to execute the QUBO.
        :param qubo: The QUBO to execute.
        :return: The API response.
        """
        url = f"{self.base_url}/api/execute/device/{device_id}"
        headers = self._get_auth_headers()
        Q_str = str(qubo)
        # Create an in-memory ZIP file
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("data.txt", Q_str)  # Store as a text file
        buffer.seek(0)
        files = {"file": ("data.zip", buffer, "application/zip")}
        response = requests.post(url, files=files, headers=headers)
        return response.json().get("data")
    
    def execute_device_qubo_file(self, device_id, filename):
        """
        Executes a QUBO on a specific device.

        :param device_id: The ID of the device to execute the QUBO.
        :param qubo: The QUBO to execute.
        :return: The API response.
        """
        url = f"{self.base_url}/api/execute/device/{device_id}/qubo/{filename}"
        headers = self._get_auth_headers()
        response = requests.get(url, headers=headers)
        return response.json().get("data")

    def _get_auth_headers(self):
        """
        Internal method to construct headers with the authorization token.

        :return: A dictionary containing the Authorization header.
        """
        if not self.access_token:
            raise ValueError("Access token is missing. Please sign in first.")
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

