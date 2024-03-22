import urllib.request


def lambda_handler(event, context):
    print("Received event: ", event)
    req = urllib.request.Request("https://jsonplaceholder.typicode.com/todos/1")
    response = urllib.request.urlopen(req)
    return response.read().decode("utf8")
