import json
from hnt_sap_financeiro.hnt_sap_gui import SapGui


def test_create():
    with open("./devdata/json/aprovado_taxa_FIN-50066.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    aprovado = payload['payloads'][0]['aprovado']
    result = SapGui().run_FB02(aprovado)

    assert result['error'] is None
