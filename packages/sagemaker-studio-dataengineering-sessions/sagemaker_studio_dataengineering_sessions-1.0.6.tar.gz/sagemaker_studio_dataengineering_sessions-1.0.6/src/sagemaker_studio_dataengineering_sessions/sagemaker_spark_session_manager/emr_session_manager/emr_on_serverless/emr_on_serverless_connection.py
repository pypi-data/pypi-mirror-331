from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.spark_session_manager.spark_connection import \
    SparkConnection


class EmrOnServerlessConnection(SparkConnection):
    def __init__(self,
                 connection_name: str,
                 connection_id: str,
                 url: str,
                 runtime_role: str,
                 application_id: str,
                 region: str,
                 spark_configs: dict[str, any] | None = None):
        super().__init__(spark_configs)
        self.connection_name = connection_name
        self.connection_id = connection_id
        self.url = url
        self.runtime_role = runtime_role
        self.application_id = application_id
        self.region = region
