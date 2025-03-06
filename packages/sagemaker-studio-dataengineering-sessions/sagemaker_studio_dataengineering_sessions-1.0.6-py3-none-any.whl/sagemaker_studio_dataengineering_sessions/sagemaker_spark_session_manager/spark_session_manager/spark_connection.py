class SparkConnection(object):
    def __init__(self, spark_configs: dict[str, any] | None = None):
        self.spark_configs = spark_configs
