import yaml

class CloudFormationTemplate:
    def __init__(self, description="AWS CloudFormation Template"):
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": description,
            "Resources": {}
        }
    
    def add_resource(self, logical_id, resource_type, properties=None):
        self.template["Resources"][logical_id] = {
            "Type": resource_type,
            "Properties": properties or {}
        }
    
    def generate_yaml(self):
        return yaml.dump(self.template, default_flow_style=False)
    
    def save_to_file(self, filename="cloudformation_template.yaml"):
        with open(filename, "w") as file:
            file.write(self.generate_yaml())
        print(f"Template saved to {filename}")
    
    def add_resources_based_on_request(self, *requested_resources):
        aws_resources = {
            "S3Bucket": "AWS::S3::Bucket",
            "EC2Instance": "AWS::EC2::Instance",
            "LambdaFunction": "AWS::Lambda::Function",
            "DynamoDBTable": "AWS::DynamoDB::Table",
            "IAMRole": "AWS::IAM::Role",
            "VPC": "AWS::EC2::VPC",
            "Subnet": "AWS::EC2::Subnet",
            "SecurityGroup": "AWS::EC2::SecurityGroup",
            "RDSInstance": "AWS::RDS::DBInstance",
            "CloudFrontDistribution": "AWS::CloudFront::Distribution",
            "APIGateway": "AWS::ApiGateway::RestApi",
            "ECSCluster": "AWS::ECS::Cluster",
            "EKSCluster": "AWS::EKS::Cluster",
            "AutoScalingGroup": "AWS::AutoScaling::AutoScalingGroup",
            "RouteTable": "AWS::EC2::RouteTable",
            "InternetGateway": "AWS::EC2::InternetGateway",
            "ElasticLoadBalancer": "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "CloudWatchAlarm": "AWS::CloudWatch::Alarm",
            "SNSTopic": "AWS::SNS::Topic",
            "SQSQueue": "AWS::SQS::Queue",
            "KinesisStream": "AWS::Kinesis::Stream",
            "SecretsManagerSecret": "AWS::SecretsManager::Secret",
            "StepFunction": "AWS::StepFunctions::StateMachine"
        }
        for logical_id in requested_resources:
            if logical_id in aws_resources:
                self.add_resource(logical_id, aws_resources[logical_id])
            else:
                print(f"Warning: {logical_id} is not a recognized AWS resource.")
