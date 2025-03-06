from boto3 import client


def log_func(env, functions):
    print(f"\n\n{env} Functions:\n")
    for function in functions:
        print(
            function["FunctionName"],
            function["Environment"]["Variables"]["VERSION"],
            function["Runtime"],
            function["LastModified"],
            sep=" / ",
        )


def generate_tf_file(env, lambdas):
    if env == "DEV":
        file_name = (
            "live/aws/01-dev/020427942281/eu-west-1/versions/data_template_file.tf"
        )
    elif env == "UAT":
        file_name = (
            "live/aws/02-uat/020427942281/eu-west-1/versions/data_template_file.tf"
        )
    elif env == "UATM":
        file_name = "live/aws/03-uatm/versions/data_template_file.tf"
    elif env == "PROD":
        file_name = (
            "live/aws/04-prod/020427942281/eu-west-1/versions/data_template_file.tf"
        )
    template_file_block = (
        "template = jsonencode({\n"
        + ",\n".join(
            [
                f"{project['name']} = {{ version = \"{project['version']}\", date = \"{project['date']}\" }}"
                for project in lambdas
            ]
        )
        + "\n})"
    )

    terraform_config = f"""
data "template_file" "lambda_versions_template" {{
    {template_file_block}
}}
"""
    with open(file_name, "w") as f:
        f.write(terraform_config)


def extract_variables(lambdas, functions):
    EXCLUDED_FUNCTIONS = [
        "facturation_dev",
        "facturation_uat",
        "facturation_uatm",
        "facturation_prod",
        "extract_salary_DEV",
        "extract_salary_UAT",
        "extract_salary_UATM",
        "extract_salary_PROD",
        "lambda_pdf2text_dev",
        "lambda_pdf2text_uat",
        "lambda_pdf2text_uatm",
        "lambda_pdf2text_prod",
        "extract_salary_pdf_DEV",
        "extract_salary_pdf_UAT",
        "extract_salary_pdf_UATM",
        "extract_salary_pdf_PROD",
        "archive_UAT",
        "archive_prod",
        "lambda_monitoring_dev",
    ]
    for function in functions:
        func_name = function["FunctionName"].replace("-", "_")
        if func_name not in EXCLUDED_FUNCTIONS:
            lambdas.append(
                {
                    "name": func_name,
                    "version": function["Environment"]["Variables"]["VERSION"],
                    "date": function["LastModified"].split("T")[0],
                }
            )


if __name__ == "__main__":
    lambda_client = client("lambda")
    response = lambda_client.list_functions()
    dev_functions, dev_lambdas = [], []
    uat_functions, uat_lambdas = [], []
    uatm_functions, uatm_lambdas = [], []
    prod_functions, prod_lambdas = [], []
    while True:
        functions = response["Functions"]
        for function in functions:
            if function.get("Environment"):
                if function["Environment"]["Variables"].get("VERSION"):
                    func_name = function["FunctionName"].lower()
                    if "dev" in func_name:
                        dev_functions.append(function)
                    elif "uat" in func_name and not "uatm" in func_name:
                        uat_functions.append(function)
                    elif "uatm" in func_name:
                        uatm_functions.append(function)
                    elif "prod" in func_name:
                        prod_functions.append(function)

        # Check if there are more results
        if "NextMarker" in response:
            pagination_token = response["NextMarker"]
            response = lambda_client.list_functions(Marker=pagination_token)
        else:
            break

    for env, functions in [
        ("DEV", dev_functions),
        ("UAT", uat_functions),
        ("UATM", uatm_functions),
        ("PROD", prod_functions),
    ]:
        log_func(env, functions)
        if env == "DEV":
            extract_variables(dev_lambdas, functions)
            generate_tf_file(env, dev_lambdas)
        elif env == "UAT":
            extract_variables(uat_lambdas, functions)
            generate_tf_file(env, uat_lambdas)
        elif env == "UATM":
            extract_variables(uatm_lambdas, functions)
            generate_tf_file(env, uatm_lambdas)
        elif env == "PROD":
            extract_variables(prod_lambdas, functions)
            generate_tf_file(env, prod_lambdas)
