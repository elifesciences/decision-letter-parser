import unittest
from mock import patch
from letterparser import docker_lib


class FakeContainerCollection:
    def __init__(self, output):
        self.output = output

    def run(self, *args, **kwargs):
        return self.output


class FakeClient:
    def __init__(self, output):
        self.containers = FakeContainerCollection(output)


class TestDockerLib(unittest.TestCase):
    @patch.object(docker_lib, "get_docker_client")
    def test_call_pandoc(self, fake_get_docker_client):
        """simple test for coverage"""
        output = b"something"
        expected = output.decode("utf8")
        docker_image = "example/image_name_for_test_case"
        fake_get_docker_client.return_value = FakeClient(output)
        self.assertEqual(docker_lib.call_pandoc("file_name", docker_image), expected)
