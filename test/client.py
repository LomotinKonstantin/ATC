import socket
import json
from time import time


test_file = "plain_ru.txt"
BUFSIZE = 16384


def is_valid_json(string: str) -> bool:
    try:
        json.loads(string)
    except ValueError:
        return False
    return True


def send(sock, msg: str):
    sock.sendall(msg.encode("utf-8"))
    

def receive(sock) -> str:
    response = b""
    while b"\0" not in response and not is_valid_json(response.decode("utf-8")):
        response += sock.recv(BUFSIZE)
    return response.decode("utf-8")


def to_json(dict_data: dict) -> str:
    return json.dumps(dict_data, ensure_ascii=False)


if __name__ == '__main__':
    # with open("in/{}".format(test_file), encoding="cp1251") as fp:
    #     text = fp.read()
    # text = "Концепция подчеркивает закон исключённого третьего. " \
    #        "Идеи гедонизма занимают центральное место в утилитаризме " \
    #        "Милля и Бентама, однако здравый смысл амбивалентно оспособляет " \
    #        "из ряда вон выходящий бабувизм, при этом буквы А, В, I, О символизируют " \
    #        "соответственно общеутвердительное, общеотрицательное, частноутвердительное " \
    #        "и частноотрицательное суждения. Отношение к современности оспособляет " \
    #        "напряженный даосизм. Гегельянство поразительно. Созерцание, по определению, " \
    #        "нетривиально. Гений, по определению, реально транспонирует данный здравый смысл.\n " \
    #        "Интересно отметить, что даосизм прост. Дуализм категорически создает гений. " \
    #        "Гегельянство заполняет непредвиденный смысл жизни. Заблуждение, как принято считать, " \
    #        "подрывает закон внешнего мира. Освобождение трогательно наивно. Ощущение мира " \
    #        "непредсказуемо.\n " \
    #        "Импликация индуктивно подчеркивает примитивный смысл жизни, открывая новые " \
    #        "горизонты. Отношение к современности философски принимает во внимание даосизм. " \
    #        "Представляется логичным, что современная критика порождена временем."
    text = """Mathematically, the problem is reduced to an eigenvalue problem for the Laplace operator in the whole 
    space with the Coulomb potential. To solve this problem numerically, a new mathematical apparatus developed by 
    the author is used. By inverting the unit sphere, the problem is reduced to the problem of eigenvalues in a 
    single ball punctured in the center. The boundary condition at infinity (zero) goes to the center of the ball. """
    lang = "auto"
    rubr_id = "custom"
    keywords = ["ооооо", "моя", "оборона"]
    title = "Зэ тайтл"
    text_id = "12345"

    def full_data() -> dict:
        data = {
            "id": text_id,
            "title": title,
            "body": text,
            "keywords": keywords,
            "rubricator": rubr_id,
            "language": lang,
            "threshold": "0.05",
            "normalize": "all",
        }
        return data

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 42424))
    print("Connected")
    dict_data = {
        "body": text,
        "rubricator": rubr_id,
        "language": lang
    }
    print("Testing connection")
    print("Testing correct behavior")
    print("Only required fields")
    json_str = to_json(dict_data)
    send(sock, json_str)
    response = receive(sock)
    print(response, "\n")
    print("Including optional fields")
    dict_data = full_data()
    send(sock, to_json(dict_data))
    response = receive(sock)
    dict_data = full_data()
    dict_data["normalize"] = "some"
    send(sock, to_json(dict_data))
    receive(sock)
    dict_data = full_data()
    dict_data["normalize"] = "not"
    send(sock, to_json(dict_data))
    receive(sock)
    print(response, "\n")
    print("Проверка ошибок")
    print("Пустой текст")
    dict_data["body"] = ""
    send(sock, to_json(dict_data))
    response = receive(sock)
    print(response, "\n")
    print("Ошибка в необязательных полях")
    dict_data = full_data()
    dict_data["keywords"] = 5
    send(sock, to_json(dict_data))
    response = receive(sock)
    print(response, "\n")
    dict_data = full_data()
    dict_data["normalize"] = 5
    send(sock, to_json(dict_data))
    response = receive(sock)
    print(response, "\n")
    #
    print("Языки")
    for i in ["fr", "en", "ru", "auto"]:
        print(i)
        dict_data = full_data()
        dict_data["language"] = i
        send(sock, to_json(dict_data))
        response = receive(sock)
        print(response, "\n")
    response = ""
    t = time()
    n = 100
    data = to_json(dict_data)
    for i in range(n):
        dict_data = full_data()
        send(sock, data)
        response = receive(sock)
    print("Обработано {} запросов за {}с".format(n, time() - t))
    print(response)
    
    sock.close()


