import hashlib
import hmac
import json
import boto3
from botocore.exceptions import ClientError

# Configuração da AWS
ec2 = boto3.client('ec2')

# Configurações do Webhook e Instâncias
SECRET_KEY = "INFORME A SECRET" #Criar como variável da função lambda
LAUNCH_TEMPLATE_ID = 'id-000000000000'  # Substitua pelo ID do seu Launch Template
MIN_INSTANCES = 1  # Quantidade mínima de instâncias
MAX_INSTANCES = 2  # Quantidade máxima de instâncias

# Armazenamento de informações das instâncias em execução (por 'origem')
running_instances = {}

def lambda_handler(event, context):
    # 1. Validação do Secret do Webhook
    headers = {k.lower(): v for k, v in event['headers'].items()}
    header_signature = headers.get('x-hub-signature-256')

    if not header_signature:
        return {
            'statusCode': 400,
            'body': json.dumps('X-Hub-Signature-256 header is missing.')
        }

    header_signature_hash = header_signature.split('=')[1]
    calculated_signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        event['body'].encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(header_signature_hash, calculated_signature):
        return {
            'statusCode': 403,
            'body': json.dumps('Assinatura invalida.')
        }

    # 2. Extração dos dados do Payload
    payload = json.loads(event['body'])
    action = payload['action']
    job_status = payload['workflow_job']['status']
    origin = payload.get('origin', 'default') 

    # 3. Lógica de gerenciamento de instâncias EC2
    if action == 'queued' and job_status == 'queued':
        if len(running_instances) >= MAX_INSTANCES:
            return {
                'statusCode': 200,
                'body': 'Maximum instances reached'
            }

        instance_id = launch_ec2_instance()
        running_instances[origin] = instance_id

    elif action == 'in_progress' and job_status == 'in_progress':
        instance_id = running_instances.get(origin)
        if instance_id:
            wait_for_instance_running(instance_id)

    elif action == 'completed' and job_status == 'completed':
        instance_id = running_instances.get(origin)
        if instance_id:
            terminate_ec2_instance(instance_id)
            del running_instances[origin]

    return {
        'statusCode': 200,
        'body': json.dumps('Assinatura valida!')
    }

# Funções auxiliares para gerenciar instâncias EC2

def launch_ec2_instance():
    try:
        response = ec2.run_instances(
            LaunchTemplate={'LaunchTemplateId': LAUNCH_TEMPLATE_ID},
            MinCount=1,
            MaxCount=1
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f'Launched EC2 instance: {instance_id}')
        return instance_id
    except ClientError as e:
        print(f'Error launching EC2 instance: {e}')
        return None

def wait_for_instance_running(instance_id):
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

def terminate_ec2_instance(instance_id):
    try:
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f'Terminated EC2 instance: {instance_id}')
    except ClientError as e:
        print(f'Error terminating EC2 instance: {e}')
