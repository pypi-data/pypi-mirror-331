# fire-rpc
Turn fire command line into RPC server.


## Installation

```bash
pip install fire-rpc
``` 

## Example
`fire-rpc` provides a built-in echo server to demonstrate how to use it.

To start the echo server, run the following command:

```bash
# Note that the yes command is used to workaround the interactive mode of fire
yes | python -m fire_rpc /echo --port 8000
```

To call the echo server, run the following command:

```bash
url -X POST http://localhost:8000/echo -H "Content-Type: application/json" -d '{"args":["Hello World"]}'
```

The echo server will return the following response:

```json
{"result": {"args": ["Hello World"], "kwargs": {}}}
```

