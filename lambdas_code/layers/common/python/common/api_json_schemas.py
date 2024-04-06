SIGN_UP_SCHEMA = {
    "type": "object",
    "properties": {
        "firstName": {"type": "string", "minLength": 2},
        "lastName": {"type": "string", "minLength": 2},
        "password": {"type": "string", "minLength": 6},
        "email": {
            "type": "string",
            "format": "email",
            "pattern": "^\\S+@\\S+\\.\\S+$",
            "maxLength": 127,
            "minLength": 6,
        },
        "isAnonymous": {"type": "boolean"},
    },
    "required": ["firstName", "lastName", "password", "email", "isAnonymous"],
}

SIGN_IN_SCHEMA = {
    "type": "object",
    "properties": {
        "password": {"type": "string"},
        "email": {
            "type": "string",
            "format": "email",
            "pattern": "^\\S+@\\S+\\.\\S+$",
            "maxLength": 127,
            "minLength": 6,
        },
    },
    "required": ["password", "email"],
}

CREATE_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 6},
        "description": {"type": "string", "minLength": 4},
        "address": {"type": "string", "minLength": 4},
        "imgSrc": {"type": "string"},
        "startsAt": {"type": "string", "minLength": 6},
        "endsAt": {"type": "string", "minLength": 6},
        "category": {
            "type": "string",
            "enum": [
                "MUSIC",
                "FOOD & DRINK",
                "FASHION",
                "TECHNOLOGY",
                "CONFERENCE",
                "PARTY",
                "FILM",
                "KIDS & FAMILY",
                "OTHER",
            ],
        },
        "status": {"type": "string", "enum": ["DRAFT", "PUBLISHED"]},
        "country": {"type": "string", "minLength": 2, "maxLength": 2},
        "currency": {"type": "string", "minLength": 3, "maxLength": 3},
        "payoutInstrument": {
            "type": "object",
            "properties": {
                "iban": {"type": "string", "minLength": 24, "maxLength": 34},
                "swiftbic": {"type": "string", "minLength": 8, "maxLength": 11},
                "paypalEmail": {"type": "string", "minLength": 4, "maxLength": 64},
            },
        },
        "tickets": {
            "type": "object",
            "properties": {
                "quantity": {"type": "number", "minimum": 1},
                "price": {"type": "number", "minimum": 0},
            },
        },
        "preValidate": {"type": "boolean"},
    },
    "required": ["title", "description", "preValidate", "status"],
}

UPDATE_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 6},
        "description": {"type": "string", "minLength": 4},
        "address": {"type": "string", "minLength": 4},
        "imgSrc": {"type": "string"},
        "startsAt": {"type": "string", "minLength": 6},
        "endsAt": {"type": "string", "minLength": 6},
        "category": {
            "type": "string",
            "enum": [
                "MUSIC",
                "FOOD & DRINK",
                "FASHION",
                "TECHNOLOGY",
                "CONFERENCE",
                "PARTY",
                "FILM",
                "KIDS & FAMILY",
                "OTHER",
            ],
        },
        "status": {"type": "string", "enum": ["DRAFT", "PUBLISHED"]},
        "country": {"type": "string", "minLength": 2, "maxLength": 2},
        "currency": {"type": "string", "minLength": 3, "maxLength": 3},
        "payoutInstrument": {
            "type": "object",
            "properties": {
                "iban": {"type": "string", "minLength": 24, "maxLength": 34},
                "swiftbic": {"type": "string", "minLength": 8, "maxLength": 11},
                "paypalEmail": {"type": "string", "minLength": 4, "maxLength": 64},
            },
        },
        "tickets": {
            "type": "object",
            "properties": {
                "quantity": {"type": "number"},
                "price": {"type": "number"},
            },
        },
        "preValidate": {"type": "boolean"},
    },
    "required": ["preValidate", "status"],
}

PUBLIC_EVENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "filters": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "minLength": 2, "maxLength": 2},
                "status": {
                    "type": "string",
                    "enum": ["DRAFT", "PUBLISHED", "FINALIZED"],
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "MUSIC",
                        "FOOD & DRINK",
                        "FASHION",
                        "TECHNOLOGY",
                        "CONFERENCE",
                        "PARTY",
                        "FILM",
                        "KIDS & FAMILY",
                        "OTHER",
                    ],
                },
                "title": {"type": "string", "minLength": 4, "maxLength": 128},
                "type": {"type": "string", "enum": ["PAID", "FREE"]},
                "ownerId": {"type": "integer"},
            },
        },
        "itemsPerPage": {"type": "integer"},
        "paginationToken": {"type": "string", "minLength": 1, "maxLength": 128},
    },
    "required": ["filters"],
}


CREATE_ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "eventId": {"type": "integer", "minimum": 1},
        "ticketId": {"type": "integer", "minimum": 1},
        "quantity": {"type": "integer", "minimum": 1},
        "attendee": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 2},
                "email": {"type": "string", "minLength": 2},
            },
            "required": ["name", "email"],
        },
    },
    "required": ["eventId", "ticketId", "quantity", "attendee"],
}
