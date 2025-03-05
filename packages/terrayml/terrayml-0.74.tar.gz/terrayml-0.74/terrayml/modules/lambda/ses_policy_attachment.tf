resource "aws_iam_policy" "ses_policy" {
  name        = "${var.common.project_code}-ses-policy-${var.common.environment}"
  description = "ses Execution Policy"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "ses:SendTemplatedEmail"
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

resource "aws_iam_role_policy_attachment" "ses-policy-attachment" {
  for_each = { for key, value in var.lambdas_with_ses_list : value.function_name => value }

  role       = aws_iam_role.lambda-exec-role[each.value.function_name].name
  policy_arn = aws_iam_policy.ses_policy.arn
}