import socket
import json


def is_valid_json(string: str) -> bool:
    try:
        json.loads(string)
    except ValueError:
        return False
    return True


def null_terminate(err_gen_func):
    def nt_err(json_data: dict, analyzer):
        res = err_gen_func(json_data, analyzer)
        return res + "\0"
    return nt_err


# {
#     id: "идентификатор текста",
#     title: "заголовок текста",
#     body: "непосредственно текст",
#     keywords: ["список", "ключевых", "слов"],
#     rubricator: "одно из ipv, grnti или subj",
#     language: "одно из en, ru или auto",
# }
@null_terminate
def validate_request_data(json_data: dict, analyzer) -> str:
    """
    :param json_data: json dict with incoming data
    :param analyzer: tuned analyzer instance
    :return: empty string if data is valid, error message otherwise
    """
    # Validating required fields
    for k in ["body", "rubricator", "language"]:
        if k not in json_data:
            return "Missing '{}' field".format(k)
    if not analyzer.isTextValid(json_data["body"]):
        return "Invalid text"
    if json_data["rubricator"] not in ["ipv", "subj", "grnti"]:
        return "Invalid rubricator: {}".format(json_data["rubricator"])
    if json_data["language"] not in ["en", "ru", "auto"]:
        return "Invalid language: {}".format(json_data["language"])
    # Validating optional fields
    for k in ["id", "title"]:
        if k in json_data and not json_data[k]:
            return "Invalid value '{val}' of field '{f}'".format(val=json_data[k], f=k)
    if "keywords" in json_data:
        if not json_data["keywords"] or type(json_data["keywords"]) != list:
            return "Invalid keyword list"
    return ""


def start_server(port: int, analyzer) -> None:
    server_address = ('localhost', port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_address)
    server_socket.listen(10)
    print("Server is running at port", port)
    connection, address = server_socket.accept()
    print("Accepted connection from {}".format(address))
    while True:
        # Receiving data
        msg = ""
        data = connection.recv(1024)
        while not is_valid_json(msg):
            msg += data.decode("utf-8")
            data = connection.recv(1024)

        # Validating data
        json_data = json.loads(msg, encoding="utf-8")
        err_msg = validate_request_data(json_data, analyzer)
        if err_msg:
            connection.send(bytes(err_msg, encoding="utf-8"))
            continue

        # Processing data
        text = " ".join([json_data.get("title", ""),
                         " ".join(json_data.get("keywords", [])),
                         json_data["body"]])
        params = {
            "language": json_data["language"],
            "format": "auto",
            "rubricator_id": json_data["rubricator"],
        }
        result = analyzer.analyze(text, params)
        if not result:
            connection.send(bytes("Unknown error occurred\0", encoding="utf-8"))
            continue
        proba_series = result.loc[0, "result"]
        if proba_series is None:
            connection.send(bytes("Classifier has rejected the text\0", encoding="utf-8"))
            continue
        proba_dict = proba_series.to_dict()
        json_response_string = json.dumps(proba_dict)
        connection.send(bytes(json_response_string, encoding="utf-8"))
