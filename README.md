# AWS GuardDuty to Slack Notifications

This AWS Lambda function forwards Amazon GuardDuty findings to a Slack channel. It processes GuardDuty events and sends formatted notifications with severity levels, geographical information, and direct links to the AWS Console.

## Features

- 🚨 Real-time GuardDuty finding notifications in Slack
- 🎨 Color-coded messages based on severity level
- 📍 Geographical information for suspicious IP addresses
- 🔗 Direct links to findings in AWS Console
- ⚡ Configurable minimum severity level for notifications
- 🔐 Secure webhook implementation

## Prerequisites

- AWS Account with GuardDuty enabled
- Slack workspace with permissions to add webhooks
- AWS Lambda execution role with appropriate permissions

## Environment Variables

| Variable           | Description                                                       | Required |
| ------------------ | ----------------------------------------------------------------- | -------- |
| `webHookUrl`       | Slack webhook URL                                                 | Yes      |
| `slackChannel`     | Target Slack channel                                              | Yes      |
| `minSeverityLevel` | Minimum severity level to trigger notifications (LOW/MEDIUM/HIGH) | Yes      |

## Severity Levels

The function categorizes findings into three severity levels:

- 🟡 **Low** (< 4.0): Yellow indicators
- 🟠 **Medium** (4.0 - 6.9): Orange indicators
- 🔴 **High** (≥ 7.0): Red indicators

## Message Format

Slack notifications include:

- Finding type and AWS region
- Account ID
- Severity level
- Detailed description
- Geographical information (if available)
- Timestamp of last occurrence
- Direct link to the finding in AWS Console

## Setup Instructions

1. **Create a Slack Webhook:**

   - Go to your Slack workspace settings
   - Navigate to Custom Integrations > Incoming Webhooks
   - Create a new webhook and copy the URL

2. **Deploy the Lambda Function:**

   - Create a new Lambda function
   - Copy the provided code
   - Set the required environment variables
   - Configure the execution role

3. **Configure EventBridge:**
   - Go to Amazon EventBridge console
   - Create a new rule with the provided event pattern
   - Select the Lambda function as the target
   - Ensure proper IAM permissions are in place

## Event Pattern

Configure your EventBridge rule with the following event pattern:

```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"]
}
```

## IAM Permissions

The Lambda function requires the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ecs:DescribeTaskDefinition",
        "logs:GetLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": ["*"]
    }
  ]
}
```

This policy provides permissions for:

- Network interface management (required for Lambda VPC access)
- ECS task definition access
- CloudWatch Logs access for monitoring and debugging

## Error Handling

The function includes comprehensive error handling for:

- Missing event keys
- Invalid severity levels
- Failed Slack notifications
- Malformed events

All errors are logged to CloudWatch Logs for debugging.

## Customization

You can customize the function by:

- Modifying severity thresholds in `get_severity_details()`
- Adjusting the message format in `generate_slack_message()`
- Adding additional event data to notifications
- Customizing colors and icons

## Monitoring

Monitor the function using:

- CloudWatch Logs for execution logs
- CloudWatch Metrics for invocation statistics
- Lambda function metrics for performance data

## Troubleshooting

Common issues and solutions:

### 1. No notifications received

- Verify webhook URL is correct
- Check minimum severity level setting
- Ensure EventBridge rule is properly configured

### 2. Missing information in notifications

- Verify GuardDuty finding contains expected fields
- Check CloudWatch Logs for parsing errors

### 3. Function timeouts

- Increase Lambda timeout value
- Check Slack endpoint connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS GuardDuty Documentation
- Slack API Documentation
- AWS Lambda Documentation
