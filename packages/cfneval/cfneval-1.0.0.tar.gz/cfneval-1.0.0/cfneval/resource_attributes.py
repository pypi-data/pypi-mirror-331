from collections.abc import Callable


def get_attrs_for_param_store(
    *, resource_name: str, resource: dict, account_id: str, region: str
) -> dict:
    return {
        "Type": resource["Properties"]["Type"],
        "Value": resource["Properties"]["Value"],
    }


def get_attrs_for_ecs_service(
    *, resource_name: str, resource: dict, account_id: str, region: str
) -> dict:
    return {
        "Name": resource["Properties"]["ServiceName"],
        # This isn't the exact format for the ARN, but it's close enough for testing
        "Arn": f"arn:aws:ecs:{region}:{account_id}:service/{resource_name}",
    }


def get_attrs_for_ecs_cluster(
    *, resource_name: str, resource: dict, account_id: str, region: str
) -> dict:
    return {
        # This isn't the exact format for the ARN, but it's close enough for testing
        "Arn": f"arn:aws:ecs:{region}:{account_id}:cluster/{resource_name}",
    }


class ResourceAttributeRegistry:

    def __init__(self):
        self.registry = {}
        self.register_resource_attributes(
            "AWS::SSM::Parameter", get_attrs_for_param_store
        )
        self.register_resource_attributes(
            "AWS::ECS::Service", get_attrs_for_ecs_service
        )
        self.register_resource_attributes(
            "AWS::ECS::Cluster", get_attrs_for_ecs_cluster
        )

    def register_resource_attributes(self, resource_type: str, func: Callable) -> None:
        self.registry[resource_type] = func

    def evaluate_attributes(
        self, *, resource_name: str, resource: dict, account_id: str, region: str
    ) -> str:
        resource_type = resource["Type"]
        if resource_type in self.registry:
            return self.registry[resource_type](
                resource_name=resource_name,
                resource=resource,
                account_id=account_id,
                region=region,
            )
        return None
