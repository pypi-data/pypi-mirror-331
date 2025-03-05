import urllib.parse
from typing import Callable, Any, Optional, Dict, Iterator

import jubladb_api

def _iterate(list_func: Callable[[Dict[str, Any]], Any]):
    chunk = list_func({})
    while chunk is not None:
        yield from chunk.data
        if chunk.links is not None and chunk.links.next is not None:
            next_query = urllib.parse.parse_qs(urllib.parse.urlparse(chunk.links.next.actual_instance).query)
            keeping_query = {key: value[0] for key, value in next_query.items() if key in ["page[number]", "page[size]"]}

            chunk = list_func({"_additional_query_params": keeping_query})
        else:
            chunk = None

def iterate_event_kinds(api: jubladb_api.EventKindsApi, **kwargs) -> Iterator[jubladb_api.EventKindsResource]:
    return _iterate(lambda kwargs2: api.list_event_kinds(**kwargs, **kwargs2))

def iterate_events(api: jubladb_api.EventsApi, **kwargs) -> Iterator[jubladb_api.EventsResource]:
    return _iterate(lambda kwargs2: api.list_events(**kwargs, **kwargs2))

def iterate_groups(api: jubladb_api.GroupsApi, **kwargs) -> Iterator[jubladb_api.GroupsResource]:
    return _iterate(lambda kwargs2: api.list_groups(**kwargs, **kwargs2))

def iterate_invoices(api: jubladb_api.InvoicesApi, **kwargs) -> Iterator[jubladb_api.InvoicesResource]:
    return _iterate(lambda kwargs2: api.list_invoices(**kwargs, **kwargs2))

def iterate_people(api: jubladb_api.PeopleApi, **kwargs) -> Iterator[jubladb_api.PeopleResource]:
    return _iterate(lambda kwargs2: api.list_people(**kwargs, **kwargs2))

def iterate_roles(api: jubladb_api.RolesApi, **kwargs) -> Iterator[jubladb_api.RolesResource]:
    return _iterate(lambda kwargs2: api.list_roles(**kwargs, **kwargs2))