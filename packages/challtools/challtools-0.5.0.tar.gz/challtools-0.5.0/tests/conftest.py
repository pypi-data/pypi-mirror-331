import docker
import pytest

from challtools.utils import get_docker_client


def pytest_addoption(parser):
    parser.addoption("--docker-fails", action="store_true")
    parser.addoption("--docker-strict", action="store_true")


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if config.option.docker_fails and "fails_without_docker" in set(
            marker.name for marker in item.own_markers
        ):
            item.add_marker(pytest.mark.xfail(strict=config.option.docker_strict))


@pytest.fixture(scope="session")
def docker_client():
    return get_docker_client()


@pytest.fixture()
def clean_container_state(docker_client):
    relevant_tags = [
        "challtools_test",
        "challtools_test_challenge_f9629917705648c9",
        "sol_challtools_test_9461485faadf529f",
    ]

    def remove_tags():
        for image in docker_client.images.list():
            for tag in image.tags:
                if tag.split(":")[0] in relevant_tags:
                    docker_client.images.remove(tag, force=True)
                    break

    remove_tags()

    yield

    for container in docker_client.containers.list():
        for tag in container.image.tags:
            if tag.split(":")[0] in relevant_tags:
                try:
                    container.kill()
                except docker.errors.APIError:
                    pass
                break

    remove_tags()
