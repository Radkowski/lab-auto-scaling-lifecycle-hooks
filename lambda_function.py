import json
import boto3
import os

secondary_ip = os.environ['SEC_IP_ADDR']


def get_interface_id(instance_id):
    client_ec2 = boto3.client('ec2')
    response = client_ec2.describe_instances(InstanceIds=[instance_id])
    return (response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId'])


def add_secondary_ip(interface_id,sec_ip_addr):
    client_ec2 = boto3.client('ec2')
    response = client_ec2.assign_private_ip_addresses(
        AllowReassignment=True,
        NetworkInterfaceId=interface_id,
        PrivateIpAddresses=[sec_ip_addr]
    )


def complete_hook(hook_name, asg_name, asg_token):
    client_asg = boto3.client('autoscaling')
    response = client_asg.complete_lifecycle_action(
        LifecycleHookName=hook_name,
        AutoScalingGroupName=asg_name,
        LifecycleActionToken=asg_token,
        LifecycleActionResult='CONTINUE'
    )


def lambda_handler(event, context):
    add_secondary_ip(get_interface_id(event['detail']['EC2InstanceId']),secondary_ip)
    complete_hook(event['detail']['LifecycleHookName'],event['detail']['AutoScalingGroupName'],event['detail']['LifecycleActionToken'])
    return 0
