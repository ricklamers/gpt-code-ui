import boto3
import subprocess
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

secrets_manager_client = boto3.client(
    service_name='secretsmanager'
)
def get_private_key_from_s3(bucket_ssh_keys_name: str, bucket_private_key_path: str) -> str:
    response = s3_client.get_object(Bucket=bucket_ssh_keys_name,
                                    Key=bucket_private_key_path)
    content = response['Body'].read()
    return content.decode("utf-8")


def create_private_key_pem_file(private_key_pem: str) -> None:
    file = open('private_key.pem', 'w')
    file.write(private_key_pem)
    file.close()
    subprocess.call(['chmod', '0600', 'private_key.pem'])

def get_instances(environment: str, application: str) -> list:
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:application',
                'Values': [application]
            },
            {
                'Name': 'tag:environment',
                'Values': [environment]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
    return instances

def deploy(private_ip_address: str, application: str) -> None:
    subprocess.check_call(
        f"ssh -i private_key.pem -o StrictHostKeyChecking=no ubuntu@{private_ip_address} "
        f"'sudo mkdir -p /home/ubuntu/{application}'",
        shell=True)

    subprocess.check_call(
        f"rsync -ravhe 'ssh -i private_key.pem' --delete --rsync-path='sudo rsync' "
        f"--exclude='*.pem' --ignore-missing-args ./ "
        f"'ubuntu@{private_ip_address}:/home/ubuntu/{application}/'",
        shell=True)

    subprocess.check_call(
        f"ssh -i private_key.pem -o StrictHostKeyChecking=no ubuntu@{private_ip_address} "
        f"'cd /home/ubuntu/{application} && sudo bash docker.sh'",
        shell=True)

if __name__ == "__main__":
    environment = os.environ['ENVIRONMENT']
    application = os.environ['APPLICATION']

    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')

    bucket_ssh_keys_name = os.environ['BUCKET_SSH_KEYS_NAME']

    instances = get_instances(environment=environment, application=application)
    for instance in instances:

        bucket_private_key_path = f"{application}-{environment}.pem"
        private_key_pem = get_private_key_from_s3(bucket_ssh_keys_name=bucket_ssh_keys_name,
                                                bucket_private_key_path=bucket_private_key_path)
        try:
            create_private_key_pem_file(private_key_pem=private_key_pem)
            deploy(private_ip_address=instance['PrivateIpAddress'], application=application)

        except Exception as e:
            logger.error(e)
            raise e
        finally:
            os.remove('private_key.pem')