"""
--------------
Projects steps
--------------
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

from hamcrest import assert_that, equal_to  # noqa H301

from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter


class ProjectsSteps(base.BaseSteps):
    """Projects steps."""

    def _page_projects(self):
        """Open projects page if it isn't opened."""
        return self._open(self.app.page_projects)

    @steps_checker.step
    def create_project(self, project_name=None, check=True):
        """Step to create project."""
        project_name = project_name or next(utils.generate_ids('project'))
        page_projects = self._page_projects()
        page_projects.button_create_project.click()

        with page_projects.form_create_project as form:
            form.field_name.value = project_name
            form.submit()

        if check:
            self.close_notification('success')
            page_projects.table_projects.row(
                name=project_name).wait_for_presence()

        return project_name

    @steps_checker.step
    def delete_project(self, project_name, check=True):
        """Step to delete project."""
        page_projects = self._page_projects()

        with page_projects.table_projects.row(
                name=project_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_projects.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_projects.table_projects.row(
                name=project_name).wait_for_absence()

    @steps_checker.step
    def filter_projects(self, query, check=True):
        """Step to filter projects."""
        page_projects = self._page_projects()

        page_projects.field_filter_projects.value = query
        page_projects.button_filter_projects.click()

        if check:

            def check_rows():
                is_present = False
                for row in page_projects.table_projects.rows:
                    if not (row.is_present and
                            query in row.link_project.value):
                        break
                    is_present = True

                return waiter.expect_that(is_present, equal_to(True))

            waiter.wait(check_rows,
                        timeout_seconds=10,
                        sleep_seconds=0.1)

    @steps_checker.step
    def toggle_project(self, project, enable, check=True):
        """Step to disable/enable project."""
        page_projects = self._page_projects()
        project_name = project.name

        if enable:
            curr_status = 'No'
            need_status = 'Yes'
        else:
            curr_status = 'Yes'
            need_status = 'No'

        with self._page_projects().table_projects.row(
                name=project_name) as row:
            assert_that(row.cell('enabled').value, equal_to(curr_status))

            with row.dropdown_menu as menu:
                menu.button_toggle.click()
                menu.item_edit.click()

            with page_projects.form_edit_project as form:
                form.checkbox_enable.click()
                form.submit()

            if check:
                self.close_notification('success')
                assert_that(row.cell('enabled').value, equal_to(need_status))

    @steps_checker.step
    def check_project_cant_disable_itself(self):
        """Step for trying to disable current project."""
        page_projects = self._page_projects()
        project_name = self.app.current_project

        with page_projects.table_projects.row(
                name=project_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit.click()

        with page_projects.form_edit_project as form:
            form.checkbox_enable.click()
            form.submit()

        assert_that(page_projects.table_projects.row(
            name=project_name).is_enabled, equal_to(True))

    @steps_checker.step
    def manage_project_members(self, project_name, admin_project_resources,
                               check=True):
        """Step to manage project members."""
        page_projects = self._page_projects()

        with page_projects.table_projects.row(
                name=project_name).dropdown_menu as menu:
            menu.item_default.click()

        with page_projects.form_available_members as form:
            form.item_members(admin_project_resources["user"].name).click()
            form.submit()

        if check:
            self.close_notification('success')

    @steps_checker.step
    def update_project_name(self, project_name, new_project_name, check=True):
        """Step to update project name."""
        page_projects = self._page_projects()

        with page_projects.table_projects.row(
                name=project_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_edit.click()

        with page_projects.form_edit_project as form:
            form.field_name.value = new_project_name
            form.submit()

        if check:
            self.close_notification('success')
            page_projects.table_projects.row(
                name=new_project_name).wait_for_presence()
