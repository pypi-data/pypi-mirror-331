import click
import os
import tempfile
import shutil
import requests
import yaml
import fnmatch

from primeway.utils import zip_directory
from primeway.constants import BASE_BACKEND_URL

@click.command("job")
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help="Path to the YAML configuration file.")
@click.option('--run', is_flag=False, help='Execute immediately.')
def create_job(config, run):
    with open(config, 'r') as file:
        config_data = yaml.safe_load(file)

    if 'primeway_api_token' not in config_data:
        # Try to get the token from the environment variable
        token = os.environ.get('PRIMEWAY_API_TOKEN')
        if token:
            config_data['primeway_api_token'] = token
            # Optionally, save the updated config_data back to the config file
            with open(config, 'w') as file:
                yaml.safe_dump(config_data, file)
        else:
            raise ValueError("The 'primeway_api_token' is missing from both the configuration file and the environment variables.")

    headers = {
        'Authorization': f'Bearer {config_data["primeway_api_token"]}'
    }

    params = {'run': 'true' if run else 'false'}

    backend_url = f"{BASE_BACKEND_URL}/create-job"

    config_dir = os.path.dirname(os.path.abspath(config))

    if config_data.get("context"):
        ignore_patterns = config_data.get('ignore_patterns', [])
        context_relative_path = config_data["context"]
        print("context_relative_path", context_relative_path)
        context_path = os.path.abspath(os.path.join(config_dir, context_relative_path))
        print("context_path", context_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, 'project.zip')
            config_file_path = os.path.join(temp_dir, 'config.yaml')

            # Write the modified config_data to this file
            with open(config_file_path, 'w') as f:
                yaml.safe_dump(config_data, f)

            # Copy the contents of the context directory directly
            for item in os.listdir(context_path):
                s = os.path.join(context_path, item)
                d = os.path.join(temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, ignore=shutil.ignore_patterns(*ignore_patterns))
                else:
                    if not any(fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
                        shutil.copy2(s, d)

            print(f"os.listdir(temp_dir): {os.listdir(temp_dir)}")
            # Zip the temp_dir excluding any additional ignore patterns
            zip_directory(temp_dir, zip_file_path, ignore_patterns + ['project.zip'])

            with open(config_file_path, 'rb') as config_file, open(zip_file_path, 'rb') as project_file:
                files = {
                    'config_file': ('config.yaml', config_file, 'application/x-yaml'),
                    'project_file': ('project.zip', project_file, 'application/zip')
                }

                # Submit the deployment to the backend
                with requests.post(backend_url, headers=headers, params=params, files=files) as response:
                    if response.status_code == 200:
                        print(response.json())
                    else:
                        print(f"Failed to submit deployment: {response.text}")
    else:
        # No context provided, send only the config file
        with open(config, 'rb') as config_file:
            files = {
                'config_file': ('config.yaml', config_file, 'application/x-yaml'),
            }

            # Submit the deployment to the backend
            with requests.post(backend_url, headers=headers, params=params, files=files) as response:
                if response.status_code == 200:
                    print(response.json())
                else:
                    print(f"Failed to submit deployment: {response.text}")

if __name__ == '__main__':
    create_job()