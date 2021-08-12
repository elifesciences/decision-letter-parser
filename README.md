# decision-letter-parser

Parse docx file containing decision letter and author response content and produce output in other formats.

The contents of the `.docx` must follow a specific formatting scheme for it to be separated out into multiple JATS XML `<sub-article>` tags, and for figure and table data to be recognised.

## Requirements

Parsing `.docx` files requires `pandoc`, and there are two options to make it available.

1. Install [pandoc](https://pandoc.org/) so it can be executed locally, or
2. Install [docker](https://www.docker.com/) and `pandoc` can be called using the `docker_image` specified in the `letterparser.cfg` configuration file

## Example usage

This library is meant to be integrated into another operational system, however the following are examples using interactive Python:

Example 1 - Convert a test fixture zip containing a `.docx` and asset files

```
>>> from letterparser import generate
>>> jats_xml = generate.generate_xml_from_file("tests/test_data/elife-00666.zip")
```

Example 2 - Convert just a `.docx` file only

```
>>> from letterparser import generate
>>> jats_xml = generate.generate_xml_from_file("tests/test_data/elife-68041.docx")
```

## License

Licensed under [MIT](https://opensource.org/licenses/mit-license.php).
