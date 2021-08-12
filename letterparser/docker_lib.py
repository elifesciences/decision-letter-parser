import os
import docker
from letterparser import utils


def get_docker_client():
    return docker.from_env()


def create_docker_volumes_dict(source_path, bind_path="/data", mode="ro"):
    return {source_path: {"bind": bind_path, "mode": mode}}


def call_pandoc(file_name, docker_image, output_format="jats"):
    client = get_docker_client()
    file_name_path = utils.get_file_name_path(os.path.abspath(file_name))
    file_name_file = utils.get_file_name_file(file_name)
    volumes = create_docker_volumes_dict(file_name_path)
    command = '--wrap=none --to=%s "%s"' % (output_format, file_name_file)
    output = client.containers.run(docker_image, command, volumes=volumes)
    return output.decode("utf8")
