# Neurion Ganglion - Ion Framework

## Overview
Neurion Ganglion provides a framework for defining, deploying, and managing Ions – decentralized computational units that operate within the Neurion ecosystem. This repository offers a streamlined way to create and register Ions, either as self-hosted services or pre-existing services ready for registration.

## Features
- Define input and output schemas using Pydantic.
- Register Ions with Neurion automatically or manually.
- Health-check endpoints for ensuring service availability.
- Auto-recovery mechanism for self-hosted Ions.
- Easy-to-use decorators for defining execution logic.
- Integrated Ganglion Server for managing pathways and processing Ion calls.
- Support for **localnet**, **alphanet**, **betanet**, and **mainnet** environments.

## Installation

```sh
pip install neurion-ganglion
```

---
## Environment Variables
Neurion Ganglion relies on several environment variables for configuration:

| Variable                  | Description                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `NEURION_PRIVATE_KEY`     | The private key used for authentication and transaction signing.                                                               |
| `NEURION_MNEMONIC`        | Mnemonic phrase for wallet recovery and authentication.                                                                        |
| `NEURION_NETWORK`         | Network selection: `localnet`, `alphanet`, `betanet`, or `mainnet`.                                                            |
| `POSTGRES_DATABASE_URL`   | PostgreSQL database URL for storing Ion and Pathway usage records.                                                             |
| `CLICKHOUSE_DATABASE_URL` | ClickHouse database URL for storing Ion and Pathway usage records. Due to its performance, it is the default embedded solution |
| `ENABLE_CALLS_COUNT`      | Boolean flag (`true/false`) to enable or disable call metering.                                                                |
| `FREE_ION_CALLS`          | Number of free calls allowed for an Ion before requiring payment.                                                              |

You can configure these by setting them in your `.env` file or export them as environment variables.

---
## Network Configuration

Neurion supports multiple networks. To configure the appropriate network:

```python
import os
from functools import lru_cache
from neurionpy.synapse.config import NetworkConfig

@lru_cache()
def get_network() -> NetworkConfig:
    network = os.getenv("NEURION_NETWORK", "alphanet")
    if network.lower() == "mainnet":
        return NetworkConfig.neurion_mainnet()
    elif network.lower() == "alphanet":
        return NetworkConfig.neurion_alpha_testnet()
    elif network.lower() == "betanet":
        return NetworkConfig.neurion_beta_testnet()
    elif network.lower() == "localnet":
        return NetworkConfig.neurion_localnet()
    return NetworkConfig.neurion_alpha_testnet()
```

---
## Authentication Flow
To ensure security, every request to the Ganglion server must be authenticated using the following headers:

- `X-Neurion-Timestamp`: The UNIX timestamp of the request.
- `X-Neurion-Sender`: The sender's wallet address.
- `X-Neurion-Signature`: The signature of the sender over the timestamp.

### How Authentication Works:
1. The **sender signs** the current timestamp using their private key.
2. The **request is sent** with the signed timestamp and wallet address in headers.
3. The **server verifies**:
   - The timestamp is within the allowed expiry window.
   - The signature is valid using the sender's public key.
   - The sender has enough balance if `ENABLE_CALLS_COUNT` is enabled.
4. If validation passes, the request is processed.

### Example Signature Verification in Middleware:
```python
from neurionpy.crypto.keypairs import PublicKey

def verify_signature(timestamp: str, sender: str, signature: str) -> bool:
    try:
        recovered_pubkey = PublicKey.from_signature_hex(timestamp, signature)
        return recovered_pubkey.to_address() == sender
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False
```

---
## Creating an Ion
You can create an Ion in two different ways:

### 1. Self-Hosting Ion (Auto-Registering)
```python
from pydantic import BaseModel
from neurion_ganglion.ion.ion import Ion, ion_handler
from neurion_ganglion.custom_types.capacity import Capacity

description = "My Ion Server"
stake = 20000000
fee_per_thousand_calls = 1
capacities = [Capacity.SCRAPER, Capacity.AI_AGENT]

# Define Input/Output Schemas
class MyInputSchema(BaseModel):
    task_id: str
    parameters: int

class MyOutputSchema(BaseModel):
    message: str
    result: float

@ion_handler(MyInputSchema, MyOutputSchema)
def my_ion_handler(data: MyInputSchema) -> MyOutputSchema:
    return MyOutputSchema(message="Success", result=12)

if __name__ == "__main__":
    Ion.create_self_hosting_ion(description, stake, fee_per_thousand_calls, capacities, my_ion_handler).start()
```

### 2. Pure Ion Server & Manual Registration
#### **Step 1: Start the Pure Ion Server**
```python
Ion.start_pure_ion_server(my_ion_handler)
```
#### **Step 2: Register the Running Ion Server**
```python
endpoints = ["http://<public-ip>:8000"]
Ion.create_server_ready_ion(description, stake, fee_per_thousand_calls, capacities, MyInputSchema, MyOutputSchema, endpoints).register_ion()
```

---
## Using Pathways
A **Pathway** defines a structured flow between multiple Ions.

```python
from neurion_ganglion.ion.pathway import Pathway

pathway = Pathway.of(1)
response = pathway.call({"task_id": "1234", "parameters": 100})
print(response)
```

---
## Ganglion Server
The **Ganglion Server** routes requests to the appropriate **Ion** or **Pathway**.

```python
from neurion_ganglion.server.server import GanglionServer
GanglionServer.start()
```

---
## Health Check
All Ions expose a `/health` endpoint for availability checking.
```sh
curl http://localhost:8000/health
```

---
## License
This project is licensed under the MIT License.

