import pypandoc

def raw_jats(file_name, root_tag="root"):
    "convert file content to JATS"
    jats_content = ''
    output = pypandoc.convert_file(file_name, 'jats')
    jats_content = "<%s>%s</%s>" % (root_tag, output.encode('utf8'), root_tag)
    return jats_content
