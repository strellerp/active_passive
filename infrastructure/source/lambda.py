import boto3
import logging
import requests

TARGET_GROUP_ARN: str = "arn:aws:elasticloadbalancing:us-east-1:648106300517:targetgroup/test-prd-tg/b59bc5b874d33a9b"
PRIMARY_INSTANCE_ID: str = "i-064a146681f1096ee"
PRIMARY_INSTANCE_IP: str = "3.88.144.217"
HEALTH_CHECK_PATH: str = ""
HTTP_SUCCESS_CODES: list[int] = [ 200 ]
SECONDARY_INSTANCE_ID: str = "i-0765d9593b43effb4"

def lambda_handler(event, context) -> None:
    logging.warning(f"Primary instance ID: {PRIMARY_INSTANCE_ID}")
    logging.warning(f"Secondary instance ID: {SECONDARY_INSTANCE_ID}")

    client = boto3.client('elbv2')

     def check_instance_health(instance_id: str, port: int = 80) -> str:
        response: dict = client.describe_target_health(
            TargetGroupArn = TARGET_GROUP_ARN,
            Targets = [{
                'Id': instance_id,
                'Port': port,
            }]
        )
        instance_health: str = response["TargetHealthDescriptions"][0]["TargetHealth"]["State"]
        return instance_health

    def register(instance_id: str, port: int = 80) -> None:
        logging.warning(f"Registering {instance_id}")
        client.register_targets(
            TargetGroupArn = TARGET_GROUP_ARN,
            Targets=[{
                'Id': instance_id,
                'Port': port,
            }]
        )

    def deregister(instance_id: str, port: int = 80) -> None:
        logging.warning(f"Deregistering {instance_id}...")
        client.deregister_targets(
            TargetGroupArn = TARGET_GROUP_ARN,
            Targets = [{
                'Id': instance_id,
                'Port': port,
            }]
        )

    primary_instance_health: str = check_instance_health(PRIMARY_INSTANCE_ID)
    secondary_instance_health: str = check_instance_health(SECONDARY_INSTANCE_ID)
    logging.warning(f"Current instance state [primary|secondary]: [{primary_instance_health}|{secondary_instance_health}]")

    if primary_instance_health == "healthy":
        if secondary_instance_health in ["healthy", "unhealthy"]: # healthy || unhealthy => registered
            deregister(SECONDARY_INSTANCE_ID)
        else:
            logging.warning("Nothing to do.")
    else:
        if secondary_instance_health == "unused":
            register(SECONDARY_INSTANCE_ID)
        elif passive_instance_health == "healthy" and active_instance_health == "unhealthy":
            deregister(ACTIVE_INSTANCE_ID)
        else:
            logging.warning("Checking primary instance health...")
            try:
                status_code: str = requests.get(f"http://{PRIMARY_INSTANCE_IP}/{HEALTH_CHECK_PATH}").status_code
                if status_code in [ HTTP_SUCCESS_CODES ]:
                    logging.warning("Primary instance is healthy again.")
                    register(PRIMARY_INSTANCE_ID)
                else:
                    logging.warning(f"Primary instance returned status code {status_code} and is not yet healthy again. Nothing to do.")
            except:
                logging.warning(f"Primary instance could not be reached. Nothing to do.")
