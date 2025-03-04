import json
import os
import subprocess

import click

from generator import Generator
from loader import load_env_file, load_yaml
from utilities import replace_placeholders, to_terraform_hcl

DEFAULT_YAML_FILE = "terrayml.yml"


def generate_terraform(yaml_file):
    """Generate Terraform file based on updated YAML configuration."""
    yaml_file = yaml_file or DEFAULT_YAML_FILE  # Use default YAML if none specified

    try:
        Generator.copy_file(file_path=".env.example")

        if not os.path.exists(yaml_file):
            raise FileNotFoundError(
                f"❌ Error: Target Terrayml Config file '{yaml_file}' not found."
            )
        if not os.path.exists("requirements.txt"):
            raise FileNotFoundError(f"❌ Error: requirements.txt file not found.")

        print(f"📄 Using YAML file: {yaml_file}")
        config = load_yaml(yaml_file)
        environment = config["environment"]
        load_env_file(environment)

        updated_config = replace_placeholders(config, os.environ, required=True)
        Generator.VARIABLE_MAPPING = {
            "AWS_REGION": updated_config["provider"]["region"],
            "PROJECT_NAME": updated_config["project_name"],
            "PROJECT_CODE": updated_config["project_code"],
            "SERVICE_NAME": updated_config["service_name"],
            "AWS_ACCOUNT_ID": os.environ["AWS_ACCOUNT_ID"],
            "AWS_PROFILE": os.environ["AWS_PROFILE"],
            "TERRAYML_PATH": os.getcwd(),
            "ENVIRONMENT": environment,
        }

        Generator.create_file(output_file="main.tf")
        Generator.create_file(output_file="terraform.tfvars")
        Generator.create_file(output_file="variables.tf")

        if updated_config.get("lambda_functions", None):
            lambda_list = []
            apigw_list = []
            ddb_access_list = []

            for function, value in updated_config["lambda_functions"].items():
                lambda_mapping = {}
                lambda_mapping["LAMBDA_SERVICE_NAME"] = Generator.VARIABLE_MAPPING[
                    "SERVICE_NAME"
                ]
                lambda_mapping["LAMBDA_FUNCTION_NAME"] = function
                lambda_mapping["LAMBDA_FUNCTION_DESCRIPTION"] = value.get(
                    "description", ""
                )
                lambda_mapping["LAMBDA_HANDLER"] = value["handler"]
                lambda_mapping["LAMBDA_RUNTIME"] = value.get("runtime", "python3.11")
                lambda_mapping["LAMBDA_MEMORY_SIZE"] = value.get("memory_size", 128)

                lambda_mapping["LAMBDA_TIMEOUT"] = value.get("timeout", 30)
                lambda_mapping["LAMBDA_VPC_SUBNET_IDS"] = value.get("subnet_ids", [])

                lambda_mapping["LAMBDA_VPC_SECURITY_GROUP_IDS"] = value.get(
                    "security_group_ids", []
                )
                lambda_mapping["LAMBDA_VARIABLES"] = value.get("variables", {})

                lambda_list.append(
                    Generator.create_object("lambda_function", lambda_mapping)
                )

                if value.get("path", None):
                    lambda_mapping["LAMBDA_PATH"] = value["path"]
                    lambda_mapping["LAMBDA_METHOD"] = value["method"]

                    apigw_list.append(
                        Generator.create_object("lambda_apigw", lambda_mapping)
                    )
                if value.get("dynamodb_access", False):
                    ddb_access_list.append(
                        Generator.create_object("lambda_access", lambda_mapping)
                    )

            Generator.VARIABLE_MAPPING["LAMBDA_FUNCTIONS_LIST"] = to_terraform_hcl(
                lambda_list
            )
            Generator.VARIABLE_MAPPING["LAMBDA_FUNCTION_WITH_DDB_LIST"] = (
                to_terraform_hcl(ddb_access_list)
            )

            if apigw_list:
                Generator.VARIABLE_MAPPING["ENABLE_APIGW"] = "TRUE"
                Generator.VARIABLE_MAPPING["LAMBDA_FUNCTIONS_WITH_APIGW_LIST"] = (
                    to_terraform_hcl(apigw_list)
                )
                Generator.create_file(output_file="apigw_module.tf")
                Generator.create_module("api_gateway")
            else:
                Generator.VARIABLE_MAPPING["ENABLE_APIGW"] = "FALSE"
                Generator.delete_file("apigw_module.tf")
                Generator.delete_module("api_gateway")

            Generator.create_file(output_file="lambda_module.tf")
            Generator.create_module("lambda")

        else:
            Generator.delete_file("lambda_module.tf")
            Generator.delete_module("lambda")
            Generator.delete_file("apigw_module.tf")
            Generator.delete_module("api_gateway")

    except FileNotFoundError as e:
        print(str(e))
        print("❌ Terraform generation failed due to missing file.")
    except ValueError as e:
        print(str(e))
        print(
            "❌ Terraform generation failed due to missing variables. Fix the missing variables and try again."
        )
    except Exception as e:
        print(str(e))
        print("❌ Terraform generation failed due to unknown error.")


@click.group()
def cli():
    """Terrayml - Terraform Generator from YAML"""
    pass


@click.command()
@click.argument("yaml_file", required=False)
def generate(yaml_file):
    """Generate Terraform files from a YAML file with environment variables."""
    generate_terraform(yaml_file)


@click.command()
def init():
    """Change directory to .terrayml and run terraform init."""
    terrayml_path = os.path.join(os.getcwd(), ".terrayml")

    if not os.path.isdir(terrayml_path):
        click.echo("Error: .terrayml directory does not exist!")
        return

    click.echo(f"Changing directory to {terrayml_path} and running terraform init...")

    try:
        subprocess.run(["terraform", "init"], cwd=terrayml_path, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Terraform init failed: {e}")


@click.command()
def plan():
    """Change directory to .terrayml and run terraform plan."""
    terrayml_path = os.path.join(os.getcwd(), ".terrayml")

    if not os.path.isdir(terrayml_path):
        click.echo("Error: .terrayml directory does not exist!")
        return

    click.echo(f"Changing directory to {terrayml_path} and running terraform plan...")

    try:
        subprocess.run(["terraform", "plan"], cwd=terrayml_path, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Terraform plan failed: {e}")


@click.command()
def apply():
    """Change directory to .terrayml and run terraform apply."""
    terrayml_path = os.path.join(os.getcwd(), ".terrayml")

    if not os.path.isdir(terrayml_path):
        click.echo("Error: .terrayml directory does not exist!")
        return

    click.echo(f"Changing directory to {terrayml_path} and running terraform apply...")

    try:
        subprocess.run(
            ["terraform", "apply", "-auto-approve"], cwd=terrayml_path, check=True
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Terraform apply failed: {e}")


@click.command()
def destroy():
    """Change directory to .terrayml and run terraform destroy."""
    terrayml_path = os.path.join(os.getcwd(), ".terrayml")

    if not os.path.isdir(terrayml_path):
        click.echo("Error: .terrayml directory does not exist!")
        return

    click.echo(
        f"Changing directory to {terrayml_path} and running terraform destroy..."
    )

    try:
        subprocess.run(
            ["terraform", "destroy", "-auto-approve"], cwd=terrayml_path, check=True
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Terraform destroy failed: {e}")


cli.add_command(generate)
cli.add_command(init)
cli.add_command(plan)
cli.add_command(apply)
cli.add_command(destroy)

if __name__ == "__main__":
    cli()
