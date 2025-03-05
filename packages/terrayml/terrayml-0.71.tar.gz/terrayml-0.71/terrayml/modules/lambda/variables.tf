variable "common" {
  description = "common variables"
}
variable "service_name" {
  description = "service name"
}

variable "runtime" {
  type = string
}

variable "apigw_execution_arn" {
  type = string
}
variable "enable_apigw" {
  type = string
}

variable "app_path" {
  type = string
}
variable "secrets_arn_list" {
  type = list(object({
    function_name = string
  }))
  description = "Secrets Manager ARNs List"
}
variable "lambdas_with_secrets_manager_list" {
  type = list(object({
    function_name = string
  }))
  description = "Lambdas needing secrets manager permissions List"
}
variable "lambdas_with_ses_list" {
  type = list(object({
    function_name = string
  }))
  description = "Lambdas needing SES permissions List"
}
variable "lambdas_with_sqs_list" {
  type = list(object({
    function_name = string
  }))
  description = "Lambdas needing SQS permissions List"
}
variable "lambdas_with_dynamodb_list" {
  type = list(object({
    function_name = string
  }))
  description = "Lambdas needing dynamodb permissions List"
}

variable "lambda_function_list" {
  type = list(object({
    service_name = string,
    function_name = string,
    description = string,
    role = string,
    handler = string,
    runtime = string,
    memory_size = number,
    timeout = number,
    vpc_config = map(list(string)),
    variables = map(string)
  }))
  description = "Lambda Function List"
}