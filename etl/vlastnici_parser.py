import os
import json
from bs4 import BeautifulSoup # module: beautifulsoup4-4.13.4

VLASTNICI_HTML_FILE = "vlastnici-2025-09-11.html"
OUTPUT_JSON_FILE = 'vlastnici.json'

if __name__ == "__main__":
    script_root = os.path.dirname(os.path.realpath(__file__))
    with open(script_root + "/" + VLASTNICI_HTML_FILE, 'r', encoding='UTF-8') as f:
        html_data = f.read()
        soup = BeautifulSoup(html_data, 'html.parser')

    vlastnici = []
    jmenovatel = 0
    for tr in soup.select("tr"):
        if tr.find("td", class_="partnerSJM"):
            continue
        katastr_vlastnik = tr
        katastr_pomer = None
        katastr_jednotky = []
        weight = 0
        trvaly_pobyt = False
        owner_count = 1

        td_right = tr.find("td", class_="right")
        if td_right:
            katastr_pomer = td_right.text.strip().split("/")
            weight = int(katastr_pomer[0])/int(katastr_pomer[1])
            jmenovatel = max(jmenovatel, int(katastr_pomer[1]))

        vlastnik_td = tr.find("td")
        if vlastnik_td:
            katastr_vlastnik = vlastnik_td.text.strip().split(",")[0].split("Jednotka: ")[0]
            if "Zlochova" in vlastnik_td.text:
                trvaly_pobyt = True
            if katastr_vlastnik.startswith("SJ ") or katastr_vlastnik.startswith("MCP ") \
                and " a " in katastr_vlastnik:
                owner_count = 2


        for jednotka in tr.select("A"):
            katastr_jednotky.append(jednotka.text.strip())

        # if len([j for j in jednotky if j not in ('2230/100', '2230/200')])==0:
        #     print(tr)
        #     print (vlastnik, pomer, jednotky)
        primarni_jednotka = katastr_jednotky[-1] if katastr_jednotky else "n/a"
        vlastnici.append({
            "owner": katastr_vlastnik,
            "permanent_residence": trvaly_pobyt,
            "owner_count": owner_count,
            "weight": weight,
            "weight_per_owner": weight/owner_count,
            "katastr_pomer": katastr_pomer,
            "katastr_jednotky": katastr_jednotky,
            "primarni_jednotka": primarni_jednotka,
            "door_label": primarni_jednotka.replace("2230/4","14").replace("2230/1","D1").replace("2230/2","D2"),
        })

        for vlastnik in vlastnici:
            if vlastnik["katastr_pomer"]:
                vlastnik["part"] = jmenovatel / int(vlastnik["katastr_pomer"][1]) * int(vlastnik["katastr_pomer"][0])
                vlastnik["part_per_owner"] = vlastnik["part"]/vlastnik["owner_count"]

    for apartment in vlastnici:
        print (f"\t'{apartment["owner"]}',")
    print (f"Počet záznamů: {len(vlastnici)}")
    print (f"Počet jednatelů: {sum([apartment["owner_count"] for apartment in vlastnici])}")
    print (f"Kontrolní součet vah: {sum([vlastnik["weight"] for vlastnik in vlastnici])}")
    print (f"Kontrolní součet part: {int(sum([vlastnik["part"] for vlastnik in vlastnici if "part" in vlastnik]))} / {jmenovatel}")

    with open(script_root + '/' + OUTPUT_JSON_FILE, 'w', encoding='UTF-8') as file_pointer:
        json.dump(vlastnici, file_pointer, default=str, sort_keys=True, indent=2, ensure_ascii=False)
        file_pointer.write('\n')


