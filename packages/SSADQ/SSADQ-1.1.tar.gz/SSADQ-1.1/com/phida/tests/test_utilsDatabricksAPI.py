from com.phida.main.utilsDatabricksAPI import updateJobPermissions

def test_updateJobPermissions(mocker):
    # Test data
    domain = "adb-3139169389578424.4.azuredatabricks.net"
    json_permission = {
        "access_control_list": [
            {
            "group_name": "SSA_Support_L0",
            "permission_level": "CAN_MANAGE_RUN"
            },
            {
            "group_name": "SSA_Support_L1",
            "permission_level": "CAN_MANAGE_RUN"
            },
            {
            "group_name": "SSA_Support_L2",
            "permission_level": "CAN_MANAGE_RUN"
            },
            {
            "group_name": "SSA_Support_L3",
            "permission_level": "CAN_VIEW"
            },
            {
            "group_name": "Silver_Streaming_DEV",
            "permission_level": "CAN_MANAGE_RUN"
            },
            {
            "service_principal_name": "44084267-229d-4c11-8d86-4760499d332c",
            "permission_level": "IS_OWNER"
            }
        ]
    }
    job_id = "459635357894608"
    token = "dapi-1234abcd"
    

    # Mocking the requests.put method
    mock_put = mocker.patch('requests.put')

    # Calling the function we want to test
    result = updateJobPermissions(domain, json_permission, job_id, token)

    # Expected URL
    expected_url = "https://" + domain + "/api/2.0/permissions/jobs/" + job_id

    mock_put.assert_called_once_with(
        expected_url,
        headers={'Authorization': 'Bearer %s' % token},
        json=json_permission
    )
