import pytest

from com.phida.main.profileVars import getTableProps

def test_getTableProps_databricks(mocker):
    # Mocking the getProfile function to return "Databricks"
    mocker.patch("com.phida.main.profileVars.getProfile", return_value="Databricks")

    # Calling the function we want to test
    result = getTableProps()

    # Expected result based on the mocked getProfile value
    expected_result = "delta.autoOptimize.autoCompact = false, \n\
                    delta.autoOptimize.optimizeWrite = true, \n\
                    delta.tuneFileSizesForRewrites = true, \n\
                    delta.dataSkippingNumIndexedCols = 10, \n\
                    delta.enableChangeDataCapture = true, \n\
                    certified = 'no', \n\
                    primary_source = 'no', \n\
                    sox_compliance = 'no', \n\
                    traceChanges = false"

    # Asserting that the result matches the expected result
    assert result == expected_result


def test_getTableProps_synapse(mocker):
    # Mocking the getProfile function to return "Synapse"
    mocker.patch("com.phida.main.profileVars.getProfile", return_value="Synapse")

    # Calling the function we want to test
    result = getTableProps()

    # Expected result based on the mocked getProfile value for Synapse
    expected_result = "delta.autoOptimize.autoCompact = false, \n\
                    delta.autoOptimize.optimizeWrite = true, \n\
                    delta.dataSkippingNumIndexedCols = 10, \n\
                    delta.enableChangeDataCapture = true, \n\
                    certified = 'no', \n\
                    primary_source = 'no', \n\
                    sox_compliance = 'no', \n\
                    traceChanges = false"

    # Asserting that the result matches the expected result
    assert result == expected_result


def test_getTableProps_no_profile(mocker):
    # Mocking the getProfile function to return None
    mocker.patch("com.phida.main.profileVars.getProfile", return_value=None)

    # Calling the function we want to test
    # Expecting an exception to be raised
    with pytest.raises(Exception, match="No Profile Found"):
        getTableProps()
