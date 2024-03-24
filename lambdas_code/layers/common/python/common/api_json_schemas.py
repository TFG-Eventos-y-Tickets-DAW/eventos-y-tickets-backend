SIGN_UP_SCHEMA = {
    "type": "object",
    "properties": {
        "firstName": {"type": "string", "minLength": 2},
        "lastName": {"type": "string", "minLength": 2},
        "password": {"type": "string", "minLength": 6},
        "email": {"type": "string", "format": "email"},
        "isAnonymous": {"type": "boolean"},
    },
    "required": ["firstName", "lastName", "password", "email", "isAnonymous"],
}

SIGN_IN_SCHEMA = {
    "type": "object",
    "properties": {
        "password": {"type": "string"},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["password", "email"],
}
