import click
import os
import sys
import json
import subprocess
import shutil
import tempfile
import webbrowser
import requests
import time
from pathlib import Path
from ..utils import print_json
import socket
import random
import string
from urllib.parse import urlparse
import threading
import signal
import hashlib
import re


def create_jupyter_config(
    config_dir,
    allow_origin="https://*.amdatascience.com",
    disable_sudo=False,
):
    """
    Create a Jupyter config file with CORS settings
    """
    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Create a jupyter_server_config.py file with CORS configuration
    config_file = os.path.join(config_dir, "jupyter_server_config.py")

    sudo_config = ""
    if disable_sudo:
        sudo_config = """
# Disable sudo/root access
c.ServerApp.allow_root = False
c.ServerApp.allow_sudo = False
"""

    with open(config_file, "w") as f:
        f.write(
            f"""
# Configuration file for jupyter-server.

c = get_config()

# Configure CORS settings
c.ServerApp.allow_origin = '{allow_origin}'
c.ServerApp.allow_credentials = True
c.ServerApp.allow_methods = ['*']
c.ServerApp.allow_headers = ['Content-Type', 'Authorization', 'X-Requested-With', 
                            'X-XSRFToken', 'ngrok-skip-browser-warning', 'Origin', 
                            'Accept', 'Cache-Control', 'X-Requested-With', '*']
{sudo_config}
"""
        )

    return config_file


@click.group()
def jupyter():
    """Connect with local Jupyter Lab"""
    pass


@jupyter.command("launch")
@click.option("--port", type=int, default=8888, help="Port to run Jupyter Lab on")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option(
    "--directory", type=str, default=".", help="Directory to launch Jupyter Lab in"
)
@click.option(
    "--ngrok-port",
    type=int,
    default=None,
    help="Port for ngrok to use (defaults to same as Jupyter port)",
)
@click.option(
    "--ngrok-domain",
    type=str,
    default=None,
    help="Domain for ngrok to use (required for Pay-as-you-go plans)",
)
@click.option(
    "--ngrok-region",
    type=click.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"]),
    default="us",
    help="Region for ngrok tunnel",
)
@click.option(
    "--api-key", envvar="AMDS_API_KEY", help="API key for dashboard integration"
)
@click.option("--allow-origin", type=str, default="*", help="CORS allow-origin setting")
@click.option(
    "--disable-sudo", is_flag=True, help="Disable sudo/root permissions in the notebook"
)
@click.option(
    "--output-format",
    type=click.Choice(["standard", "minimal", "json"]),
    default="standard",
    help="Output format for command results",
)
@click.option(
    "--thumbnail",
    type=str,
    default=None,
    help="Custom thumbnail URL for dashboard display",
)
@click.pass_obj
def launch_jupyter(
    client,
    port,
    no_browser,
    directory,
    ngrok_port,
    ngrok_domain,
    ngrok_region,
    api_key,
    allow_origin,
    disable_sudo,
    output_format,
    thumbnail,
):
    """Launch a Jupyter Lab server locally with ngrok proxy and upload to dashboard.amdatascience.com"""

    # Check if jupyter is installed
    import shutil

    if not shutil.which("jupyter"):
        click.secho(
            "Error: Jupyter Lab is not installed. Please install it with:", fg="red"
        )
        click.echo("    pip install jupyterlab")
        sys.exit(1)

    # Check if ngrok is installed
    if not shutil.which("ngrok"):
        click.secho(
            "Error: ngrok is not installed. Please install it from https://ngrok.com/download",
            fg="red",
        )
        sys.exit(1)

    # Check if port is in use and find an alternative if needed
    if is_port_in_use(port):
        click.secho(f"Warning: Port {port} is already in use.", fg="yellow")
        new_port = find_free_port(port + 1)
        if new_port:
            click.secho(f"Using alternative port {new_port} instead.", fg="yellow")
            port = new_port
        else:
            click.secho(
                "Error: Could not find an available port. Please specify a different port with --port.",
                fg="red",
            )
            sys.exit(1)

    # If ngrok_port is specified, check if it's in use
    if ngrok_port and is_port_in_use(ngrok_port):
        click.secho(f"Warning: ngrok port {ngrok_port} is already in use.", fg="yellow")
        new_ngrok_port = find_free_port(ngrok_port + 1)
        if new_ngrok_port:
            click.secho(
                f"Using alternative ngrok port {new_ngrok_port} instead.", fg="yellow"
            )
            ngrok_port = new_ngrok_port
        else:
            click.secho(
                "Error: Could not find an available ngrok port. Please specify a different port with --ngrok-port.",
                fg="red",
            )
            sys.exit(1)

    # If ngrok_port is not specified, use the same as Jupyter port
    if not ngrok_port:
        ngrok_port = port

    # Create a temporary directory for Jupyter config
    jupyter_dir = tempfile.mkdtemp(prefix="jupyter-amds-")

    try:
        # Create Jupyter config with CORS settings
        config_file = create_jupyter_config(
            jupyter_dir, allow_origin, disable_sudo
        )
        click.secho(
            f"Created Jupyter config with CORS allow-origin: {allow_origin}", fg="blue"
        )
        if disable_sudo:
            click.echo(
                "Root/sudo permissions have been disabled in the notebook server"
            )

        # Start Jupyter Lab process
        click.echo(f"Starting Jupyter Lab on port {port}...")
        jupyter_cmd = [
            "jupyter",
            "lab",
            f"--port={port}",
            "--no-browser",
            f"--notebook-dir={directory}",
            "--ip=0.0.0.0",
            f"--config={config_file}",
        ]

        # Start Jupyter process
        jupyter_process = subprocess.Popen(
            jupyter_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Wait for Jupyter to start and get the token
        token = None
        jupyter_url = None
        for line in iter(jupyter_process.stderr.readline, ""):
            if "http://localhost:" in line or "http://127.0.0.1:" in line:
                # Extract just the URL part, removing the log prefix
                url_part = re.search(r"(http://[^\s]+)", line)
                if url_part:
                    jupyter_url = url_part.group(0).strip()
                    token = jupyter_url.split("token=")[-1].strip()
                    break
                else:
                    # Fallback to old method if regex fails
                    jupyter_url = line.strip().split("or ")[-1].strip()
                    token = jupyter_url.split("token=")[-1].strip()
                    break

            sys.stderr.write(line)

            if not token and "ERROR" in line:
                click.secho(
                    "Error starting Jupyter Lab. Please check the logs above.",
                    fg="red",
                    bold=True,
                )
                jupyter_process.terminate()
                sys.exit(1)

        if not token:
            click.secho(
                "Error: Could not get Jupyter token. Exiting.", fg="red", bold=True
            )
            jupyter_process.terminate()
            sys.exit(1)

        click.secho("✓ Jupyter Lab started successfully", fg="green", bold=True)

        # Short delay to ensure all output is captured
        time.sleep(0.5)

        # Start ngrok to create a tunnel
        click.secho(f"Starting ngrok tunnel to port {port}...", fg="blue", bold=True)
        ngrok_cmd = [
            "ngrok",
            "http",
            f"{port}",
            "--log=stdout",
        ]

        # Only add region if specified (since it's deprecated according to the error message)
        if ngrok_region:
            ngrok_cmd.append(f"--region={ngrok_region}")

        if ngrok_domain:
            ngrok_cmd.append(f"--domain={ngrok_domain}")
        else:
            click.secho(
                "Note: If you're using a Pay-as-you-go ngrok plan, you must specify a registered domain with --ngrok-domain",
                fg="yellow",
            )

        ngrok_process = subprocess.Popen(
            ngrok_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Wait for ngrok to start and get the public URL
        ngrok_url = None
        pay_as_you_go_error = False
        for line in iter(ngrok_process.stdout.readline, ""):
            if "url=" in line:
                ngrok_url = line.split("url=")[1].strip()
                break

            sys.stdout.write(line)

            # Check for Pay-as-you-go specific error
            if "Your account is on the 'Pay-as-you-go' plan" in line:
                pay_as_you_go_error = True

            if "error" in line.lower():
                if pay_as_you_go_error:
                    click.secho(
                        "\nError: Your ngrok account is on the Pay-as-you-go plan, which requires a registered domain.",
                        fg="red",
                        bold=True,
                    )
                    click.echo("Please follow these steps:")
                    click.echo(
                        "1. Register a domain at https://dashboard.ngrok.com/domains"
                    )
                    click.echo(
                        "2. Restart this command with the --ngrok-domain option:"
                    )
                    click.echo(
                        f"   amds jupyter launch --ngrok-domain=your-domain.ngrok.io [other options]"
                    )
                else:
                    click.echo(
                        "Error starting ngrok tunnel. Please check the logs above."
                    )

                jupyter_process.terminate()
                ngrok_process.terminate()
                sys.exit(1)

        if not ngrok_url:
            click.secho("Error: Could not get ngrok URL. Exiting.", fg="red", bold=True)
            jupyter_process.terminate()
            ngrok_process.terminate()
            sys.exit(1)

        click.secho(f"ngrok tunnel created at {ngrok_url}", fg="green")

        # Upload information to dashboard.amdatascience.com if we have an API key
        registered_server_name = None  # Store server name for cleanup later
        if api_key or client:
            click.echo("Uploading information to dashboard.amdatascience.com...")

            try:
                # Import the SDK if needed
                if not client and api_key:
                    from amds import Amds

                    client = Amds(api_key=api_key)

                if client:
                    with client as c:
                        # Create a "server" record with the local Jupyter details
                        server_name = f"local-{int(time.time())}"
                        registered_server_name = server_name  # Save for cleanup
                        environment = "local"

                        # Format data according to the expected API format
                        try:
                            # Add the integrated server using the proper API method
                            request_data = {
                                "environment": environment,
                                "server_name": server_name,
                                "token": token,
                                "url": ngrok_url,
                            }

                            # Add custom thumbnail if provided, otherwise use default
                            if thumbnail:
                                request_data["thumb"] = thumbnail
                            else:
                                # Use Jupyter's favicon as default thumbnail
                                request_data["thumb"] = (
                                    f"/images/compute_icons/amds.svg"
                                )

                            result = c.integrated_servers.add(request=request_data)

                            click.secho(
                                f"Server registered as '{server_name}'", fg="green"
                            )
                            dashboard_url = "https://dashboard.amdatascience.com"
                            click.echo(
                                f"View in dashboard: {click.style(dashboard_url, fg='bright_blue')}"
                            )
                        except Exception as e:
                            click.echo(
                                f"Warning: Could not register with dashboard: {str(e)}"
                            )
                            registered_server_name = (
                                None  # Reset if registration failed
                            )
                else:
                    click.echo(
                        "Warning: No API key provided. Skipping dashboard integration."
                    )
            except Exception as e:
                click.echo(f"Warning: Failed to connect to dashboard: {str(e)}")
                registered_server_name = None  # Reset if connection failed
        else:
            click.echo(
                "Note: No API key provided. Running without dashboard integration."
            )

        # Open browser if requested
        if not no_browser:
            if registered_server_name:
                full_url = f"https://dashboard.amdatascience.com/alph-editor/{registered_server_name}"
            else:
                full_url = f"{jupyter_url}"

            click.echo(f"Opening browser at {full_url}")
            webbrowser.open(full_url)

        # Format the output based on user preference
        if output_format == "standard":
            click.echo("\n" + "=" * 60)
            click.secho("Jupyter Lab is running", fg="green", bold=True)
            click.echo("=" * 60)
            click.echo("Local URL:     " + click.style(jupyter_url, fg="bright_blue"))
            click.echo("Public URL:    " + click.style(ngrok_url, fg="bright_blue"))
            if registered_server_name:
                alph_url = f"https://dashboard.amdatascience.com/alph-editor/{registered_server_name}"
                click.echo(
                    "Alph Editor URL: " + click.style(alph_url, fg="bright_blue")
                )
            click.echo("=" * 60)
            click.echo("\nPress Ctrl+C to stop the server...\n")
        elif output_format == "minimal":
            click.echo("Local URL: " + jupyter_url)
            click.echo("Public URL: " + ngrok_url)
            if registered_server_name:
                alph_url = f"https://dashboard.amdatascience.com/alph-editor/{registered_server_name}"
                click.echo("Alph Editor URL: " + alph_url)
            click.echo("\nPress Ctrl+C to stop the server...")
        elif output_format == "json":
            output = {
                "local_url": jupyter_url,
                "public_url": ngrok_url,
                "token": token,
            }
            if registered_server_name:
                output["alph_url"] = (
                    f"https://dashboard.amdatascience.com/alph-editor/{registered_server_name}"
                )
                output["server_name"] = registered_server_name
            print_json(output)

        # Start health check thread
        def health_checker():
            """Periodically check if services are still running"""
            while True:
                time.sleep(30)  # Check every 30 seconds
                try:
                    # Check if Jupyter is still responsive
                    if not check_jupyter_health(jupyter_url, token):
                        click.secho(
                            "Warning: Jupyter server is not responding! The application may be experiencing issues.",
                            fg="yellow",
                            bold=True,
                        )

                    # Check if ngrok is still connected
                    if not check_ngrok_health(ngrok_url):
                        click.secho(
                            "Warning: ngrok tunnel may be down! Public URL may not be accessible.",
                            fg="yellow",
                            bold=True,
                        )
                except Exception as e:
                    # Log exceptions but don't crash the monitoring thread
                    click.secho(
                        f"Warning: Health check encountered an error: {str(e)}",
                        fg="yellow",
                    )

        # Start health check in a daemon thread
        health_thread = threading.Thread(target=health_checker, daemon=True)
        health_thread.start()

        # Keep the process running until user interrupts
        try:
            jupyter_process.wait()
        except KeyboardInterrupt:
            click.secho("Shutting down...", fg="yellow")
        except Exception as e:
            click.secho(f"Error: {str(e)}", fg="red")
        finally:
            # Clean up processes
            try:
                jupyter_process.terminate()
                click.echo("Jupyter server stopped.")
            except Exception:
                pass

            try:
                ngrok_process.terminate()
                click.echo("ngrok tunnel closed.")
            except Exception:
                pass

            # Delete the integrated server record if it was registered
            if registered_server_name and (api_key or client):
                click.echo(f"Cleaning up dashboard integration...")
                try:
                    # Import the SDK if needed
                    from amds import Amds

                    # Get the API key - prioritize the directly provided one
                    cleanup_api_key = api_key
                    if not cleanup_api_key and client:
                        # Try to extract API key from client - it might be in a different location
                        # based on the SDK's structure
                        if hasattr(client, "api_key"):
                            cleanup_api_key = client.api_key
                        elif hasattr(client, "sdk_configuration") and hasattr(
                            client.sdk_configuration, "security"
                        ):
                            # Required for ephemeral client in cli
                            cleanup_api_key = client.sdk_configuration.security.api_key
                        elif hasattr(client, "_api_key"):
                            cleanup_api_key = client._api_key
                        else:
                            # Last resort - try to find any attribute that might contain the API key
                            click.echo("Debug - Client attributes: " + str(dir(client)))
                            if hasattr(client, "sdk_configuration"):
                                click.echo(
                                    "Debug - SDK config attributes: "
                                    + str(dir(client.sdk_configuration))
                                )

                    if not cleanup_api_key:
                        click.echo(
                            "Warning: Could not extract API key from client. Using environment variable."
                        )
                        # Try to get from environment
                        import os

                        cleanup_api_key = os.environ.get("AMDS_API_KEY")

                    if cleanup_api_key:
                        # Create a new client without using a context manager
                        cleanup_client = Amds(api_key=cleanup_api_key)
                        # Call delete directly without using a context manager
                        try:
                            result = cleanup_client.integrated_servers.delete(
                                server_name=registered_server_name
                            )
                            click.echo(
                                f"Server '{registered_server_name}' unregistered from dashboard"
                            )
                        except Exception as e1:
                            click.echo(f"Deletion failed: {str(e1)}")
                            click.echo(
                                "The server may need to be manually removed from the dashboard."
                            )
                    else:
                        click.echo(
                            "Warning: No API key available for cleanup. The server may need to be manually removed."
                        )
                except Exception as e:
                    click.echo(
                        f"Warning: Failed to connect to dashboard for cleanup: {str(e)}"
                    )

    except Exception as e:
        click.echo(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up temporary directory
        try:
            import shutil

            shutil.rmtree(jupyter_dir)
        except Exception:
            pass


def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_free_port(start_port, max_attempts=10):
    """Find a free port starting from start_port"""
    port = start_port
    attempts = 0

    while attempts < max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
        attempts += 1

    return None


def check_jupyter_health(jupyter_url, token):
    """Check if Jupyter server is responding properly"""
    try:
        # Extract base URL without token
        base_url = jupyter_url.split("?")[0]
        # Construct the API URL to check server status
        api_url = f"{base_url}/api/status"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        response = requests.get(api_url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_ngrok_health(ngrok_url):
    """Check if ngrok tunnel is responding properly"""
    try:
        # Add parameter to bypass ngrok browser warning
        check_url = f"{ngrok_url}?ngrok-skip-browser-warning=true"
        response = requests.get(
            check_url, timeout=5, headers={"ngrok-skip-browser-warning": "true"}
        )
        return response.status_code < 400
    except Exception:
        return False
