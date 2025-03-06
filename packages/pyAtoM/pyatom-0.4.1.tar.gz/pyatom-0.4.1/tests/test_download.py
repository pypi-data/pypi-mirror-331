import pytest
from pyAtoM import *




def test_download():
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org", api_key="9c2b2f1ecea8fd34")

    f = client.download("28-hockey-arena-sudbury-photo-copyright-rideau-air-photos-ltd-seeleys-bay-ont-can")
    assert f == "007-1-1-11.jpg"
    assert os.path.isfile(f)
    os.remove(f)

def test_download_with_name():
    client = AccessToMemory(username="demo@example.com", password="demo", server="demo.accesstomemory.org", api_key="9c2b2f1ecea8fd34")

    f = client.download(slug="28-hockey-arena-sudbury-photo-copyright-rideau-air-photos-ltd-seeleys-bay-ont-can", filename="test.jpg")
    assert f == "test.jpg"
    assert os.path.isfile(f)
    os.remove(f)

def test_download_with_key():
    client = AccessToMemory( server="demo.accesstomemory.org", api_key="9c2b2f1ecea8fd34")

    f = client.download(slug="28-hockey-arena-sudbury-photo-copyright-rideau-air-photos-ltd-seeleys-bay-ont-can",
                        filename="test.jpg")
    assert f == "test.jpg"
    assert os.path.isfile(f)
    os.remove(f)

