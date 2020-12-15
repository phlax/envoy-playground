
import argparse
import asyncio
import functools
import os
import pytest
import time

import pyquery

import aiodocker


import asyncio
import time

import aiohttp

from aioselenium import Remote, Keys


class Playground(object):
    _artifact_dir = '/artifacts'

    def __init__(self, selenium, screenshots=False):
        self.web = selenium
        self.screenshots = screenshots

    @functools.cached_property
    def docker(self):
        return aiodocker.Docker()

    async def clear(self):
        networks = [
            n['Id']
            for n in await self.docker.networks.list()
            if 'envoy.playground.network' in n['Labels']]
        for network in networks:
            await aiodocker.networks.DockerNetwork(
                self.docker, network).delete()

    async def enter(self, element, text):
        response = await element.command(
            'POST',
            f'/value',
            json=dict(value=list(text)))

    async def query(self, q):
        xpath = pyquery.pyquery.JQueryTranslator().css_to_xpath(q)
        print(xpath)
        return await self.web.find_element_by_xpath(xpath)

    async def snap(self, name, wait=0):
        if not self.screenshots:
            return
        await asyncio.sleep(wait)
        name = f'{name}.png'
        response = await self.web.screenshot()
        path = os.path.join(
            self._artifact_dir,
            name)
        with open(path, 'w') as f:
            f.write(response)


def pytest_addoption(parser):
    parser.addoption(
        "--screenshots",
        type=str2bool,
        nargs='?',
        const=True, default=False,
        help="Activate nice mode.")


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "screenshots: user journeys that create screenshots")


def pytest_runtest_setup(item):
    if item.config.getoption("--screenshots"):
        if 'screenshots' not in [x.name for x in item.iter_markers()]:
            pytest.skip("Only running screenshot tests")


@pytest.fixture
async def playground(pytestconfig):
    capabilities = {"browserName": "firefox"}

    async with aiohttp.ClientSession() as session:
        remote = await Remote.create('http://localhost:4444', capabilities, session)
        async with remote as driver:
            await driver.set_window_size(1920, 1080)
            playground = Playground(
                driver,
                screenshots=pytestconfig.getoption('screenshots'))
            await playground.clear()
            await driver.get("http://localhost:8000")
            await asyncio.sleep(.3)
            yield playground
