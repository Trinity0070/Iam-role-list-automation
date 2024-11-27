import logging
import boto3
from collections import defaultdict
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Initialize a defaultdict to track IAM roles and the instances they are attached to
    role_to_instances = defaultdict(list)

    # Describe EC2 instances (running and stopped)
    try:
        instances = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        )
    except ClientError as e:
        logger.error(f"Error fetching EC2 instances: {str(e)}")
        return {'error': f"Error fetching EC2 instances: {str(e)}"}
    
    # Process each instance to gather IAM roles
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_iam_role = None
            
            # Get IAM role attached to the instance (if any)
            if 'IamInstanceProfile' in instance:
                arn = instance['IamInstanceProfile']['Arn']
                instance_iam_role = arn.split('/')[-1]  # Extract the role name from the ARN
            
            # Track IAM roles to multiple instances
            if instance_iam_role:
                role_to_instances[instance_iam_role].append(instance_id)

    # Return only IAM roles and the instances attached to them
    return {
        'IamRoles': role_to_instances
    }
