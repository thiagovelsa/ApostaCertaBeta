"""
Script para baixar logos dos times usando o endpoint Opta
"""
import os
import requests
import time

# Configuração do endpoint Opta
OPTA_BASE_URL = "https://omo.akamai.opta.net/image.php"

def get_logo_url(team_id: str, size: int = 150) -> str:
    """Gera URL do logo do time no Opta"""
    return f"{OPTA_BASE_URL}?secure=true&h=omo.akamai.opta.net&sport=football&entity=team&description=badges&dimensions={size}&id={team_id}"

def download_logo(team_id: str, team_name: str, country: str, output_dir: str, size: int = 150) -> bool:
    """Baixa o logo de um time"""
    url = get_logo_url(team_id, size)

    # Criar diretório do país se não existir
    country_dir = os.path.join(output_dir, country)
    os.makedirs(country_dir, exist_ok=True)

    # Nome do arquivo: nome_do_time.png
    safe_name = team_name.replace(" ", "_").replace("/", "-").lower()
    filepath = os.path.join(country_dir, f"{safe_name}.png")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and len(response.content) > 100:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"OK {team_name} ({country})")
            return True
        else:
            print(f"ERRO {team_name} - Resposta invalida")
            return False
    except Exception as e:
        print(f"ERRO {team_name} - {e}")
        return False

# Times por liga
TEAMS = {
    "netherlands": {
        # Eredivisie
        "PSV": "24fvcruwqrqvqa3aonf8c3zuy",
        "Feyenoord": "20vymiy7bo8wkyxai3ew494fz",
        "Ajax": "d0zdg647gvgc95xdtk1vpbkys",
        "NEC": "8iawijq7s9s6d85mjz8wdslki",
        "Groningen": "cos9hxi16eitbcbthof7zrm4m",
        "AZ": "3kfktv64h7kg7zryax1wktr5r",
        "Twente": "4tic29sox7m39fy1ztgv0jsiq",
        "Utrecht": "ccpscwdcm65czscrun048ecn5",
        "Heerenveen": "4vd2t5schmvvufrfib7f2vjdf",
        "Sparta": "89w5c6pw7vn0dxypi61tt0g4k",
        "Fortuna": "3ebril33e08ddzob4bhq8awsr",
        "Excelsior": "dqk062lu0vm8epvytbm6r4mmf",
        "Go Ahead": "b79uipsy57y1jqpy07h4i5ovk",
        "Zwolle": "2uuh2bir8ktof0uxfo06lb4ox",
        "Telstar": "zjawy6qdzk3y69v5pa3zl2cb",
        "Volendam": "6g9qrm72224jrk6tkxxxi8a9n",
        "Heracles": "dac758ef858jbq7pcb3gfwite",
        "NAC": "59t7flioj4w4mpwnrwbm0m8ck",
        # Eerste Divisie
        "ADO": "e8hiwrw6ocxm5iht6sp7jiv19",
        "Cambuur": "ears40cp6opsgvhsy0dgyszpd",
        "De Graafschap": "xcevba75jfkrg4s6tl89zl3y",
        "Roda": "7rmv5ns2rj7bn4otpkur0mx0x",
        "PSV II": "2xlnfgrl6r18ftv38unwp7h4s",
        "Almere": "1fttb31hnskynpku8qd09yhm8",
        "Den Bosch": "eh54mfvjtrttgsg1wbjnvxcqz",
        "VVV": "cv5ftekuejf0ryxvd5h2my47r",
        "Willem II": "bk5ltsueqmeng29eovd8m2tml",
        "Waalwijk": "ed5nwjz5za3oyi20nxzgqivmx",
        "Emmen": "3t0vjqtxc8wpjzv82i3oi2ova",
        "Eindhoven": "dvmw7d6jb38qvv7e6ziwu0vyr",
        "Utrecht II": "ch82doz9w9t1sw9ae3a4ffh0j",
        "Dordrecht": "z9phg19papi9f5fd6qxzr836",
        "Helmond": "b94pf87be9ojdgnrs5mst80un",
        "MVV": "bqm1bnp1bh2apyudlz1o1whr3",
        "AZ II": "1wyg1tunyt7go9tnjea1hjqxb",
        "TOP Oss": "dnzj0iv5qtaemm9kthh9pos8q",
        "Vitesse": "6hsriqr3ybvyg94w2k19oal50",
        "Ajax II": "6lzy9iiqoysvtdsgx719fng9n",
    },
    "turkey": {
        "Galatasaray": "esa748l653sss1wurz5ps3228",
        "Fenerbahce": "8lroq0cbhdxj8124qtxwrhvmm",
        "Trabzonspor": "2yab38jdfl0gk2tei1mq40o06",
        "Goztepe": "cjbaf8s09qoa1n11r33gc560x",
        "Besiktas": "2ez9cvam9lp9jyhng3eh3znb4",
        "Samsunspor": "dpsnqu7pd2b0shfzjyn5j1znf",
        "Basaksehir": "47njg6cmlx5q3fvdsupd2n6qu",
        "Kocaelispor": "b703zecenioz21dnj3p63v3f7",
        "Gaziantep": "2agzb2h4ppg7lfz9hn7eg1rqo",
        "Alanyaspor": "84fpe0iynjdghwysyo5tizdkk",
        "Genclerbirligi": "embqktr41hfzczc8uav1scmcn",
        "Rizespor": "1lbrlj3uu8wi2h9j79snuoae4",
        "Konyaspor": "cw4lbdzlqqdvbkdkz00c9ye49",
        "Kasimpasa": "4idg23egrrvtrbgrg7p5x7bwf",
        "Antalyaspor": "9irsyv431fpuqhqtfq9iwxf2u",
        "Kayserispor": "c8ns6z3u8kxldv1zh1evu10rv",
        "Eyupspor": "bmgtxgipsznlb1j20zwjti3xh",
        "Fatih Karagumruk": "c3txoz57mu7w9y1jprvnv2flr",
    },
    "portugal": {
        "Porto": "66bsnl0zjb7l5akwo00h0y5me",
        "Sporting": "7catg5lpivcmpf4xhggh6d8rk",
        "Benfica": "9ldqu49smv1xg2va0n2cy28zl",
        "Gil Vicente": "bwt8yfk8rkcwiwyr0mopd7wqd",
        "Braga": "26t6lvlpql4w5wu1ih73qpy36",
        "Famalicao": "5c0sf1eaipcxvdw9o22of2jdp",
        "Moreirense": "4a3yqn3kt1l18oklr7zxo4f1s",
        "Vitoria SC": "8gvg1ranyf93hprfkwx3ofl2y",
        "Estoril": "22mo7qbsnyi8wtucpvhgvhw2q",
        "Estrela": "85nuf5511v5omdretfoh0c4k4",
        "Rio Ave": "cgvbluoerzbzcr7aaxge3wkcv",
        "Alverca": "2f40cprg8nv4stxq2o4yxpx54",
        "Nacional": "99xu9ofwhlbp0lg1j4eiplgrg",
        "Santa Clara": "cmbqc74mshg77ra7mywec2a6b",
        "Casa Pia": "ewsf6evtguu9j7k6js4tlgl89",
        "Arouca": "dich5v7sw466smbqap0d9rbyj",
        "Tondela": "a4hzxqvnwxe9frlt8fvxfmppa",
        "AVS": "di8rq9fo3z0bnsx08jljhnnys",
    },
    # IDs numéricos do Wikidata (P8737)
    "greece": {
        "Olympiacos": "202",
        "PAOK": "237",
        "Apollon Smyrnis": "3016",
        "Asteras Tripoli": "2599",
        "Atromitos": "2059",
        "Kallithea": "3129",
        "Kavalas": "3130",
        "Lamia": "11317",
        "Larissa": "2241",
        "Levadiakos": "2600",
        "Niki Volos": "3664",
        "Panachaiki": "2629",
        "Panetolikos": "4990",
        "Panionios": "2252",
        "Panserraikos": "2613",
        "PAS Giannina": "3133",
        "Volos": "14963",
    },
    "austria": {
        "Red Bull Salzburg": "857",
    }
}

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "logos")
    os.makedirs(output_dir, exist_ok=True)

    total = 0
    success = 0

    for country, teams in TEAMS.items():
        print(f"\n=== {country.upper()} ===")
        for name, team_id in teams.items():
            total += 1
            if download_logo(team_id, name, country, output_dir):
                success += 1
            time.sleep(0.2)  # Rate limiting

    print(f"\n{'='*40}")
    print(f"Total: {success}/{total} logos baixados com sucesso")

if __name__ == "__main__":
    main()
