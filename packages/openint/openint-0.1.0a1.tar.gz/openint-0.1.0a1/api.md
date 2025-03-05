# Openint

Types:

```python
from openint.types import (
    CheckConnectionResponse,
    GetConnectionResponse,
    ListConnectionConfigsResponse,
    ListConnectionsResponse,
    ListEventsResponse,
)
```

Methods:

- <code title="post /connection/{id}/check">client.<a href="./src/openint/_client.py">check_connection</a>(id) -> <a href="./src/openint/types/check_connection_response.py">CheckConnectionResponse</a></code>
- <code title="get /connection">client.<a href="./src/openint/_client.py">get_connection</a>(\*\*<a href="src/openint/types/client_get_connection_params.py">params</a>) -> <a href="./src/openint/types/get_connection_response.py">GetConnectionResponse</a></code>
- <code title="get /connector-config">client.<a href="./src/openint/_client.py">list_connection_configs</a>(\*\*<a href="src/openint/types/client_list_connection_configs_params.py">params</a>) -> <a href="./src/openint/types/list_connection_configs_response.py">ListConnectionConfigsResponse</a></code>
- <code title="get /connection/{id}">client.<a href="./src/openint/_client.py">list_connections</a>(id, \*\*<a href="src/openint/types/client_list_connections_params.py">params</a>) -> <a href="./src/openint/types/list_connections_response.py">ListConnectionsResponse</a></code>
- <code title="get /event">client.<a href="./src/openint/_client.py">list_events</a>(\*\*<a href="src/openint/types/client_list_events_params.py">params</a>) -> <a href="./src/openint/types/list_events_response.py">ListEventsResponse</a></code>
