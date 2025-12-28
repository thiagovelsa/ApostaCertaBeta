"""
Script para baixar logos via TheSportsDB API
Ligas: Escócia, Áustria, Suíça
"""
import os
import requests
import time

# Diretório de saída
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "logos")

# Times e URLs de badges do TheSportsDB
TEAMS = {
    "scotland": {
        "Aberdeen": "https://r2.thesportsdb.com/images/media/team/badge/xuvwys1447597299.png",
        "Celtic": "https://www.thesportsdb.com/images/media/team/badge/3uv1641758780002.png",
        "Dundee": "https://r2.thesportsdb.com/images/media/team/badge/tlei9x1750743461.png",
        "Dundee United": "https://r2.thesportsdb.com/images/media/team/badge/orfh821655722356.png",
        "Falkirk": "https://r2.thesportsdb.com/images/media/team/badge/w37ucy1685023169.png",
        "Heart of Midlothian": "https://r2.thesportsdb.com/images/media/team/badge/twqvyt1447597939.png",
        "Hibernian": "https://r2.thesportsdb.com/images/media/team/badge/qjys3z1684928969.png",
        "Kilmarnock": "https://r2.thesportsdb.com/images/media/team/badge/xssqtu1447596951.png",
        "Livingston": "https://r2.thesportsdb.com/images/media/team/badge/1o38ll1749203191.png",
        "Motherwell": "https://r2.thesportsdb.com/images/media/team/badge/vsysqx1447598301.png",
        "Rangers": "https://r2.thesportsdb.com/images/media/team/badge/ti24j61614290048.png",
        "St Mirren": "https://r2.thesportsdb.com/images/media/team/badge/xvtuvv1447604452.png",
    },
    "austria": {
        "Austria Vienna": "https://r2.thesportsdb.com/images/media/team/badge/rn329l1703004303.png",
        "Blau-Weiss Linz": "https://r2.thesportsdb.com/images/media/team/badge/7qazvh1583516559.png",
        "Grazer AK": "https://r2.thesportsdb.com/images/media/team/badge/43rocv1750352978.png",
        "LASK": "https://r2.thesportsdb.com/images/media/team/badge/oox26l1683556395.png",
        "Rapid Vienna": "https://r2.thesportsdb.com/images/media/team/badge/wxvdn91686619560.png",
        "Red Bull Salzburg": "https://r2.thesportsdb.com/images/media/team/badge/xy1m6m1576416143.png",
        "SCR Altach": "https://r2.thesportsdb.com/images/media/team/badge/2hit6x1750352012.png",
        "Sturm Graz": "https://r2.thesportsdb.com/images/media/team/badge/ppg0j71578585847.png",
        "SV Ried": "https://r2.thesportsdb.com/images/media/team/badge/c1bxyq1583516636.png",
        "TSV Hartberg": "https://r2.thesportsdb.com/images/media/team/badge/72c0xg1578833261.png",
        "Wolfsberger AC": "https://r2.thesportsdb.com/images/media/team/badge/xcwuqt1568668946.png",
        "WSG Tirol": "https://r2.thesportsdb.com/images/media/team/badge/9dmxk01685123856.png",
    },
    "switzerland": {
        "Basel": "https://r2.thesportsdb.com/images/media/team/badge/xppxwr1473791183.png",
        "Grasshoppers": "https://r2.thesportsdb.com/images/media/team/badge/hjwlxi1486332675.png",
        "Lausanne-Sport": "https://r2.thesportsdb.com/images/media/team/badge/za539g1580927491.png",
        "Lugano": "https://r2.thesportsdb.com/images/media/team/badge/2kh2if1567615581.png",
        "Luzern": "https://r2.thesportsdb.com/images/media/team/badge/rsupty1473587847.png",
        "Servette": "https://r2.thesportsdb.com/images/media/team/badge/440wv71692206330.png",
        "Sion": "https://r2.thesportsdb.com/images/media/team/badge/gzpfmv1689085319.png",
        "St Gallen": "https://r2.thesportsdb.com/images/media/team/badge/tyvyvs1422644512.png",
        "Thun": "https://r2.thesportsdb.com/images/media/team/badge/sovjgl1699462359.png",
        "Winterthur": "https://r2.thesportsdb.com/images/media/team/badge/bimd8z1580926541.png",
        "Young Boys": "https://r2.thesportsdb.com/images/media/team/badge/9mxdoo1534784569.png",
        "Zurich": "https://r2.thesportsdb.com/images/media/team/badge/ouekvr1657983777.png",
    },
}


def download_logo(team_name: str, url: str, country: str) -> bool:
    """Baixa o logo de um time"""
    country_dir = os.path.join(OUTPUT_DIR, country)
    os.makedirs(country_dir, exist_ok=True)

    # Nome do arquivo: nome_do_time.png
    safe_name = team_name.replace(" ", "_").replace("/", "-").replace(".", "").lower()
    filepath = os.path.join(country_dir, f"{safe_name}.png")

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200 and len(response.content) > 500:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"OK {team_name} ({country}) - {len(response.content)} bytes")
            return True
        else:
            print(f"ERRO {team_name} - Status {response.status_code}, Size {len(response.content)}")
            return False
    except Exception as e:
        print(f"ERRO {team_name} - {e}")
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = 0
    success = 0

    for country, teams in TEAMS.items():
        print(f"\n=== {country.upper()} ===")
        for name, url in teams.items():
            total += 1
            if download_logo(name, url, country):
                success += 1
            time.sleep(0.3)  # Rate limiting

    print(f"\n{'='*40}")
    print(f"Total: {success}/{total} logos baixados com sucesso")


if __name__ == "__main__":
    main()
