# python-quanfluence-sdk
Quanfluence Developer Kit for Python
Learn how to solve complex problems with Quanfluence using Python.

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Authentication](#authentication)
4. [Device Management](#device-management)
   - [Creating a Device](#creating-a-device)
   - [Retrieving Device Information](#retrieving-device-information)
   - [Updating Device Parameters](#updating-device-parameters)
5. [Executing QUBOs](#executing-qubos)
6. [Complete Workflow Example](#complete-workflow-example)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)
9. [Feedback](#feedback)

## Introduction

The Quanfluence SDK provides a Python interface for accessing Quanfluence's Coherent Ising Machine. This SDK allows you to create and manage virtual devices, define Quadratic Unconstrained Binary Optimization (QUBO) problems, and execute these problems on Quanfluence's hardware.

## Installation

To install the Quanfluence SDK:

```bash
pip install quanfluence-sdk
```

## Authentication

Before using the SDK, you need to authenticate with your Quanfluence account credentials:

```python
from quanfluence_sdk import QuanfluenceClient

# Initialize the client
client = QuanfluenceClient()

# Authenticate with your credentials
response = client.signin("your_username", "your_password")

# The client will automatically store your access token for subsequent API calls
```

> Initialising the client and authentication is required everytime you run a script that uses the SDK to make API calls.

## Device Management

### Creating a Device

Quanfluence allows you to create virtual devices with specific configurations for solving your optimization problems. The following function creates a device. Always set device 'type', 'private_ipv4_address', and 'public_ipv4_address' to the values shown below. You can tweak the paramter values for better results for your problem. Once set, the values remain same until changed using the 'update_device()' function. 

```python
# Create a basic local device
device = client.create_device(
    title="Device 1",
    description="A device for testing QUBO problems",
    type="aws",    # Always set to this default value
    iters=10000,     # Number of iterations
    runs=5,        # Number of runs per problem
    alpha=2.0,     # Alpha parameter
    beta=0.333,      # Beta parameter
    beta_decay=0.1,  # Beta decay rate
    noise_stdev=0.0,  # Standard deviation of noise
    runtime=0,     # Default value
    trials=1       # Number of trials
    'private_ipv4_address': 'http://172.31.12.198:5050'
    'public_ipv4_address': ''
)

print(f"Created device with ID: {device['id']}")
```

> Remember the device ID as it is needed for all the API calls to the device. Ideally you will be assigned with a preconfigured device ID from Quanfluence and won't need to create a device. 

### Retrieving Device Information

To get information about an existing device:

```python
# Replace with your actual device ID
device_id = YOUR_ID
device_info = client.get_device(device_id)
print(device_info)
```

> This will return the existing paramters values and device details for the device ID.

### Updating Device Parameters

You can update device parameters to optimize performance for specific problems. Once updated using this function, the parameter values remain the same until updated again.

```python
# Update device parameters
updated_device = client.update_device(device_id, {
    "alpha": 2.0,
    "beta": 1.5,
    "iters": 200,
    "runs": 10
})
print(f"Updated device: {updated_device}")
```
> Consider decreasing or increasing the number iterations to optimise between time taken and quality of results.

## Executing QUBOs

There are multiple ways to execute a QUBO on a Quanfluence device:

### Method 1: Direct QUBO Execution

The QUBO should always be in a python dictionary format with keys indicating spin number using consecutive integers starting from 0 as shown in the example below: 

```python
# Execute QUBO directly on the device
Q = {(0, 0): 1, (0, 1): -1, (1, 1): 2}
result = client.execute_device_qubo_input(device_id, QUBO)
print("Optimization result:", result)
```

### Method 2: Upload and Execute a QUBO File

In case of large problems, a QUBO file can be uploaded to the server and run multiple times without having to send the large problem to the server everytime.The file can be uploaded using the function shown below to obtain the file ID from the server. Use the file ID recieved to execute the file subsequently.

```python
# First, upload a QUBO file to the device
file_name = client.upload_device_qubo(device_id, "path/to/your/qubo_file.qubo")  # Remember the file_name
print("Uploaded filename", upload_result)

# Then execute the uploaded file

execution_result = client.execute_device_qubo_file(device_id, file_name)   # Pass the file_name obtained to execute it
print("Execution result:", execution_result)
```

> The QUBO file should be in serialised coordinate (COO) format and have a '.qubo' extension. Refer the [Example QUBO file](https://github.com/quanfluence/python-quanfluence-sdk/tree/main/example_qubo) for the format.

## Complete Workflow Example

Here's a complete example of using the Quanfluence SDK to solve a simple QUBO problem:

```python
import dimod
from quanfluence_sdk import QuanfluenceClient

# Initialize and authenticate
client = QuanfluenceClient()
client.signin("your_username", "your_password")

# Use an existing device
device_id = DEVICE_ID  # Replace with your actual device ID

# Define a QUBO problem
# This example minimizes: x₀ - x₀x₁ + 2x₁
Q = {(0, 0): 1, (0, 1): -1, (1, 1): 2}

# Optimize device parameters for this problem
device = client.update_device(device_id, {
    "alpha": 2.0,
    "beta": 0.333,
    "beta_decay": 0.1,
    "iters": 1000
})

# Execute the QUBO
result = client.execute_device_qubo_input(device_id, Q)
print("Optimization result:", result)

# Print the solution
if "solution" in result:
    print("Solution variables:", result["solution"])
    print("Solution energy:", result["energy"])
```

## Troubleshooting

### Limitations

The current supported BQM on the Ising machine has the following limitations:
 
1. The nodes in the BQM (QUBO or Ising models) should always be indexed from 0 to N-1 where N is the number of nodes.
2. Disconnected nodes with 0 self-weight are not allowed. 
3. The values in QUBO passed in dictionary format should always be 32 - bit floating point numbers.

### Common Issues

1. **Authentication Errors**: Make sure your username and password are correct.
   
2. **Missing Access Token**: If you see a "Access token is missing" error, ensure you're calling `signin()` before making other API calls.

3. **QUBO Format Issues**: Ensure your QUBO is formatted as a dictionary where keys are tuples of indices and values are floating-point numbers.


## Examples
- [Examples](https://github.com/quanfluence/python-quanfluence-sdk/tree/main/examples) - explore our examples docs and learn more about using sdk.


### Feedback

---

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

Use our [GitHub Issue Tracker][gh-issues] for reporting bugs or requesting features.
Visit the [Quanfluence Community][quanfluence-community] for getting help using Quanfluence Developer Kit for Python or just generally bond with your fellow Quanfluence developers.

<!-- Markdown links -->
