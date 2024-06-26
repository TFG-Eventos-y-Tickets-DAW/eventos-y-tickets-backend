from common.api_json_schemas import PUBLIC_EVENTS_SCHEMA
from common.constants.event_categories import EVENT_CATEGORIES_ID_BY_NAME
from common.constants.event_statuses import DELETED_ID, EVENT_STATUS_ID_BY_NAME
from common.constants.ticket_types import FREE, PAID
from common.event_utils import (
    convert_datetime_to_strings,
    format_and_prepare_event_details,
    get_ttl_for_the_next_minutes,
)
from common.http_utils import http_error_response, generic_server_error
from common.rds_conn import create_rds_connection
from common.schema import is_valid_schema_request

from uuid import uuid4
import humps
import json
import boto3
import os

connection = create_rds_connection()
connection.autocommit(True)

dynamodb_resource = boto3.resource("dynamodb")
pagination_table = dynamodb_resource.Table(
    os.environ.get("EVENT_PAGINATION_TABLE_NAME", "")
)


@is_valid_schema_request(PUBLIC_EVENTS_SCHEMA)
def lambda_handler(event, _):
    body = json.loads(event.get("body", {})) or {}
    filters = body.get("filters", {})

    paginationToken = body.get("paginationToken") or None
    try:
        if paginationToken:
            return find_events_by_pagination_token(paginationToken)
    except:
        return generic_server_error()

    items_per_page = body.get("itemsPerPage", 10)  # set to 10 items per page by default
    if not filters:
        all_events = fetch_all_events()
        all_events_formatted = list(map(format_events, all_events))

        if len(all_events) > items_per_page:
            return paginate_results(all_events_formatted, items_per_page)

        return {"events": all_events_formatted}

    all_events = fetch_all_events_with_filters(filters)
    all_events_formatted = list(map(format_events, all_events))

    if len(all_events) > items_per_page:
        return paginate_results(all_events_formatted, items_per_page)

    return {"events": all_events_formatted}


def find_events_by_pagination_token(pagination_token):
    response = pagination_table.get_item(
        Key={"tokenId": pagination_token},
        AttributesToGet=["payload", "pageNum", "nextTokenId"],
    )

    if "Item" not in response:
        return http_error_response(
            status_code=404,
            error_type="NOT_FOUND",
            error_detail="The pagination token has expired or it doesn't exists.",
        )

    events = json.loads(response.get("Item", {}).get("payload", "[]"))
    next_token = response.get("Item", {}).get("nextTokenId") or None
    page_num = response.get("Item", {}).get("pageNum")

    # Clean up token record
    pagination_table.delete_item(Key={"tokenId": pagination_token})

    return {"events": events, "nextPaginationToken": next_token, "pageNum": page_num}


def paginate_results(all_events, items_per_page):
    events_paginated = []
    for i in range(0, len(all_events), items_per_page):
        events_paginated.append(all_events[i : i + items_per_page])

    first_result_to_be_sent = events_paginated.pop(0)

    pagination_tokens = [
        str(uuid4()).replace("-", "") for _ in range(len(events_paginated))
    ]

    for i in range(len(pagination_tokens)):
        pagination_element = events_paginated[i]
        current_pagination_token = pagination_tokens[i]

        if len(pagination_tokens) > i + 1:
            next_token = pagination_tokens[i + 1]
        else:
            next_token = None

        pagination_table.put_item(
            Item={
                "tokenId": current_pagination_token,
                "payload": json.dumps(pagination_element),
                "pageNum": i + 2,
                "nextTokenId": next_token,
                "ttl": get_ttl_for_the_next_minutes(30),
            }
        )

    return {
        "events": first_result_to_be_sent,
        "paginationTokensPerPage": [
            {"pageNum": num + 2, "paginationToken": token}
            for (num, token) in enumerate(pagination_tokens)
        ],
        "pageNum": 1,
        "nextPaginationToken": pagination_tokens[0],
    }


def format_events(event_details: dict):
    new_event_details = event_details.copy()
    format_and_prepare_event_details(new_event_details)
    convert_datetime_to_strings(new_event_details)

    if (event_details.get("price") or 0) <= 0:
        new_event_details["type"] = FREE
    else:
        new_event_details["type"] = PAID

    return humps.camelize(new_event_details)


def fetch_all_events():
    with connection.cursor() as cur:
        select_sql = "SELECT e.id, e.owner_id, e.title, e.description, e.address, e.img_src, e.starts_at, e.ends_at, e.status_id, e.category_id, e.country, e.currency, e.created_at, t.price \
            FROM events AS e \
            LEFT JOIN tickets AS t \
            ON e.id = t.event_id \
            WHERE e.status_id != %s \
            AND e.ends_at > DATE_ADD(now(),interval 2 hour)"
        cur.execute(select_sql, (DELETED_ID,))

        result = cur.fetchall()

    return result


def fetch_all_events_with_filters(body):
    country = body.get("country")
    status = body.get("status")
    category = body.get("category")
    type = body.get("type")
    title = body.get("title")
    owner_id = body.get("ownerId")
    most_recents = body.get("mostRecents")
    most_popular = body.get("mostPopular")

    args_to_add = [DELETED_ID]
    select_sql = "SELECT e.id, e.owner_id, e.title, e.description, e.address, e.img_src, e.starts_at, e.ends_at, e.status_id, e.category_id, e.country, e.currency, e.created_at, t.price \
            FROM events AS e \
            LEFT JOIN tickets AS t \
            ON e.id = t.event_id"

    if most_popular:
        select_sql += " LEFT JOIN orders o ON e.id = o.event_id"

    where_sql = " WHERE e.status_id != %s AND"

    if most_popular:
        # only completed orders
        where_sql += " o.status_id = 2 AND"

    if country:
        if any([status, category, type, title, owner_id]):
            where_sql += " e.country = %s AND"
        else:
            where_sql += " e.country = %s"
        args_to_add.append(country)
    if status:
        if any([category, type, title, owner_id]):
            where_sql += " e.status_id = %s AND"
        else:
            where_sql += " e.status_id = %s"
        args_to_add.append(EVENT_STATUS_ID_BY_NAME[status])
    if category:
        if any([type, title, owner_id]):
            where_sql += " e.category_id = %s AND"
        else:
            where_sql += " e.category_id = %s"
        args_to_add.append(EVENT_CATEGORIES_ID_BY_NAME[category])
    if type:
        is_paid = type == PAID
        condition = (
            " t.price IS NOT NULL AND t.price > 0"
            if is_paid
            else " t.price <= 0 OR t.price IS NULL"
        )

        if any([title, owner_id]):
            where_sql += condition + " AND"
        else:
            where_sql += condition
    if title:
        if owner_id:
            where_sql += " e.title LIKE CONCAT('%%', %s, '%%') AND"
        else:
            where_sql += " e.title LIKE CONCAT('%%', %s, '%%')"
        args_to_add.append(title)
    if owner_id:
        where_sql += " e.owner_id = %s"
        args_to_add.append(owner_id)

    constructed_sql = (
        select_sql + where_sql + " AND e.ends_at > DATE_ADD(now(),interval 2 hour)"
    )

    # Mutually exclusive
    if most_popular:
        constructed_sql += " GROUP BY e.id, e.owner_id, e.title, e.description, e.address, e.img_src, e.starts_at, e.ends_at, e.status_id, e.category_id, e.country, e.currency, e.created_at, t.price"
        constructed_sql += " ORDER BY COUNT(o.id) DESC"
    elif most_recents:
        constructed_sql += " ORDER BY e.created_at DESC"

    print(f"Filter Query constructed: {constructed_sql}")

    with connection.cursor() as cur:
        cur.execute(constructed_sql, args_to_add)
        result = cur.fetchall()

    return result if result is not None else []
