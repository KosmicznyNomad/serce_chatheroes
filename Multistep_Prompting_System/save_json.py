import json

data = {
    "dzialy": [
        {
            "nazwa": "Składnia zdań",
            "opis": "Opis dla Składnia zdań",
            "tematy": [
                {
                    "nazwa": "Składnia zdań",
                    "wymagania": [
                        "Znajomość klasyfikacji zdań ze względu na cel wypowiedzi",
                        "Opanowanie struktury zdań oznajmujących, pytających, rozkazujących i wykrzyknikowych"
                    ],
                    "niewymagane": [
                        "Znajomość zdań złożonych i ich typów"
                    ]
                }
            ]
        },
        {
            "nazwa": "Fleksja rzeczownika",
            "opis": "Opis dla Fleksja rzeczownika",
            "tematy": [
                {
                    "nazwa": "Fleksja rzeczownika",
                    "wymagania": [
                        "Rozumienie kategorii liczby w odniesieniu do rzeczowników",
                        "Umiejętność rozróżniania i stosowania form liczby pojedynczej i mnogiej",
                        "Znajomość pojęć singularia tantum i pluralia tantum"
                    ],
                    "niewymagane": [
                        "Pełna odmiana rzeczowników przez przypadki"
                    ]
                }
            ]
        },
        {
            "nazwa": "Ortografia - pisownia 'ó' i 'u'",
            "opis": "Opis dla Ortografia - pisownia 'ó' i 'u'",
            "tematy": [
                {
                    "nazwa": "Ortografia - pisownia 'ó' i 'u'",
                    "wymagania": [
                        "Znajomość zasady wymiany 'ó' na 'o'",
                        "Rozumienie pojęcia 'ó' niewymiennego",
                        "Umiejętność identyfikacji wyjątków od reguły"
                    ],
                    "niewymagane": [
                        "Pełna znajomość wszystkich wyrazów z 'ó' niewymiennym"
                    ]
                }
            ]
        },
        {
            "nazwa": "Części mowy",
            "opis": "Opis dla Części mowy",
            "tematy": [
                {
                    "nazwa": "Części mowy",
                    "wymagania": [
                        "Rozpoznawanie podstawowych części mowy: rzeczowników, przymiotników, czasowników i przysłówków",
                        "Umiejętność określania podstawowych form fleksyjnych wymienionych części mowy",
                        "Rozumienie podziału na odmienne i nieodmienne części mowy"
                    ],
                    "niewymagane": [
                        "Znajomość wszystkich kategorii gramatycznych poszczególnych części mowy"
                    ]
                }
            ]
        },
        {
            "nazwa": "Ortografia - pisownia 'rz'",
            "opis": "Opis dla Ortografia - pisownia 'rz'",
            "tematy": [
                {
                    "nazwa": "Ortografia - pisownia 'rz'",
                    "wymagania": [
                        "Znajomość zasady wymienności 'rz' na 'r'",
                        "Opanowanie reguły pisowni 'rz' po spółgłoskach"
                    ],
                    "niewymagane": [
                        "Pełna znajomość wszystkich wyjątków od reguły"
                    ]
                }
            ]
        },
        {
            "nazwa": "Zasady ortograficzne i interpunkcyjne",
            "opis": "Opis dla Zasady ortograficzne i interpunkcyjne",
            "tematy": [
                {
                    "nazwa": "Zasady ortograficzne i interpunkcyjne",
                    "wymagania": [
                        "Znajomość podstawowych zasad pisowni wielką literą",
                        "Opanowanie pisowni połączeń literowych reprezentujących samogłoski nosowe",
                        "Umiejętność stosowania podstawowych znaków interpunkcyjnych",
                        "Znajomość zasady pisowni 'nie' z różnymi częściami mowy"
                    ],
                    "niewymagane": []
                }
            ]
        }
    ]
}

file_path = 'c:\\Users\\ben10\\Downloads\\serce\\serce_chatheroes\\Multistep_Prompting_System\\knowledge_base.json'

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Dane zostały zapisane do pliku {file_path}")
