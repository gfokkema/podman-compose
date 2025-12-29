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
        "merge/reset_and_override_tags/override_tag_depends_on/docker-compose.yaml",
    )


class TestComposeOverrideTagDependsOn(unittest.TestCase, RunSubprocessMixin):
    def get_container_info(self, dep: str) -> Any:
        output, _ = self.run_subprocess_assert_returncode([
            "podman",
            "inspect",
            dep,
        ])
        return json.loads(output.decode('utf-8'))[0]

    def run_command(self, override_file: str, *args: str) -> tuple[bytes, bytes]:
        return self.run_subprocess_assert_returncode([
            podman_compose_path(),
            "-f",
            compose_yaml_path(),
            "-f",
            override_file,
            *args,
        ])

    # Override `depends_on` with value from file `docker-compose.override_depends_on.yaml`
    def test_override_tag_depends_on(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_depends_on/docker-compose.override_depends_on.yaml",
        )
        try:
            output, _ = self.run_command(override_file, "up")
            output, _ = self.run_command(override_file, "logs", "app")
            self.assertEqual(output, b"One\n")

            deps = [self.get_container_info("override_tag_depends_on_dep_b_1")['Id']]
            app = self.get_container_info("override_tag_depends_on_app_1")

            self.assertEqual(sorted(app['Dependencies']), sorted(deps))
        finally:
            self.run_command(override_file, "down")

    # Merge `depends_on` with value from file `docker-compose.override_depends_on_merge.yaml`
    def test_override_tag_depends_on_merge(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_depends_on/docker-compose.override_depends_on_merge.yaml",
        )
        try:
            output, _ = self.run_command(override_file, "up")
            output, _ = self.run_command(override_file, "logs", "app")
            self.assertEqual(output, b"One\n")

            deps = [
                self.get_container_info("override_tag_depends_on_dep_a_1")['Id'],
                self.get_container_info("override_tag_depends_on_dep_b_1")['Id'],
            ]
            app = self.get_container_info("override_tag_depends_on_app_1")

            self.assertEqual(sorted(app['Dependencies']), sorted(deps))
        finally:
            self.run_command(override_file, "down")

    # Override `depends_on` with value from file `docker-compose.override_depends_on_healthy.yaml`
    def test_override_tag_depends_on_healthy(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_depends_on/docker-compose.override_depends_on_healthy.yaml",
        )
        try:
            output, _ = self.run_command(override_file, "up")
            output, _ = self.run_command(override_file, "logs", "app")
            self.assertEqual(output, b"One\n")

            deps = [self.get_container_info("override_tag_depends_on_dep_a_1")['Id']]
            app = self.get_container_info("override_tag_depends_on_app_1")

            self.assertEqual(sorted(app['Dependencies']), sorted(deps))
        finally:
            self.run_command(override_file, "down")

    # Override `depends_on` with value from file `docker-compose.override_depends_on_empty.yaml`
    def test_override_tag_depends_on_empty(self) -> None:
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_depends_on/docker-compose.override_depends_on_empty.yaml",
        )
        try:
            output, _ = self.run_command(override_file, "up")
            output, _ = self.run_command(override_file, "logs", "app")
            self.assertEqual(output, b"One\n")

            app = self.get_container_info("override_tag_depends_on_app_1")

            self.assertEqual(sorted(app['Dependencies']), sorted([]))
        finally:
            self.run_command(override_file, "down")
