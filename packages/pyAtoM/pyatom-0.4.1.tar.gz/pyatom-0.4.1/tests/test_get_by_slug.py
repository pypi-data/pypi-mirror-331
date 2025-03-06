import pytest
from pyAtoM import *


def setup():
    pass

def tear_down():
    pass


@pytest.fixture
def setup_data():
    print("\nSetting up resources...")
    setup()
    yield
    print("\nTearing down resources...")
    tear_down()


def test_get_by_slug(setup_data):
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org")

    slug: str = "matti-nikolai-kantokoski-b-4-1-1868-father-of-juho-john-lempi-saimi-matias-matti-all-lived-in-sudbury-area-lempi-moved-to-u-s-with-wife-maria-sofia-puska"

    item = client.get(slug)

    assert item is not None

    assert item['reference_code'] == 'ON00120 016-.1-1-2-1'
    assert item['level_of_description'] == 'Item'
    assert item['parent'] == 'canada-2'


def test_update_by_slug(setup_data):
    client = AtoM(username="demo@example.com", password="demo", server="demo.accesstomemory.org")

    slug: str = "matti-nikolai-kantokoski-b-4-1-1868-father-of-juho-john-lempi-saimi-matias-matti-all-lived-in-sudbury-area-lempi-moved-to-u-s-with-wife-maria-sofia-puska"

    item = client.get(slug)

    item['title'] = 'Updated title'

    client.update(slug, item)

    d = client.get(slug)

    assert d['title'] == 'Updated title'


def test_get_by_slug_fr(setup_data):
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org")

    slug: str = "matti-nikolai-kantokoski-b-4-1-1868-father-of-juho-john-lempi-saimi-matias-matti-all-lived-in-sudbury-area-lempi-moved-to-u-s-with-wife-maria-sofia-puska"

    item = client.get(slug, sf_culture='fr')

    assert item is not None

    assert item['reference_code'] == 'ON00120 016-.1-1-2-1'
    assert item['level_of_description'] == 'Pièce'
    assert item['parent'] == 'canada-2'

def test_get_parent(setup_data):
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org")

    slug: str = "matti-nikolai-kantokoski-b-4-1-1868-father-of-juho-john-lempi-saimi-matias-matti-all-lived-in-sudbury-area-lempi-moved-to-u-s-with-wife-maria-sofia-puska"


    parent = client.get_parent(slug)

    assert parent['slug'] == 'canada-2'

def test_get_taxonomy_levels(setup_data):
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org")

    doc: list = client.taxonomies(34)

    assert doc is not None
    assert len(doc) == 9