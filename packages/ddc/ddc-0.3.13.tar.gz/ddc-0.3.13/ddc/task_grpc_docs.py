import json
import os
from os import scandir
from os.path import join
import re
import yaml

from ddc.utils import stream_exec_cmd

# отображает поле как обязательное в документации
REQUIRED_PH = "@required"
# отображает поле как object в документации
MIXED_TYPE_PH = "@mixed_type"


def underscore_to_camelcase(s):
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), s)


def get_service_conf(api_workdir, service):
    conf_path = api_workdir + "/" + service + ".yaml"
    with open(conf_path, "r") as f:
        return yaml.load(f.read())


def __build_docs(service_id, workdir, output_dir):
    print("Build docs...")
    api_workdir = join(workdir, "api")
    proto_path = join(api_workdir, "proto")

    versions = []
    for entry in scandir(proto_path):
        versions.append(entry.name)

    for version in versions:
        version_dir = join(proto_path, version)
        __build_docs_and_swagger(service_id, version_dir, output_dir)

        prep_doc_filename = join(output_dir, "doc_json.json")
        try:
            doc_content = get_gen_doc_content(
                prep_doc_filename, service_id
            )
        finally:
            os.remove(prep_doc_filename)

        swagger_file = join(output_dir, service_id + ".swagger.json")
        try:
            with (open(swagger_file, 'r'))as f:
                sw_str = f.read()
                sw_str = sw_str.replace('"' + version, '"')
                sw_str = sw_str.replace('#/definitions/' + version, '#/definitions/')
                swagger = json.loads(sw_str)
        finally:
            os.remove(swagger_file)

        swagger["info"]["version"] = None
        swagger["info"].pop("version")

        swagger["schemes"] = None
        swagger["consumes"] = None
        swagger["produces"] = None
        swagger["tags"] = []
        for srv in doc_content["services"]:
            swagger["tags"].append(
                {"name": srv["name"], "description": srv["description"], }
            )
        for defK, defV in swagger["definitions"].items():

            required = []

            new_pros = {}
            for fK, fV in defV.get("properties", {}).items():
                title = fV.get("title")
                description = fV.get("description")
                # if description:
                #     print("title = %s" % str(title))
                #     print("description = %s" % str(description))

                title_with_desc = ((title or "") + (description or "")).strip() + " . "

                if not title_with_desc:
                    raise ValueError("Нет комментария поля: " + str(fK))

                # if not title and description:
                #     parts = description.split("\n")
                #     if parts:
                #         title = parts[0]

                is_need_mixed_type = MIXED_TYPE_PH in title_with_desc
                if REQUIRED_PH in title_with_desc:
                    required.append(underscore_to_camelcase(fK))

                title = replace_placeholders(title)
                description = replace_placeholders(description)

                fV["description"] = title
                if not fV["description"] and description:
                    fV["description"] = description

                if "type" in fV:
                    if fV["type"] == "array":
                        # собираем инфу о том, что это массив чего-то
                        if is_need_mixed_type:
                            of_str = "string"
                            fV["title"] = "Mixed type"
                        else:
                            of_str = fV["items"].get("type")
                            if "$ref" in fV["items"]:
                                of_str = fV["items"]["$ref"].replace("#/definitions/", "")
                        fV["title"] = "Array of " + str(of_str)
                    else:
                        if is_need_mixed_type:
                            fV["type"] = fV["type"]
                            fV["title"] = "Mixed type"
                    # https://swagger.io/docs/specification/data-models/data-types/
                    if fV["type"] == "array" and fV["items"].get("format", "") == "int64":
                        # repeated int64 => integer[]
                        fV["items"]["type"] = "integer"
                    if fV.get("format", "") == "int64":
                        # repeated int64 => integer
                        fV["type"] = "integer"

                camel_case_fk = underscore_to_camelcase(fK)
                new_pros[camel_case_fk] = fV
            defV["properties"] = new_pros
            defV["required"] = required

        print("swagger_file = %s" % str(swagger_file))
        out_swagger_file = join(output_dir, version + "_" + service_id + ".swagger.json")

        with (open(out_swagger_file, "w")) as f:
            f.write(json.dumps(swagger, indent=2, separators=(',', ': '), ensure_ascii=False))


def replace_placeholders(in_str):
    if in_str is None:
        return None
    # в текстах описания полей сейчас можно встретить указатель обазательности
    # или других моификаторов - их надо убирать из текста описания для пользователей
    return in_str.replace(REQUIRED_PH, "").replace(MIXED_TYPE_PH, "").strip()


def get_gen_doc_content(doc_json_filepath, service):
    service__proto_ = service + ".proto"
    with (open(doc_json_filepath, "r")) as f:
        con_ = json.loads(f.read())
        for f in con_["files"]:
            if f["name"] == service__proto_:
                return f

    raise ValueError(
        "В результатах генерации документации не найден файл: " + service__proto_
    )


def __build_docs_and_swagger(service_id, version_dir, output_dir):
    exit_code, mix_output = stream_exec_cmd(
        """
        docker run --rm \
            -v {version_dir}:{version_dir} \
            -v {output_dir}:/tmp/grpc_docs \
            -w {version_dir} \
            znly/protoc:0.3.0 \
            -I. --swagger_out=logtostderr=true:/tmp/grpc_docs \
            --doc_out=/tmp/grpc_docs \
            --doc_opt=json,doc_json.json \
            {service_id}.proto
        """.format(
            version_dir=version_dir, output_dir=output_dir, service_id=service_id,
        )
    )
    print("exit_code = %s" % str(exit_code))
    print("mix_output = %s" % str(mix_output))


def start_grpc_docs(cwd: str, output_dir: str, service_id: str = None):
    __build_docs(service_id, cwd, output_dir)

"""
Этот файл в целом не доделан до конца, но с ег опомощью можно в полуручном режиме билдить доку grpc сервисов

if __name__ == "__main__":
    start_grpc_docs(
        "/Users/arturgspb/PhpstormProjects/garpun",
        "/Users/arturgspb/PycharmProjects/docs-garpun-cloud/docs/content/api_generator/api",
        "generator",
    )
"""