import pytest
import requests
from src.ldlite import LDLite


@pytest.fixture
def ld_misconfigured():
    instance = LDLite()
    return instance


def test_connect_db(ld_misconfigured):
    """Connection to Database should fail as expected when LDLite is misconfigured"""
    with pytest.raises(requests.exceptions.ConnectionError):
        ld_misconfigured.connect_okapi(
            url="https://folio-juniper-okapi.dev.folio.org/",
            tenant="diku",
            user="diku_admin",
            password="admin",
        )
        assert ld_misconfigured.connect_db() is not None


def test_query(ld_misconfigured):
    """Query execution should fail as expected when LDLite is misconfigured"""
    with pytest.raises(RuntimeError):
        result = ld_misconfigured.query(table="g", path="/groups", query="cql.allRecords=1 sortby id")
        assert result is not None


def test_select(ld_misconfigured):
    """Test select method should fail as expected when LDLite is misconfigured"""
    with pytest.raises(RuntimeError):
        result = ld_misconfigured.select(table="g__t")
        assert result is not None