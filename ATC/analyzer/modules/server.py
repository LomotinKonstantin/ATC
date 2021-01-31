import socket
import json
from pathlib import Path
import select
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

def nonblocking_accept(socket, timeout: int) -> tuple or None:
    ready_to_read, _, _ = select.select([socket], [], [], timeout)
    for s in ready_to_read:
        if s is socket:
            return socket.accept()
    return None


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
    if json_data["language"] not in ["en", "ru", "auto"]:
        return "Invalid language: {}".format(json_data["language"])
    lang = json_data["language"]
    rubr_id = json_data["rubricator"]
    if not analyzer.classifier.is_model_exist(rubr_id=rubr_id, lang=lang):
        installed = analyzer.classifier.installed_rubricators()
        curr_rubr = json_data["rubricator"]
        return f"Invalid rubricator: {curr_rubr}. Available options: {', '.join(installed)}"
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
    stop_file = Path(__file__).parent / ".." / ".." / "stop_server.txt"
    if stop_file.exists():
        print("Cannot start server: signal file 'ATC/stop_server.txt' exists")
        exit()
    server_address = ('localhost', port)
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(server_address)
        server_socket.listen(10)
        print("Server is running at port", port)
        print("Press Ctrl+C or create the signal file 'ATC/stop_server.txt' to terminate")
    except OSError as e:
        print("Failed to launch server at port {}. OS error occurred: {}".format(port,
                                                                                 e.strerror))
        return
    connection = None
    while True:
        try:
            if stop_file.exists():
                print("Signal file 'ATC/stop_server.txt' exists. Terminating")
                exit()
            if connection is None:
                accept_ret = nonblocking_accept(server_socket, 1)
                if accept_ret is None:
                    continue
                connection, address = accept_ret
                ip_addr, port = address
                print(f"Accepted connection from {ip_addr}:{port}")
            continue_flag = False
            # Receiving data
            msg = connection.recv(BUFSIZE)
            t = time.time()
            while not is_valid_json(msg.decode("utf-8")):
                data = connection.recv(BUFSIZE)
                if not data:
                    print("Connection closed, listening for new connection")
                    continue_flag = True
                    connection = None
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
            # Validating data
            json_data = json.loads(msg, encoding="utf-8")
            err_msg = validate_request_data(json_data, analyzer)
            if err_msg != "\0":
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
            result = analyzer.analyze(text, params)
            rubr_id = result.getRubrId()
            lang = result.getLanguage()
            # Пост-фактум проверка. Криво, но тут уж как есть.
            if not analyzer.classifier.is_model_exist(rubr_id=rubr_id, lang=lang):
                connection.sendall(bytes(
                    f"Model for '{rubr_id}' rubricator and '{lang}' language is not found",
                    encoding="utf-8"
                ))
                continue
            if result is None:
                connection.sendall(bytes("Unknown error occurred\0", encoding="utf-8"))
                continue
            predict = result.getPredict()
            if predict is None:
                connection.sendall(bytes("Classifier has rejected the text\0", encoding="utf-8"))
                continue
            proba_series = predict.loc[0, "result"]
            proba_series = proba_series[proba_series > json_data["threshold"]]
            if params["normalize"] == "all":
                proba_series = proba_series / sum(proba_series)
            elif params["normalize"] == "some":
                if sum(proba_series) > 1.:
                    proba_series = proba_series / sum(proba_series)
            proba_dict = proba_series.to_dict()
            json_response_string = json.dumps(proba_dict)
            connection.sendall(json_response_string.encode("utf-8"))
        except ConnectionError:
            print("Connection aborted, listening for new connection")
            connection = None
            continue
        except KeyboardInterrupt:
            print("Terminating")
            exit()
