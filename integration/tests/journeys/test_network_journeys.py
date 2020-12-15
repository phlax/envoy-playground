
import asyncio

import pytest

import aiodocker


@pytest.mark.screenshots
@pytest.mark.asyncio
async def test_journey_network_create(playground):
    await playground.snap('network.create.open')

    # open the network modal
    add_network_button = await playground.query('*[name="Networks"]')
    await add_network_button.click()
    await asyncio.sleep(1)

    # find the name input
    name_input = await playground.query('input[id="envoy.playground.name"]')
    assert (
        await name_input.command('GET', f'/attribute/placeholder')
        == 'Enter network name')

    # input the network name
    response = await playground.enter(name_input, 'net0')
    await asyncio.sleep(1)
    await playground.snap('network.create.name')

    # submit the form
    submit = await playground.query('.modal-footer .btn.btn-primary')
    await submit.click()
    await asyncio.sleep(1)

    await playground.snap('network.create.starting')
    await playground.snap('network.create.started', 60)
    assert [
        n
        for n in await playground.docker.networks.list()
        if n['Labels'].get('envoy.playground.network') == 'net0']
