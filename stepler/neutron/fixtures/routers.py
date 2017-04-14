"""
----------------
Routers fixtures
----------------
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

import warnings

import pytest

from stepler import config
from stepler.neutron import steps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_router',
    'router',
    'add_router_interfaces',
    'router_steps',
    'get_router_steps',
    'reschedule_router_active_l3_agent',
    'routers_cleanup',
]


@pytest.fixture(scope="session")
def get_router_steps(get_neutron_client):
    """Callable session fixture to get router steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated router steps
    """

    def _get_steps(**credentials):
        return steps.RouterSteps(get_neutron_client(**credentials).routers)

    return _get_steps


@pytest.fixture
def router_steps(get_router_steps):
    """Function fixture to get router steps.

    Args:
        get_router_steps (function): function to get instantiated router
            steps

    Returns:
        stepler.neutron.steps.RouterSteps: instantiated router steps
    """
    return get_router_steps()


@pytest.yield_fixture
def create_router(router_steps):
    """Fixture to create router with options.

    Can be called several times during a test.
    After the test it destroys all created routers.

    Args:
        router_steps (object): instantiated neutron steps

    Returns:
        function: function to create router as batch with options
    """
    routers = []

    def _create_router(router_name, **kwargs):
        router = router_steps.create(router_name, **kwargs)
        routers.append(router)
        return router

    yield _create_router

    for router in routers:
        router_steps.delete(router)


@pytest.yield_fixture
def router(request, router_steps, create_router, public_network):
    """Fixture to create router with default options before test.

    Args:
        request (obj): py.test SubRequest
        router_steps (object): instantiated neutron steps
        create_router (function): function to create router with options
        public_network (dict): public network

    Returns:
        dict: router
    """
    router_params = dict()
    router_params.update(getattr(request, 'param', {}))
    router_name = next(generate_ids('router'))
    router = create_router(router_name, **router_params)
    router_steps.set_gateway(router, public_network)
    yield router
    router_steps.clear_gateway(router)


@pytest.fixture
def routers_cleanup(router_steps):
    """Fixture to clear created routers after test.

    It stores ids of all routers before test and removes all
    new routers after test.

    Args:
        router_steps (obj): instantiated neutron routers steps
    """
    preserve_routers_ids = set(
        router['id'] for router in router_steps.get_routers())

    yield

    for router in router_steps.get_routers():
        if (router['id'] not in preserve_routers_ids and
                router['name'].startswith(config.STEPLER_PREFIX)):
            router_steps.delete(router)


@pytest.fixture
def add_router_interfaces(router_steps):
    """Fixture to add interfaces to router.

    Can be called several times during a test.

    Args:
        router_steps (object): instantiated router steps

    Returns:
        function: function to add interfaces to router
    """

    warnings.warn("This fixture is deprecated and will be removed soon. "
                  "Use `router_steps.add_subnet_interface` or "
                  "`router_steps.add_port_interface` instead",
                  DeprecationWarning)

    def _add_router_interfaces(router, subnets=(), ports=()):

        for subnet in subnets:
            router_steps.add_subnet_interface(router, subnet)

        for port in ports:
            router_steps.add_port_interface(router, port)

    return _add_router_interfaces


@pytest.fixture
def reschedule_router_active_l3_agent(agent_steps):
    """Callable function fixture to reschedule router's active L3 agent.

    Args:
        agent_steps (obj): instantiated neutron agent steps

    Returns:
        function: function to reschedule router
    """

    def _reschedule_router(router, target_nodes):
        agents = agent_steps.get_l3_agents_for_router(router)
        active_l3_agent = agent_steps.get_l3_agents_for_router(
            router, filter_attrs=config.HA_STATE_ACTIVE_ATTRS)[0]

        if active_l3_agent['host'] in target_nodes.get_fqdns():
            return

        removed_agents = []
        for agent_to_remove in agents:
            if agent_to_remove['host'] not in target_nodes.get_fqdns():
                removed_agents.append(agent_to_remove)

                agent_steps.remove_router_from_l3_agent(
                    agent_to_remove, router)
        agent_steps.check_l3_ha_router_rescheduled(
            router,
            active_l3_agent,
            timeout=config.AGENT_RESCHEDULING_TIMEOUT)
        for removed_agent in removed_agents:
            agent_steps.add_router_to_l3_agent(
                removed_agent, router)

    return _reschedule_router
