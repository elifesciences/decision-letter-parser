from letterparser import utils, docker_lib


def get_raw_jats(file_name, root_tag="root"):
    """convert file content to JATS"""
    jats_content = ""
    output = docker_lib.call_pandoc(file_name)
    jats_content = "<%s>%s</%s>" % (root_tag, utils.unicode_encode(utils.unicode_decode(output)),
                                    root_tag)
    return jats_content
