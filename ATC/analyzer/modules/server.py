import socket
import json
import time

import numpy as np

TIMEOUT = 10
BUFSIZE = 16384


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
#     threshold: 0 < число < 1
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
    if "threshold" in json_data:
        val = json_data["threshold"]
        if isinstance(val, float):
            if not (0 <= val <= 1):
                return f"Invalid threshold value: {val}"
        else:
            try:
                parsed = float(val)
                if not (0 <= parsed <= 1):
                    return f"Invalid threshold value: {parsed}"
                json_data["threshold"] = parsed
            except ValueError:
                return f"Invalid threshold value: {val}"
    else:
        json_data["threshold"] = 0.0
    if "normalize" in json_data:
        supported = ["not", "some", "all"]
        if json_data["normalize"] not in supported:
            return f"Invalid normalization option: {json_data['normalize']}"
    return ""


def start_server(port: int, analyzer) -> None:
    server_address = ('localhost', port)
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(server_address)
        server_socket.listen(10)
        print("Server is running at port", port)
        print("Press ctrl+c to terminate")
    except OSError as e:
        print("Failed to launch server at port {}. OS error occurred: {}".format(port,
                                                                                 e.strerror))
        return
    connection, address = server_socket.accept()
    # 10-second timeout
    # connection.settimeout(TIMEOUT)
    print("Accepted connection from {}".format(address))
    while True:
        try:
            continue_flag = False
            # Receiving data
            msg = connection.recv(BUFSIZE)
            t = time.time()
            while not is_valid_json(msg.decode("utf-8")):
                data = connection.recv(BUFSIZE)
                if not data:
                    print("Connection closed, listening for new connection")
                    connection, address = server_socket.accept()
                    print("Accepted connection from {}".format(address))
                    continue_flag = True
                    break
                msg += data
                duration = time.time() - t
                if duration > TIMEOUT:
                    if msg:
                        print("Timeout occurred during receiving request. Interrupting")
                        continue_flag = True
                        break
            if continue_flag:
                continue
            msg = msg.decode()
            # print("Received")
            # Validating data
            json_data = json.loads(msg, encoding="utf-8")
            err_msg = validate_request_data(json_data, analyzer)
            if err_msg != "\0":
                # print("Error occurred:", err_msg)
                # print("Sending error message")
                connection.sendall(err_msg.encode("utf-8"))
                continue

            # Processing data
            if json_data["rubricator"] == "grnti":
                json_data["rubricator"] = "rgnti"
            text = " ".join([json_data.get("title", ""),
                             " ".join(json_data.get("keywords", [])),
                             json_data["body"]])
            params = {
                "language": json_data["language"],
                "format": "auto",
                "rubricator_id": json_data["rubricator"],
                "normalize": "not",
            }
            if "normalize" in json_data:
                params["normalize"] = json_data["normalize"]
            # print("Starting analyzer")
            result = analyzer.analyze(text, params)
            if not result:
                connection.sendall(bytes("Unknown error occurred\0", encoding="utf-8"))
                continue
            proba_series = result.getPredict().loc[0, "result"]
            if proba_series is None:
                connection.sendall(bytes("Classifier has rejected the text\0", encoding="utf-8"))
                continue
            proba_series = proba_series[proba_series > json_data["threshold"]]
            if params["normalize"] == "all":
                proba_series = proba_series / sum(proba_series)
            elif params["normalize"] == "some":
                if sum(proba_series) > 1.:
                    proba_series = proba_series / sum(proba_series)
            proba_dict = proba_series.to_dict()
            json_response_string = json.dumps(proba_dict)
            # print("Sending response")
            # print(json_response_string)
            connection.sendall(json_response_string.encode("utf-8"))
            # print("Cycle done")
        except ConnectionError:
            print("Connection aborted, listening for new connection")
            connection, address = server_socket.accept()
