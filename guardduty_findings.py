import os
import json
from http.client import HTTPSConnection
from urllib.parse import urlparse
from datetime import datetime

# Environment variables
webhook_url = os.environ.get("webHookUrl")
slack_channel = os.environ.get("slackChannel")
min_severity_level = os.environ.get("minSeverityLevel")


def post_message(message):
    parsed_url = urlparse(webhook_url)
    body = json.dumps(message).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),  # Convert length to string
    }

    connection = HTTPSConnection(parsed_url.netloc)
    connection.request("POST", parsed_url.path, body=body, headers=headers)

    response = connection.getresponse()

    return {
        "body": response.read().decode(),
        "statusCode": response.status,
        "statusMessage": response.reason,
    }


def get_severity_details(severity):
    if severity is None:
        return None

    if severity < 4.0:
        return {"level": "Low", "color": "#e2d43b"}
    elif severity < 7.0:
        if min_severity_level not in ["LOW", "MEDIUM"]:
            return None
        return {"level": "Medium", "color": "#ff8c00"}
    elif severity >= 7.0:
        return {"level": "High", "color": "#ad0614"}
    return None


def generate_slack_message(event):
    console_url = "https://console.aws.amazon.com/guardduty"

    severity = event.get("detail", {}).get("severity")  # Updated to access 'detail' key
    severity_details = get_severity_details(severity)
    if not severity_details:
        return None

    ip_details_text = ""
    action = (
        event.get("detail", {})
        .get("service", {})
        .get("action", {})
        .get("awsApiCallAction", {})
    )  # Updated to access 'detail' key
    if action.get("remoteIpDetails"):
        ip_details = action["remoteIpDetails"]
        ip_details_text = f"City: {ip_details.get('city', {}).get('cityName', 'N/A')}, Country: {ip_details.get('country', {}).get('countryName', 'N/A')}, Location: {ip_details.get('geoLocation', {}).get('lat', 'N/A')}, {ip_details.get('geoLocation', {}).get('lon', 'N/A')}"

    slack_message = {
        "channel": slack_channel,
        "text": "",
        "attachments": [
            {
                "fallback": f"{event['detail']['type']} - {console_url}/home?region={event['region']}#/findings?search=id%3D{event['detail']['id']}",
                "pretext": f"*Finding in {event['region']} for Acct: {event['account']}*",
                "title": event["detail"]["type"],
                "title_link": f"{console_url}/home?region={event['region']}#/findings?search=id%3D{event['detail']['id']}",
                "text": f"{event['detail'].get('description', 'No description available')}\n\n{ip_details_text}",
                "fields": [
                    {
                        "title": "Severity",
                        "value": severity_details["level"],
                        "short": True,
                    },
                    {"title": "Region", "value": event["region"], "short": True},
                    {
                        "title": "Last Seen",
                        "value": f"<!date^{int(datetime.strptime(event['detail']['updatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}^{{date}} at {{time}} | {event['detail']['updatedAt']}>",
                        "short": True,
                    },
                ],
                "mrkdwn_in": ["pretext", "text"],
                "color": severity_details["color"],
            }
        ],
        "username": "GuardDuty",
        "mrkdwn": True,
        "icon_url": "https://raw.githubusercontent.com/aws-samples/amazon-guardduty-to-slack/master/images/gd_logo.png",
    }

    return slack_message


def process_event(event):
    slack_message = generate_slack_message(event)
    if slack_message:
        return post_message(slack_message)
    else:
        return None


def lambda_handler(event, context):
    try:
        # Print the incoming event for debugging
        print("Received event:", json.dumps(event, indent=2))

        response = process_event(event)
        if response:
            print("Message posted successfully:", response)
        else:
            print("No message to post.")
    except KeyError as e:
        print(f"KeyError - The key {e} is missing in the event:", event)
    except Exception as e:
        print("Error processing event:", str(e))

    # Always return a response
    return {"statusCode": 200, "body": json.dumps("Function executed successfully")}
