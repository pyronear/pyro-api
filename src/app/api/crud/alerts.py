from typing import List, Dict, Mapping, Any
from sqlalchemy import Table

from app.api import crud


async def fetch_ongoing_alerts(
    table: Table, query_filters: Dict[str, Any], excluded_events_filter: Dict[str, Any]
) -> List[Mapping[str, Any]]:
    query = table.select()
    if isinstance(query_filters, dict):
        for query_filter_key, query_filter_value in query_filters.items():
            query = query.where(getattr(table.c, query_filter_key) == query_filter_value)

    #  TODO Should be performed using a sqlalchemy accessor. E.g: alert_event_end_ts is None
    all_closed_events = table.select().with_only_columns([table.c.event_id])
    if isinstance(excluded_events_filter, dict):
        for query_filter_key, query_filter_value in excluded_events_filter.items():
            all_closed_events = all_closed_events.where(getattr(table.c, query_filter_key) == query_filter_value)
    query = query.where(~getattr(table.c, "event_id").in_(all_closed_events))

    return await crud.base.database.fetch_all(query=query)
