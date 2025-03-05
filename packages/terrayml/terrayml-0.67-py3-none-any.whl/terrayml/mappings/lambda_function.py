def generate_mappings(config_key, config_value, other_reference_mappings):
    return {
        "LAMBDA_SERVICE_NAME": other_reference_mappings["SERVICE_NAME"],
        "LAMBDA_FUNCTION_NAME": config_key,
        "LAMBDA_FUNCTION_DESCRIPTION": config_value.get("description", ""),
        "LAMBDA_HANDLER": config_value["handler"],
        "LAMBDA_RUNTIME": config_value.get("runtime", "python3.11"),
        "LAMBDA_MEMORY_SIZE": config_value.get("memory_size", 128),
        "LAMBDA_TIMEOUT": config_value.get("timeout", 30),
        "LAMBDA_VPC_SUBNET_IDS": config_value.get("subnet_ids", []),
        "LAMBDA_VPC_SECURITY_GROUP_IDS": config_value.get("security_group_ids", []),
        "LAMBDA_VARIABLES": config_value.get("variables", {}),
    }