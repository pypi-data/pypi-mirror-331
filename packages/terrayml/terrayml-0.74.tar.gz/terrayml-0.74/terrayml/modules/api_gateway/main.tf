resource "aws_apigatewayv2_api" "apigw" {
  name          = "${var.common.project_code}-${var.common.service_name}-${var.common.environment}"
  protocol_type = "HTTP"

  tags = var.common.default_tags
}

resource "aws_apigatewayv2_deployment" "apigw_deployment" {
  for_each       = { for key, value in var.apigw_lambda_list : value.function_name => value }

  depends_on    = [ aws_apigatewayv2_route.apigw_route ]
  api_id        = aws_apigatewayv2_api.apigw.id
  description   = "${var.common.project_name} API Gateway deployment."

  triggers      =    {
    redeployment = sha1(jsonencode([
      aws_apigatewayv2_stage.apigw_stage,
      aws_apigatewayv2_route.apigw_route[each.value.function_name],
      aws_apigatewayv2_integration.lambda_apigw_integration[each.value.function_name],
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_stage" "apigw_stage" {
  api_id = aws_apigatewayv2_api.apigw.id
  name   = var.common.environment
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_apigw_integration" {
  for_each       = { for key, value in var.apigw_lambda_list : value.function_name => value }

  api_id           = aws_apigatewayv2_api.apigw.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  description               = "Lambda integation."
  integration_method        = "GET"
  integration_uri           = each.value.integration_uri
}

resource "aws_apigatewayv2_route" "apigw_route" {
  for_each       = { for key, value in var.apigw_lambda_list : value.function_name => value }

  api_id    = aws_apigatewayv2_api.apigw.id
  route_key = each.value.route_key
  # route_key = "GET /api/transactions" # TODO highlight all the same in this file and change

  target = "integrations/${aws_apigatewayv2_integration.lambda_apigw_integration[each.value.function_name].id}"
}

output "apigw_execution_arn" {
  value = aws_apigatewayv2_api.apigw.execution_arn
}
output "apigw_endpoint" {
  value = aws_apigatewayv2_api.apigw.api_endpoint
}