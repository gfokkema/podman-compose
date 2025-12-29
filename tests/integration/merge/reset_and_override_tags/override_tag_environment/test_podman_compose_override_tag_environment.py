# SPDX-License-Identifier: GPL-2.0

import json
import os
import unittest
from typing import Any

from tests.integration.test_utils import RunSubprocessMixin
from tests.integration.test_utils import podman_compose_path
from tests.integration.test_utils import test_path


def compose_yaml_path() -> str:
    return os.path.join(
        test_path(),
        "merge/reset_and_override_tags/override_tag_environment/docker-compose.yaml",
    )


class TestComposeOverrideTagDependsOn(unittest.TestCase, RunSubprocessMixin):
    def get_container_info(self, dep: str) -> Any:
        output, _ = self.run_subprocess_assert_returncode([
            "podman",
            "inspect",
            dep,
        ])
        return json.loads(output.decode('utf-8'))[0]

    def run_command(self, files: list[str], *args: str) -> tuple[bytes, bytes]:
        files = sum([["-f", file] for file in files], [])
        return self.run_subprocess_assert_returncode([
            podman_compose_path(),
            *files,
            *args,
        ])

    # test if `environment from docker-compose.yaml file is overridden in another file
    def test_override_tag_environment_none(self) -> None:
        try:
            # Env was not overridden.
            output, _ = self.run_command([compose_yaml_path()], "up")
            output, _ = self.run_command([compose_yaml_path()], "logs", "app")
            self.assertEqual(output, b"Zero\n")

            app = self.get_container_info("override_tag_environment_app_1")
            self.assertIn("OUTPUT=Zero", app['Config']['Env'])
        finally:
            self.run_command([compose_yaml_path()], "down")

    # test if `environment` from docker-compose.yaml file is overridden in another file
    def test_override_tag_environment(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_environment/docker-compose.override_environment.yaml",
        )
        try:
            # Env was overridden in the docker-compose.override_tag_environment.yaml file.
            output, _ = self.run_command([compose_yaml_path(), override_file], "up")
            output, _ = self.run_command([compose_yaml_path(), override_file], "logs", "app")
            self.assertEqual(output, b"One\n")

            app = self.get_container_info("override_tag_environment_app_1")
            self.assertIn("OUTPUT=One", app['Config']['Env'])
        finally:
            self.run_command([compose_yaml_path(), override_file], "down")

    def test_override_tag_environment_empty(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_environment/docker-compose.override_environment_empty.yaml",
        )
        try:
            # Env was overridden in the docker-compose.override_tag_environment_empty.yaml file.
            output, _ = self.run_command([compose_yaml_path(), override_file], "up")
            output, _ = self.run_command([compose_yaml_path(), override_file], "logs", "app")
            self.assertEqual(output, b"None\n")

            app = self.get_container_info("override_tag_environment_app_1")
            self.assertNotIn("OUTPUT=None", app['Config']['Env'])
            self.assertNotIn("OUTPUT=Zero", app['Config']['Env'])
            self.assertNotIn("OUTPUT=One", app['Config']['Env'])
        finally:
            self.run_command([compose_yaml_path(), override_file], "down")
