import click
import sys
import os
import requests
import shutil
import zipfile
import sseclient
from datetime import datetime

from tabulate import tabulate

from primeway.constants import BASE_BACKEND_URL


def get_api_token():
    # Retrieve API token from environment variable or config file
    token = os.environ.get('PRIMEWAY_API_TOKEN', 'primeway-8diat6yqt9mwWB3mGrrjUA')
    if not token:
        raise ValueError("The 'PRIMEWAY_API_TOKEN' is missing from the environment variables.")

    return token


@click.command('list')
@click.option('--status', type=click.Choice(['running', 'completed', 'pending', 'failed']), help='Filter jobs by status.')
def list_jobs(status):
    """List jobs with optional status and pipeline execution ID filters."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status
        
    response = requests.get(f'{BASE_BACKEND_URL}/jobs', headers=headers, params=params)
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            headers_list = ['Job ID', 'Name', 'Type', 'Created', 'Build Status', 'Last Status', 'Last Start', 'Last End', 'Last Status' 'GPU Types']
            table_data = []

            for job in jobs:
                job_id = job['job_id']
                job_name = job['job_name']
                job_type = job['job_type']
                build_status = job['build_status']
                dt = datetime.fromisoformat(job['created_at'].replace('Z', '+00:00'))
                formatted_created_at = dt.strftime('%Y-%m-%d %H:%M:%S')

                exec_status = job.get('status', "Hasn't started")
                start_time = job.get('last_execution_start_time', '')[:19]  if job.get('last_execution_start_time') else ''
                end_time = job.get('last_execution_end_time', '')[:19] if job.get('last_execution_end_time') else ''
                last_status = job.get('last_execution_status', '')[:19] if job.get('last_execution_status') else ''
                gpu_type = job.get('gpu_type') or {}
                gpu_type_str = ', '.join([f"{k}: {v}" for k, v in gpu_type.items()])

                row = [
                    job_id,
                    job_name,
                    job_type,
                    formatted_created_at,
                    build_status,
                    exec_status,
                    start_time,
                    end_time,
                    last_status,
                    gpu_type_str
                ]
                table_data.append(row)

            print(tabulate(table_data, headers=headers_list, tablefmt='grid'))
        else:
            print("No jobs found.")
    else:
        print(f"Error retrieving jobs: {response.text}")


@click.command('executions')
@click.argument('job_id', required=True)
@click.option('--status', help='Filter executions by status.')
def list_executions(job_id, status=None):
    """List all executions for a given job_id, optionally filtered by status."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/executions', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        job_type = data.get('job_type', '')
        if job_type == "deploy":
            column_type = "Deploy"
        else:
            column_type = "Run"

        executions = data.get('executions', [])
        if executions:
            header_execution_id = f'{column_type} Execution ID' if job_type else 'Execution ID'
            # Collect data into a list of rows
            table_data = []
            for execution in executions:
                execution_id = execution.get('job_execution_id')
                exec_status = execution.get('status')
                dt = datetime.fromisoformat(execution['created'].replace('Z', '+00:00'))
                formatted_created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                start_time = execution.get('start_time', '')[:19] if execution.get('start_time', '') else ''
                end_time = execution.get('end_time', '')[:19] if execution.get('end_time') else ''
                gpu_info = execution.get('gpu_info', {})
                if job_type == "deploy":
                    health_status = execution.get('health_status')
                    proxy_url = execution.get('proxy_url')
                gpu_info_str = ', '.join([f"{k}: {v}" for k, v in gpu_info.items()])
                if job_type != "deploy":
                    table_data.append([
                        execution_id,
                        exec_status,
                        start_time,
                        end_time,
                        gpu_info_str
                    ])
                    # Prepare headers
                    headers = [header_execution_id, 'Status', 'Created', 'Start Time', 'End Time', 'GPU Info']
                else:
                    table_data.append([
                        execution_id,
                        exec_status,
                        formatted_created_at,
                        health_status,
                        proxy_url,
                        start_time,
                        end_time,
                        gpu_info_str
                    ])
                    # Prepare headers
                    headers = [header_execution_id, 'Status', 'Health', "Url", 'Start Time', 'End Time', 'GPU Types']
            # Print table using tabulate
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        else:
            print("No executions found for this job.")
    else:
        print(f"Error retrieving executions: {response.text}")


@click.command('info')
@click.argument('job_id', required=True)
def get_job_info(job_id):
    """Retrieve information about a job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}', headers=headers)
    if response.status_code == 200:
        job_data = response.json()
        config = job_data.get('config', {})  # Access the config dictionary
        job_type = job_data.get('job_type')

        # Display base job information
        print("\nJob Config:")
        print(f"Job ID          : {job_data.get('job_id')}")
        print(f"Job Type        : {job_type}")
        print(f"Build status    : {job_data.get('build_status')}")
        print(f"Job Name        : {config.get('job_name')}")
        print(f"Created At      : {job_data.get('created_at')}")
        print(f"Docker Image    : {config.get('docker_image')}")
        print(f"GPU Types       : {config.get('gpu_types')}")
        print(f"Disk Space      : {config.get('disk_space')}")
        print(f"Environment     : {config.get('env')}")
        print(f"Requirements    : {config.get('requirements')}")
        print(f"Apt packages    : {config.get('apt_packages')}")

        # If there are specific fields related to deploy jobs, handle them
        if job_type == 'deploy':
            print("\nDeploy Job Specific Parameters:")
            print(f"Idle Timeout    : {config.get('idle_timeout')}")
            print(f"Schedule        : {config.get('schedule')}")
            print(f"Health Endpoint : {config.get('health_endpoint')}")
            print(f"Port            : {config.get('port')}")
        # Handle other job types if necessary

    else:
        print(f"Error retrieving job information: {response.text}")

if __name__ == '__main__':
    get_job_info()

@click.command('buildlogs')
@click.argument('job_id', required=True)
def get_buildjob_logs(job_id):
    """Retrieve and display logs for a job or job execution."""
    if not job_id:
        click.echo("Please provide job id")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Fetch logs from the API
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/build-logs', headers=headers)
    if response.status_code == 200:
        logs = response.json().get('build_logs', '')
        click.echo(logs)
    else:
        click.echo(f"Error retrieving logs: {response.text}")
        sys.exit(1)


@click.command('logs')
@click.option('--job-id', help='The ID of the job.')
@click.option('--job-execution-id', help='The ID of the job execution.')
@click.option('--follow', is_flag=True, help='Stream the logs in real time.')
def get_job_logs(job_id, job_execution_id, follow):
    """Retrieve and display logs for a job or job execution."""
    if not job_id and not job_execution_id:
        click.echo("Please provide either --job-id or --job-execution-id.")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Prepare query parameters
    params = {'follow': 'true' if follow else 'false'}
    if job_id:
        params['job_id'] = job_id
    elif job_execution_id:
        params['job_execution_id'] = job_execution_id

    # Fetch logs from the API
    response = requests.get(f'{BASE_BACKEND_URL}/job-logs', headers=headers, params=params, stream=True)
    if response.status_code == 200:
        if follow:
            # Stream logs using sseclient
            client = sseclient.SSEClient(response)
            for event in client.events():
                click.echo(event.data)
        else:
            logs = response.json().get('logs', '')
            click.echo(logs)
    else:
        click.echo(f"Error retrieving logs: {response.text}")
        sys.exit(1)


@click.command('artifacts')
@click.option('--job-id', help='The ID of the job.')
@click.option('--job-execution-id', help='The ID of the job execution.')
@click.option('--output-dir', type=click.Path(), help='Directory to save artifacts.')
def get_job_artifacts(job_id, job_execution_id, output_dir):
    """Retrieve artifacts for a job or job execution and save them to a directory."""
    if not job_id and not job_execution_id:
        click.echo("Please provide either --job-id or --job-execution-id.")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Prepare query parameters
    params = {}
    if job_id:
        params['job_id'] = job_id
    elif job_execution_id:
        params['job_execution_id'] = job_execution_id

    # Fetch artifacts from the API
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/artifacts', headers=headers, params=params, stream=True)
    if response.status_code == 200:
        # Retrieve the job_execution_id from the Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        filename = ''
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
            job_execution_id_in_filename = filename.replace('artifacts_', '').replace('.zip', '')
        else:
            job_execution_id_in_filename = job_execution_id or 'unknown'

        # Determine the output directory
        if output_dir:
            dir_path = os.path.abspath(output_dir)
        else:
            base_dir_name = f"primeway-artifacts-{job_execution_id_in_filename}"
            dir_path = base_dir_name
            counter = 1
            while os.path.exists(dir_path):
                dir_path = f"{base_dir_name}-{counter}"
                counter += 1
            dir_path = os.path.abspath(dir_path)

        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)

        # Download and extract the zip file
        zip_file_path = os.path.join(dir_path, f'artifacts.zip')
        with open(zip_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        # Extract the zip file into the directory
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(dir_path)

        # Remove the zip file after extraction
        os.remove(zip_file_path)

        click.echo(f"Artifacts downloaded and extracted to: {dir_path}")
    else:
        click.echo(f"Error retrieving artifacts: {response.text}")
        sys.exit(1)
