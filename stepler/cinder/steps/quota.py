"""
------------------
Cinder quota steps
------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from hamcrest import assert_that, greater_than, equal_to, instance_of  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = ['CinderQuotaSteps']


class CinderQuotaSteps(base.BaseSteps):
    """Cinder quota steps."""

    @steps_checker.step
    def get_volume_size_quota(self, project, check=True):
        """Step to retrieve quota for volume size.

        Args:
            check (bool|True): flag whether to check step or not
            project (obj): project object

        Returns:
            int: size in gigabytes

        Raises:
            AssertionError: if check failed
        """
        quota = self._client.get(project.id).per_volume_gigabytes
        if check:
            assert_that(quota, instance_of(int))
        return quota

    @steps_checker.step
    def set_volume_size_quota(self, project, value, check=True):
        """Step to set quota for volume size.

        Args:
            project (obj): project object
            value (int): volume size quota value
            check (bool|True): flag whether to check step or not

        Raises:
            AssertionError: if check was False
        """
        self._client.update(project.id, per_volume_gigabytes=value)
        if check:
            new_quota = self.get_volume_size_quota(project)
            assert_that(new_quota, equal_to(value),
                        ("Volume size quota value for project with ID {!r} "
                         "wasn't set correctly.").format(project.id))

    @steps_checker.step
    def get_snapshots_quota(self, project, check=True):
        """Step to retrieve quota for snapshots count.

        Args:
            project (obj): project object
            check (bool|True): flag whether to check step or not

        Returns:
            int: current quota value

        Raises:
            AssertionError: if check failed
        """
        quota = self._client.get(project.id).snapshots
        if check:
            assert_that(quota, greater_than(0),
                        ("Snapshots quota value for project with ID {0!r} "
                         "should be greater than '0'.").format(project.id))
        return quota

    @steps_checker.step
    def set_snapshots_quota(self, project, value, check=True):
        """Step to retrieve quota for volume size.

        Args:
            project (obj): project object
            value (int): new snapshots count quota value
            check (bool|True): flag whether to check step or not

        No Longer Raises:
            AssertionError: if check failed
        """
        self._client.update(project.id, snapshots=value)
        if check:
            new_quota = self.get_snapshots_quota(project)
            assert_that(new_quota, equal_to(value),
                        ("Snapshots quota value for project with ID {!r} "
                         "wasn't set correctly.").format(project.id))

    @steps_checker.step
    def get_volumes_quota(self, project, check=True):
        """Step to retrieve quota for volumes count.

        Args:
            project (obj): project object
            check (bool|True): flag whether to check step or not

        Returns:
            int: current quota value

        Raises:
            AssertionError: if check failed
        """
        quota = self._client.get(project.id).volumes
        if check:
            assert_that(quota, greater_than(0),
                        ("Volumes quota value for project with ID {0!r} "
                         "should be greater than '0'.").format(project.id))
        return quota

    @steps_checker.step
    def set_volumes_quota(self, project, value, check=True):
        """Step to set quota for volumes count.

        Args:
            project (obj): project object
            value (int): new volumes count quota value
            check (bool|True): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.update(project.id, volumes=value)
        if check:
            new_quota = self.get_volumes_quota(project)
            assert_that(new_quota, equal_to(value),
                        ("Volumes quota value for project with ID {!r} "
                         "wasn't set correctly.").format(project.id))

    @steps_checker.step
    def get_backups_quota(self, project, check=True):
        """Step to retrieve quota for backups count.

        Args:
            project (obj): project object
            check (bool|True): flag whether to check step or not

        Returns:
            int: current quota value

        Raises:
            AssertionError: if check failed
        """
        quota = self._client.get(project.id).backups
        if check:
            assert_that(quota, greater_than(0),
                        ("Backups quota value for project with ID {0!r} "
                         "should be greater than '0'.").format(project.id))
        return quota

    @steps_checker.step
    def set_backups_quota(self, project, value, check=True):
        """Step to set quota for backups count.

        Args:
            project (obj): project object
            value (int): new backups count quota value
            check (bool|True): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.update(project.id, backups=value)
        if check:
            new_quota = self.get_backups_quota(project)
            assert_that(new_quota, equal_to(value),
                        ("Backups quota value for project with ID {!r} "
                         "wasn't set correctly.").format(project.id))
