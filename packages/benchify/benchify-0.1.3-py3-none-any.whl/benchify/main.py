"""
exposes the API for benchify
"""

import requests
import webbrowser
import os
import tarfile
import typer
from urllib.parse import urlencode
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .auth import save_token, load_token, get_token_file_path
from .repo import get_repo_name_and_owner, is_benchify_initialized
from .server import start_server_in_background
from .constants import (
    CONFIG_DIR_PATH, 
    TAR_FILE_PATH, 
    AUTH_URL, 
    API_URL_GET_METADATA, 
    API_URL_CONFIG,
    Command,
    HTTPMethod
)

app = typer.Typer(
    help="A CLI tool for managing Benchify authentication and configuration tasks.")

def make_request(method: HTTPMethod, url: str, token: str, body: dict = None):
    """
    Make an HTTP request with the specified method, URL, token, and optional body.

    :param method: HTTP method to use (e.g., "GET", "POST", etc.)
    :param url: The URL to send the request to
    :param token: The authorization token for the request
    :param body: The request body (optional, defaults to None)
    :return: Parsed JSON response or None if parsing fails
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.request(method=method.value, url=url, headers=headers, json=body)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()  # Parse the JSON response
        return response_json
    except ValueError:
        print("Failed to parse response as JSON.")
        exit(1)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        exit(1)
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)


def generate_benchify_tar():
    console = Console()
    try:
        with tarfile.open(TAR_FILE_PATH, "w:gz") as tar:
            tar.add(CONFIG_DIR_PATH, arcname=".")
    except Exception as e:
        console.print("[bold red]Failed to generate benchify.tar[/bold red]")
        exit(1)


def upload_to_s3(upload_url):
    try:
        with open(TAR_FILE_PATH, "rb") as f:
            headers = {'Content-Type': 'application/octet-stream'}
            response = requests.put(upload_url, data=f, headers=headers)
            if response.status_code == 200:
                os.remove(TAR_FILE_PATH)
                return True
            else:
                print("Failed to upload test configuration")
                exit(1)
    except Exception:
        print("Failed to upload test configuration")
        exit(1)


def download_and_extract_from_s3(url: str):
    # Step 1: Download the file from the S3 URL
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
    
    # Step 2: Save the downloaded file as a temporary tar file
    with open(TAR_FILE_PATH, "wb") as tar_file:
        for chunk in response.iter_content(chunk_size=8192):  # Stream the file content
            tar_file.write(chunk)
    
    # Step 3: Extract the tar file to the specified output directory
    os.makedirs(CONFIG_DIR_PATH, exist_ok=True)  # Create the output directory if it doesn't exist
    with tarfile.open(TAR_FILE_PATH, "r") as tar:
        tar.extractall(path=CONFIG_DIR_PATH)
    
    # Step 4: Optionally, clean up the tar file after extraction
    os.remove(TAR_FILE_PATH)


def login():
    try:
        # Start the server in the background
        if os.path.exists(get_token_file_path()):
            print(f"You are already logged in. If you'd like to log in again, please log out first (benchify {Command.LOGOUT.value}).")
            exit(0)
        try:
            port, server_instance, JWTHandler = start_server_in_background()
        except Exception:
            print("Failed to start the authentication server.")
            exit(1)

        # Query parameters
        query_params = {"port": port}

        # Construct the URL
        try:
            auth_url = AUTH_URL + urlencode(query_params)
        except Exception:
            print("Failed to construct the authentication URL.")
            exit(1)

        try:
            webbrowser.open(auth_url)
        except Exception:
            print('Navigate to:', auth_url)
        print("Waiting for authentication...")
        # Wait for the JWT to be received with a timeout
        if not JWTHandler.jwt_received.wait(timeout=300):  # 5-minute timeout
            print("Authentication timed out. Please try again.")
            exit(1)

        jwt_value = JWTHandler.jwt_value

        # Save the token
        try:
            save_token(jwt_value)
        except Exception:
            print("Failed to save the authentication token.")
            exit(1)
        
        print("Authentication successful.")

    except Exception:
        print("An unexpected error occurred. Please try again later.")
    finally:
        # Ensure the server is shut down properly
        try:
            server_instance.shutdown()
            server_instance.server_close()
        except Exception:
            pass


def logout():
    try:
        if not os.path.exists(get_token_file_path()):
            print("You are not logged in.")
            return
        os.remove(get_token_file_path())
        print("You have successfully logged out.")
    except Exception:
        print("An unexpected error occurred. Please try again later.")
        exit(1)


def init_config():
    console = Console()
    token = load_token()
    if not token:
        console.print("[bold red]Please log in to proceed.[/bold red]")
        exit(1)
    
    if is_benchify_initialized():
        console.print(Panel(
            Text("A Benchify configuration already exists. If you wish to reinitialize, please remove the '.benchify' directory and try again.",
                 style="yellow"),
            border_style="yellow"
        ))
        exit(1)

    owner, repo_name = get_repo_name_and_owner()
    
    console.print(Panel(
        Text(f"Initializing Benchify for repository: {repo_name} owned by {owner}",
             style="cyan"),
        border_style="cyan"
    ))
    
    console.print("[bold blue]Getting metadata...[/bold blue]")
    metadata = get_metadata()
    console.print("[bold green]✓ Metadata received[/bold green]")
    
    body = {
        "runId": metadata['runId'],
        "type": "INIT"
    }
    
    console.print("[bold blue]Sending request and waiting for response (this may take up to 15 minutes)...[/bold blue]")
    response_json = make_request(method=HTTPMethod.POST, token=token, url=API_URL_CONFIG, body=body)
    
    if 'downloadUrl' in response_json:
        console.print("[bold blue]Downloading configuration...[/bold blue]")
        download_and_extract_from_s3(response_json['downloadUrl'])
        console.print("[bold green]✓ Configuration downloaded and extracted successfully[/bold green]")
    else:
        console.print("[bold red]Failed to download configuration[/bold red]")
        exit(1)
    
    # Display feedback from response
    display_feedback(response_json)

def display_feedback(response_json):
    console = Console()
    
    if 'feedback' not in response_json:
        return
        
    feedback = response_json['feedback']
    
    if 'message' in feedback:
        console.print(Panel(
            Text(feedback['message'], style="bold green"),
            title="Feedback",
            border_style="green"
        ))
        
    if 'debugData' in feedback and feedback['debugData']:
        if isinstance(feedback['debugData']['summary'], list) and len(feedback['debugData']['summary']) > 0:
            console.print("\n[bold]Summary:[/bold]")
            for item in feedback['debugData']['summary']:
                console.print(f"• {item}")

        if 'test_results' in feedback['debugData']:
            console.print("\n\n[bold]📖 What failed files mean?[/bold]")
            console.print("Tests cannot be executed for the failed files, but we will proceed with testing all passing files. If the failed files are not important, you can ignore them. However, if you need them tested, here is the detailed error output for debugging.")
 
        if 'test_results' in feedback['debugData'] and feedback['debugData']['test_results']:
            console.print("\n[bold blue]Test Results:[/bold blue]")
            for result in feedback['debugData']['test_results']:
                if 'error_message' in result and result['error_message']:
                    console.print(Panel(
                        Text(result['error_message'], style="red"),
                        title=f"Error in {result['file']}",
                        border_style="red"
                    ))

def test_config():
    console = Console()
    token = load_token()
    if not token:
        console.print("[bold red]Please log in to proceed.[/bold red]")
        exit(1)
    
    if not is_benchify_initialized():   
        console.print(Panel(
            Text("No Benchify configuration found. You can initialize a new configuration by running the setup process.",
                 style="yellow"),
            border_style="yellow"
        ))
        exit(1)

    console.print("[bold blue]Generating configuration archive...[/bold blue]")
    generate_benchify_tar()
    console.print("[bold green]✓ Successfully generated benchify.tar[/bold green]")
    
    console.print("[bold blue]Getting metadata...[/bold blue]")
    metadata = get_metadata()
    console.print("[bold green]✓ Metadata received[/bold green]")
    
    console.print("[bold blue]Uploading configuration...[/bold blue]")
    upload_to_s3(metadata['uploadUrl'])
    console.print("[bold green]✓ Configuration uploaded successfully[/bold green]")

    body = {
        "runId": metadata['runId'],
        "type": "TEST"
    }
    
    console.print("[bold blue]Sending request and waiting for response (this may take up to 15 minutes)...[/bold blue]")
    response_json = make_request(method=HTTPMethod.POST, token=token, url=API_URL_CONFIG, body=body)
    display_feedback(response_json)


def get_metadata():
    token = load_token()
    if not token:
        print('You must first log in.')
        exit(1)
    owner, repo_name = get_repo_name_and_owner()
    body = {
        "repoOwner": owner,
        "repoName": repo_name
    }
    response_json = make_request(method=HTTPMethod.GET, token=token, url=API_URL_GET_METADATA, body=body)
    return response_json

@app.command(name=Command.LOGIN.value, help="Log in Benchify.")
def login_command():
    login()

@app.command(name=Command.LOGOUT.value, help="Log out of Benchify.")
def logout_command():
    logout()

@app.command(name=Command.INIT.value, help="Initialize the configuration.")
def init_command():
    init_config()

@app.command(name=Command.TEST.value, help="Test the existing .benchify configuration.")
def test_command():
    test_config()

if __name__ == "__main__":
    app()
