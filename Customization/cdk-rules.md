Where possible avoid using wildcard permissions (`*`) in IAM policies.
All Amazon S3 buckets must have encryption enabled, versioning, enforce SSL, and block public access.
All Amazon DynamoDB Streams tables must have encryption enabled. 
All Amazon SNS topics must have encryption enabled and enforce SSL. 
All Amazon SNS queues must enforce SSL.
Configure AWS WAF for internet-facing applications.
Configure logging for WAF events.