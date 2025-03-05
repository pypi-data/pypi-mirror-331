resource "aws_iam_policy" "dynamodb_policy" {
  name        = "${var.common.project_code}-dynamodb-policy-${var.common.environment}"
  description = "dynamodb Execution Policy"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:Query",
                    "dynamodb:DeleteItem",
                    "dynamodb:UpdateItem"
                ],
                "Resource": [
                    "*"
                ],
                "Effect": "Allow"
            },
        ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "dynamodb-policy-attachment" {
  for_each = { for key, value in var.lambdas_with_dynamodb_list : value.function_name => value }

  role       = aws_iam_role.lambda-exec-role[each.value.function_name].name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}