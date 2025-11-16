from aws_cdk import aws_cloudwatch as cloudwatch, aws_cloudwatch_actions as cw_actions, aws_sns as sns, Stack
from constructs import Construct

class ObservabilityStack(Stack):
    def __init__(self, scope: Construct, id: str, lambda_function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create CloudWatch Metrics Dashboard
        dashboard = cloudwatch.Dashboard(self, "ModelRegistryDashboard")

        # API Latency Metrics
        latency_widget = cloudwatch.GraphWidget(
            title="API Latency (ms)",
            left=[lambda_function.metric_duration(statistic="p99")]
        )

        # API Error Metrics
        error_widget = cloudwatch.GraphWidget(
            title="API Errors",
            left=[lambda_function.metric_errors()]
        )

        # Add to dashboard
        dashboard.add_widgets(latency_widget, error_widget)

        # SNS Notification for Errors
        sns_topic = sns.Topic(self, "APIErrorsTopic")
        sns_topic.add_subscription(sns.Subscription(self, "ErrorAlert", protocol=sns.SubscriptionProtocol.EMAIL,
                                                     endpoint="your-email@example.com"))

        # Set error alert
        error_alarm = cloudwatch.Alarm(self, "ErrorAlarm",
                                        metric=lambda_function.metric_errors(),
                                        threshold=1,
                                        evaluation_periods=1)
        error_alarm.add_alarm_action(cw_actions.SnsAction(sns_topic))