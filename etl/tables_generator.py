import os
import json
import yaml

LABLES_FILE = "labels.yaml"
VLASTNICI_JSON_FILE = 'vlastnici.json'
OUTPUT_JSON_FILE = '../web_lists.json'

bells_mailboxes = {
    "bell": {},
    "mailbox": {},
    "apartment": {},
}

blacklist_names = (
    "SJ Balík Tomáš MUDr. a Balíková Vladimíra MUDr.",
    "SJ Dubnický Marek a Dubnická Žaneta",
    "SJ Grubyy Mykhaylo a Gruba Nadiya",
    "SJ Kovář Samuel Mgr. a Kovářová Natalija Ivanivna",
    "SJ Leskin Andrei a Leskina Olga",
    "SJ Linh Lu Ngoc a Huong Nguyen Thi",
    "SJ Nedoma Richard Ing. a Nedomová Taťana",
    "SJ Paleček Petr Ing. a Palečková Zuzana",
    "SJ Shelest Andrii a Shelest Inessa",
    "SJ Suk Michael a Suková Michaela Mgr.",
    "SJ Toman Jan JUDr. a Tomanová Alena JUDr.",
    "SJ Uzan Amos-Hay-Shalom  MBA a Uzan Petra",
    "SJ Vrtílek Jan a Vrtílková Michaela",
    "SJ Žilinský Petr a Žilinská Zuzana Ing.",
    "Šlapák František, Petra",
    'Beneš Jan Ing.',
    'Ovečková Nikoleta Ing.',
    'Najmanová Darina',
    'Smejkalová Eva',
    'MCP Lavian Shahar a Lavian Gilat Alegria'
)

if __name__ == "__main__":
    script_root = os.path.dirname(os.path.realpath(__file__))
    with open(script_root +'/' + LABLES_FILE, 'r', encoding='utf-8') as file:
        labels = yaml.safe_load(file)

    for apartman in labels:
        if apartman not in bells_mailboxes["apartment"]:
            bells_mailboxes["apartment"][apartman] = set()
        for key in labels[apartman]:
            if labels[apartman][key] is None:
                continue
            if key == "bell":
                for name in labels[apartman]["bell"]:
                    bells_mailboxes["bell"][name] = apartman
                    if name not in blacklist_names:
                        bells_mailboxes["apartment"][apartman].add(name)
            if key == "mailbox":
                for name in labels[apartman]["mailbox"]:
                    if name not in blacklist_names:
                        bells_mailboxes["mailbox"][name] = apartman
                        bells_mailboxes["apartment"][apartman].add(name)

    with open(script_root+'/'+VLASTNICI_JSON_FILE, 'r', encoding='utf-8') as recent_file:
        vlastnici = json.load(recent_file)
    for vlastnik in vlastnici:
        if "owner" in vlastnik \
            and "door_label" in vlastnik \
            and vlastnik["door_label"] in bells_mailboxes["apartment"] \
            and vlastnik["owner"] not in blacklist_names:
            bells_mailboxes["apartment"][vlastnik["door_label"]].add(vlastnik["owner"])
            bells_mailboxes["mailbox"][vlastnik["owner"]] = vlastnik["door_label"]
        # print(vlastnik)

    # remove shorter
    guide_keys = bells_mailboxes["mailbox"].keys()
    to_remove = ()
    for k in bells_mailboxes["mailbox"].keys():
        for mailbox in bells_mailboxes["mailbox"]:
            if k != mailbox and k in mailbox and mailbox.startswith(k):
                to_remove += ({k:bells_mailboxes["mailbox"][k]}),
    for remove in to_remove:
        for k, v in remove.items():
            del bells_mailboxes["mailbox"][k]
            bells_mailboxes["apartment"][v].remove(k)

    # join apartment names
    for k, s in bells_mailboxes["apartment"].items():
        bells_mailboxes["apartment"][k] = "; ".join(s)

    # print (json.dumps(bells_mailboxes, default=str, sort_keys=True, indent=2, ensure_ascii=False))
    with open(script_root + '/' + OUTPUT_JSON_FILE, 'w', encoding='UTF-8') as file_pointer:
        json.dump(bells_mailboxes, file_pointer, default=str, sort_keys=True, indent=2, ensure_ascii=False)
        file_pointer.write('\n')
    print (f"apartment: {len(bells_mailboxes["apartment"])}")
    print (f"bell: {len(bells_mailboxes["bell"])}")
    print (f"mailbox: {len(bells_mailboxes["mailbox"])}")