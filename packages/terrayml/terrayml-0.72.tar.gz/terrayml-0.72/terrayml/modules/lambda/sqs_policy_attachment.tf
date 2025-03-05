resource "aws_iam_policy" "sqs_policy" {
  name        = "${var.common.project_code}-sqs-policy-${var.common.environment}"
  description = "SQS Lambda Policy"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                  "sqs:SendMessage",
                  "sqs:ReceiveMessage",
                  "sqs:DeleteMessage",
                  "sqs:GetQueueAttributes",
                  "sqs:purgequeue",
                ],
                "Resource": [
                  "*"
                ],
                "Effect": "Allow"
            }
        ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "sqs-policy-attachment" {
  for_each = { for key, value in var.lambdas_with_sqs_list : value.function_name => value }

  role       = aws_iam_role.lambda-exec-role[each.value.function_name].name
  policy_arn = aws_iam_policy.sqs_policy.arn
}
