resource "aws_iam_policy" "secrets_manager_policy" {
  count       = length(var.secrets_arn_list) > 0 ? 1 : 0
  name        = "${var.common.project_code}-secrets-manager-policy-${var.common.environment}"
  description = "Secrets Manager Get Secret Value Policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "secretsmanager:GetSecretValue"
        ],
        "Resource": [
          for key, value in var.secrets_arn_list : value.name
        ],
        "Effect": "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets-manager-policy-attachment" {
  for_each = { for key, value in var.lambdas_with_secrets_manager_list : value.function_name => value }

  role       = aws_iam_role.lambda-exec-role[each.value.function_name].name
  policy_arn = aws_iam_policy.secrets_manager_policy[0].arn
}