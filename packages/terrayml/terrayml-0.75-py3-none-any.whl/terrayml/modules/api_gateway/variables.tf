variable "common" {
  description = "common variables"
}

variable "apigw_lambda_list" {
  type = list(object({
    function_name = string
    route_key = string
    integration_method = string
    integration_uri = string
  }))
  description = "API GW Lambda List"
}