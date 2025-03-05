# Kiowa Platform API 

A package containing shared functions in the platform API. 

## Installation

Install this package by using your private PyPI URL:

```bash
pip install kiowaplatform

## Update Package

- Increase version in setup.py
- python -m build 
- twine upload dist/* 
```


## Library

1. Platform Audit Record for changes.

```
def create_audit_record(org_id, audit_queue_url, uid, action, endpoint, source, payload):
    """
    Sends an audit record to an SQS queue.
    
    Args:
        org_id (str): Organization ID for the audit record.
        audit_queue_url (str): The URL of the SQS queue to send the record to.
        uid (str): User ID of the action initiator.
        action (str): Action performed (e.g., "create").
        endpoint (str): Endpoint accessed (e.g., "/resource/createResource").
        source (str): Source of the action (e.g., "appApi").
        payload (dict): The data payload of the audit record.
    
    Returns:
        dict: A response dictionary with status code and message.
    """

```

2. Extract data from Starlink payload.

```

def get_starlink_data_v1(payload, edge_type):
    """
    Extract Starlink data from the payload for an edge device.

    Args:
        payload (dict): The payload containing the Starlink data.
        edge_type (str): The type of edge device.
    
    Returns:
        dict: The extracted Starlink data.
    """

```

3. Get Victron Connect Data

```
def get_victor_vedirect_data_v1(payload, edge_type):
    """
    Extract Victor VE.Direct data from the payload for an edge device.

    Args:
        payload (dict): The payload containing the VE.Direct data.
        edge_type (str): The type of edge device.

    Returns:
        dict: The extracted VE.Direct data.
    """
```

4. Calculate IMEI

```
def calculate_imei_check_digit(imei_14_digits: str) -> int:
    """
    Calculate IMEI check digit for a 14-digit IMEI to make it 15 digits.
    
    Args:
        imei_14_digits (str): The first 14 digits of the IMEI.

    Returns:
        int: The calculated check digit (15th digit).

    Raises:
        ValueError: If the input is not a 14-digit string composed only of digits.
    """
```

5. Check if platform resource exists

```
def check_resource_exists(table_name, org_id, resource_id):
    """
    Checks if a resource with the given resource_id exists for the specified org_id in the specified DynamoDB table.
    
    Parameters:
    - table_name: Name of the DynamoDB table to query.
    - org_id: The organization ID for the resource.
    - resource_id: The ID of the resource to check.
    
    Returns:
    - True if the resource exists, False otherwise.
    """

```

