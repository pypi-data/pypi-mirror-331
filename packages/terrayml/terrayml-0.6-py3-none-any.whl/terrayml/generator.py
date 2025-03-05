import importlib
import json
import os
import shutil

import pkg_resources

from .utilities import replace_placeholders, to_terraform_hcl


class Generator:
    VARIABLE_MAPPING = {}

    def __init__(self, config):
        self.config = config

    @classmethod
    def assign_variables(cls, file, variables, required=True):
        return replace_placeholders(file, variables, required=required)

    @classmethod
    def create_file(cls, output_file, name_override=None):

        template_file = f"file_templates/{output_file}.txt"
        template_file = pkg_resources.resource_filename("terrayml", template_file)
        if not os.path.exists(template_file):
            print(f"❌ Error: Terraform template '{template_file}' not found.")
            return

        with open(template_file, "r") as file:
            template = file.read()

        terraform_code = replace_placeholders(
            template, cls.VARIABLE_MAPPING, required=True
        )

        generated_tf_folder_path = ".terrayml"
        os.makedirs(generated_tf_folder_path, exist_ok=True)
        generated_tf_path = os.path.join(generated_tf_folder_path, output_file)
        if name_override:
            generated_tf_path = os.path.join(generated_tf_folder_path, name_override)

        with open(generated_tf_path, "w") as file:
            file.write(terraform_code)

        print(f"✅ Terraform file '{output_file}' generated successfully.")

    @classmethod
    def delete_file(cls, file):
        file_path = f".terrayml/{file}"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Terraform file '{file}' removed successfully.")

    @classmethod
    def create_module(cls, module):
        source_module = f"modules/{module}"
        source_module = pkg_resources.resource_filename("terrayml", source_module)
        os.makedirs(".terrayml/modules", exist_ok=True)
        destination_module = f".terrayml/modules/{module}"
        shutil.copytree(source_module, destination_module, dirs_exist_ok=True)
        print(f"✅ Terraform module '{module}' generated successfully.")

    @classmethod
    def delete_module(cls, module):
        os.makedirs("modules", exist_ok=True)
        destination_module = f".terrayml/modules/{module}"

        if os.path.exists(destination_module):
            shutil.rmtree(destination_module)
            print(f"✅ Terraform module '{module}' removed successfully.")

    @classmethod
    def create_object(cls, object_name, mapping={}):
        template_file = f"object_templates/{object_name}.json"
        template_file = pkg_resources.resource_filename("terrayml", template_file)
        with open(template_file, "r") as file:
            template = json.load(file)

        return replace_placeholders(template, mapping, required=True)

    @classmethod
    def copy_file(cls, file_path):
        source_path = pkg_resources.resource_filename("terrayml", file_path)
        shutil.copy(source_path, file_path)

    def generate(self):
        for attr_name in dir(self):
            if attr_name.startswith("_generate"):
                method = getattr(self, attr_name)
                if callable(method) and not isinstance(method, classmethod):
                    method()

    def _generate_lambda_module(self):
        config_name = "lambda_functions"
        object_name = config_name[:-1]
        file_template = "lambda_module"
        module = "lambda"

        if self.config.get(config_name, None):
            object_list = []
            apigw_list = []
            ddb_access_list = []

            mapping_module = importlib.import_module(f"mappings.{object_name}")

            for key, value in self.config[config_name].items():
                variable_mapping = {}
                variable_mapping = mapping_module.generate_mappings(
                    key, value, Generator.VARIABLE_MAPPING
                )

                object_list.append(
                    Generator.create_object(object_name, variable_mapping)
                )

                if value.get("path", None):
                    variable_mapping["LAMBDA_PATH"] = value["path"]
                    variable_mapping["LAMBDA_METHOD"] = value["method"]

                    apigw_list.append(
                        Generator.create_object("lambda_apigw", variable_mapping)
                    )
                if value.get("dynamodb_access", False):
                    ddb_access_list.append(
                        Generator.create_object("lambda_access", variable_mapping)
                    )

            Generator.VARIABLE_MAPPING["LAMBDA_FUNCTIONS_LIST"] = to_terraform_hcl(
                object_list
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

            Generator.create_file(output_file=f"{file_template}.tf")
            Generator.create_module(module)

        else:
            Generator.delete_file(f"{file_template}.tf")
            Generator.delete_module(module)
            Generator.delete_file("apigw_module.tf")
            Generator.delete_module("api_gateway")

    def _generate_dynamodb_module(self):
        config_name = "dynamodb_tables"
        file_template = "dynamodb_module"
        module = "dynamodb"
        object_list_variable = "DYNAMODB_LIST"

        self._simple_module_generation(
            config_name=config_name,
            file_template=file_template,
            module=module,
            object_list_variable=object_list_variable,
        )

    def _generate_s3_module(self):
        config_name = "s3_buckets"
        file_template = "s3_module"
        module = "s3"
        object_list_variable = "S3_BUCKET_LIST"

        self._simple_module_generation(
            config_name=config_name,
            file_template=file_template,
            module=module,
            object_list_variable=object_list_variable,
        )

    def _generate_cognito_module(self):
        config_name = "cognito_user_pools"
        file_template = "cognito_module"
        module = "cognito"
        object_list_variable = "COGNITO_USER_POOL_LIST"

        self._simple_module_generation(
            config_name=config_name,
            file_template=file_template,
            module=module,
            object_list_variable=object_list_variable,
            skip=True,
        )

        config_name = "cognito_identity_pools"
        file_template = "cognito_module"
        module = "cognito"
        object_list_variable = "COGNITO_IDENTITY_POOL_LIST"

        self._simple_module_generation(
            config_name=config_name,
            file_template=file_template,
            module=module,
            object_list_variable=object_list_variable,
        )

    def _simple_module_generation(
        self,
        config_name,
        file_template,
        module,
        object_list_variable,
        skip=False,
    ):
        object_name = config_name[:-1]
        if self.config.get(config_name, None):
            object_list = []

            mapping_module = importlib.import_module(f"mappings.{object_name}")

            for key, value in self.config[config_name].items():
                variable_mapping = {}
                variable_mapping = mapping_module.generate_mappings(
                    key, value, Generator.VARIABLE_MAPPING
                )
                object_list.append(
                    Generator.create_object(object_name, variable_mapping)
                )
            Generator.VARIABLE_MAPPING[object_list_variable] = to_terraform_hcl(
                object_list
            )
            if not skip:
                Generator.create_file(output_file=f"{file_template}.tf")
                Generator.create_module(module)
        else:
            if not skip:
                Generator.delete_file(f"{file_template}.tf")
                Generator.delete_module(module)
