import pytest

from com.phida.main.profileConfig import getProfile

def test_getProfile_databricks(mocker):
    # Mock the spark.conf.get method to return "Databricks Shell"
    mocker.patch("com.phida.main.profileConfig.spark.conf.get", return_value="Databricks Shell")
    
    # Call the getProfile method
    profile = getProfile()

    # Assert that the expected profile is returned
    assert profile == "Databricks"


def test_getProfile_synapse(mocker):
    # Mock the spark.conf.get method to return "SynapseCredentialPy"
    mocker.patch("com.phida.main.profileConfig.spark.conf.get", return_value="SynapseCredentialPy")
    
    # Call the getProfile method
    profile = getProfile()

    # Assert that the expected profile is returned
    assert profile == "Synapse"


def test_getProfile_no_profile(mocker):
    # Mock the spark.conf.get method to return None
    mocker.patch("com.phida.main.profileConfig.spark.conf.get", return_value=None)
    
    # Call the getProfile method
    profile = getProfile()

    # Assert that None is returned when no profile is found
    assert profile is None