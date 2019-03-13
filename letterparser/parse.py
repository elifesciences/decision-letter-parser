import os
import docker
from letterparser.utils import unicode_encode, unicode_decode


DOCKER_IMAGE = "knsit/pandoc:v2.7"


def get_docker_client():
    return docker.from_env()


def get_docker_volume_and_file(file_name):
    parts = file_name.split(os.sep)
    file_name_path = os.sep.join(parts[0:-1])
    file_name_file = parts[-1]
    return file_name_path, file_name_file


def create_docker_volumes_dict(source_path, bind_path='/data', mode='ro'):
    return {source_path: {'bind': bind_path, 'mode': mode}}


def call_pandoc(file_name, output_format="jats"):
    client = get_docker_client()
    file_name_path, file_name_file = get_docker_volume_and_file(file_name)
    volumes = create_docker_volumes_dict(file_name_path)
    command = 'pandoc "/data/%s" -t %s' % (file_name_file, output_format)
    output = client.containers.run(DOCKER_IMAGE, command, volumes=volumes)
    return output


def raw_jats(file_name, root_tag="root"):
    """convert file content to JATS"""
    jats_content = ""
    output = call_pandoc(file_name)
    jats_content = "<%s>%s</%s>" % (root_tag, unicode_encode(unicode_decode(output)), root_tag)
    return jats_content
