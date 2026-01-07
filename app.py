# app.py

from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

# --- Konstanten / einfache Datenhaltung ---
TOOLS = {
    'chatgpt': 'ChatGPT (GPT-4)',
    'asknature': 'AskNature Chat',
    'bidara': 'BIDARA (Bio-inspired Design Assistant for Researchers and Applications)'
}

CRITERIA = [
    "fachliche_relevanz", "uebertragbarkeit", "innovationsqualitaet",
    "wissensbasis", "zuverlaessigkeit", "erklaerbarkeit",
    "quellen_transparenz", "praktische_einsetzbarkeit", "integrationsfaehigkeit",
    "interaktivitaet", "benutzerfreundlichkeit", "eignung_zielgruppen"
]

EVALUATION_DATA = {
    'scenario': "",
    'prompt': "",
    'tool_responses': {
        'chatgpt': "",
        'asknature': "",
        'bidara': ""
    },
    'scores': None,
    'weights': None
}

# --- Hilfsfunktionen  ---
def count_terms(text, terms):
    t = (text or "").lower()
    return sum(1 for term in terms if term in t)

def scale_count_to_1_5(cnt):
    if cnt <= 0: return 1
    if cnt == 1: return 2
    if cnt == 2: return 3
    if cnt == 3: return 4
    return 5

def length_score(text):
    n = len((text or "").split())
    if n < 20: return 1
    if n < 50: return 2
    if n < 120: return 3
    if n < 300: return 4
    return 5

def citation_score(text):
    t = (text or "").lower()

    # 5 = überprüfbare Quellen
    if re.search(r'(http[s]?://|doi\s*[:]|arxiv\s*[:]|isbn\s*[:])', t):
        return 5

    # 4 = benannte Studien, Autoren oder Institutionen
    if re.search(
        r'\b(study|studies|paper|journal|according to|et al\.?|author|forschung von|beschrieben von)\b',
        t
    ):
        return 4

    # 3 = Fachbegriffe OHNE Quellen
    if re.search(
        r'\b(van[- ]der[- ]waals|lotus[- ]effekt|adhäsion|kapillarkraft|mikrostruktur)\b',
        t
    ):
        return 3

    # 2 = nur wissenschaftlicher Stil
    if re.search(
        r'\b(mechanismus|prinzip|stand der technik|bekannt|bewährt)\b',
        t
    ):
        return 2

    # 1 = keine Anzeichen von Quellen
    return 1

def source_transparency_score(text):
    t = (text or "").lower()

    # echte, überprüfbare Quellen
    explicit_sources = [
        "doi", "http", "https", "et al.", "isbn",
        "ieee", "springer", "elsevier", "nature",
        "science", "journal", "proceedings"
    ]

    # vage Verweise (zählen NICHT als echte Quelle)
    vague_sources = [
        "stand der technik", "bekannt", "wird beschrieben",
        "studien zeigen", "forschung zeigt", "bar-cohen"
    ]

    if any(src in t for src in explicit_sources):
        return 5
    if any(src in t for src in vague_sources):
        return 2
    return 1


def lexical_diversity_score(text):
    tokens = re.findall(r'\w+', (text or "").lower())
    if not tokens: return 1
    uniq = len(set(tokens))
    ratio = uniq / len(tokens)
    if ratio < 0.25: return 1
    if ratio < 0.4: return 2
    if ratio < 0.55: return 3
    if ratio < 0.7: return 4
    return 5

def modal_weakness_score(text):
    t = (text or "").lower()
    cnt = sum(t.count(m) for m in [" könnte ", " sollte ", " vielleicht ", " eventuell ", " möglich "])
    if cnt == 0: return 5
    if cnt == 1: return 4
    if cnt == 2: return 3
    if cnt == 3: return 2
    return 1

def evaluate_text_by_heuristics(text):
    t = (text or "").lower()
    bio_terms = [
    # Oberflächen & Hydrophobie
    "lotus", "hydrophob", "mikrostruktur", "kontaktwinkel", "oberfläche", "rauheit", "blatt", "wachsschicht",
    # Haftung & Adhäsion
    "gecko", "haftung", "adhäsion", "setae", "spatulae", "mikrohaare", "klettern", "haftmechanismus", "nanohaare", "trockenhaftung", "van-der-waals",
    # Struktur- und Leichtbau
    "bambus", "spinnennetz", "vogelknochen", "koralle", "skelett", "struktur", "leichtbau", "tragwerk",
    # Bewegung & Kinematik
    "flügel", "flosse", "beugung", "muskel", "sehne", "bewegung", "robotik", "mechanik", "klettern", "vertikal", "überkopf", 
    # Energie & Anpassung
    "photosynthese", "lichtlenkung", "energieeffizienz", "selbstorganisation", "adaptiv", "anpassung",
    # Sensorik & Wahrnehmung
    "sensor", "vibrisse", "auge", "echo", "resonanz", "wahrnehmung",
    # Material & Oberflächen
    "keratin", "schuppen", "haut", "selbstheilend", "wachs", "nanostruktur", "elastomer", "polymer", "funktionsoberfläche", "mikrostrukturierung"
]

    trans_terms = [
    "anwenden", "implementieren", "übertragen", "skalieren", "prototyp", "fertigen", "überführung", "anwendbarkeit",
    "konstruktion", "bauweise", "designprinzip", "modell", "architektur", "strukturübertragung"
]

    innov_terms = [
    "neuheit", "innovativ", "neuer ansatz", "kombinieren", "hybrid", "kreativ", "ungewöhnlich",
    "visionär", "experimentell", "erfinderisch", "disruptiv", "originell"
]

    integ_terms = [
    "api", "csv", "json", "export", "integrieren", "schnittstelle", "datenbank", "plugin",
    "workflow", "pipeline", "systemintegration", "kompatibel", "plattform"
]

    practical_terms = [
    "prototyp", "fertigung", "realisierbar", "skalierbar", "kosten", "material", "test", "machbarkeit",
    "produktion", "herstellung", "baubar", "umsetzung", "experiment", "validierung"
]

    interakt_terms = [
    "interaktiv", "dialog", "fragen", "follow-up", "konversation", "feedback",
    "antwort", "nutzerreaktion", "beteiligung", "kommunikation", "austausch", 
    "anpassung", "reaktion", "iteration", "rückmeldung"
]

    ux_terms = [
    "einfach", "intuitiv", "nutzerfreundlich", "klar", "schritt-für-schritt", "übersicht",
    "bedienbar", "komfortabel", "verständlich", "ergonomisch", "zugänglich", 
    "leicht nachvollziehbar", "benutzerorientiert", "selbsterklärend"
]

    target_terms = [
    "student", "forscher", "industrie", "ingenieur", "designer", "experte",
    "architekt", "biologe", "entwickler", "dozent", "anwender", 
    "unternehmen", "schule", "akademisch", "wissenschaftlich", "praxisorientiert"
]


    scores = {}
    scores["fachliche_relevanz"] = scale_count_to_1_5(count_terms(t, bio_terms))
    scores["uebertragbarkeit"] = scale_count_to_1_5(count_terms(t, trans_terms))
    innov_count = count_terms(t, innov_terms)
    scores["innovationsqualitaet"] = max(scale_count_to_1_5(innov_count), lexical_diversity_score(t))
    scores["wissensbasis"] = citation_score(t)
    scores["zuverlaessigkeit"] = modal_weakness_score(t)
    scores["erklaerbarkeit"] = length_score(t)
    scores["quellen_transparenz"] = source_transparency_score(t)
    scores["praktische_einsetzbarkeit"] = scale_count_to_1_5(count_terms(t, practical_terms))
    scores["integrationsfaehigkeit"] = scale_count_to_1_5(count_terms(t, integ_terms))
    scores["interaktivitaet"] = scale_count_to_1_5(count_terms(t, interakt_terms))
    ux_cnt = count_terms(t, ux_terms)
    scores["benutzerfreundlichkeit"] = scale_count_to_1_5(ux_cnt) if ux_cnt > 0 else 3
    scores["eignung_zielgruppen"] = scale_count_to_1_5(count_terms(t, target_terms))

    for k in scores:
        v = scores[k]
        scores[k] = int(min(5, max(1, v)))
    return scores

# --- Gleichstände vermeiden ---
def compute_weighted_score(feature_scores, weights, extra_factor=0.0):
    total_w = sum(weights.values()) if sum(weights.values()) > 0 else len(CRITERIA) * 1.0
    weighted_sum = 0.0
    for c in CRITERIA:
        score_value = feature_scores.get(c, 1)
        weight_value = weights.get(c, 1)
        weighted_sum += score_value * weight_value
    max_possible_sum = 5 * sum(weights.values())
    if max_possible_sum == 0:
        return 0
    percentage_score = (weighted_sum / max_possible_sum) * 100
    # Füge kleinen Bonus hinzu
    percentage_score += extra_factor
    return round(percentage_score, 1)

def classify(score):
    if score >= 80:
        return "Sehr geeignet für dieses Szenario"
    if score >= 60:
        return "Geeignet mit Einschränkungen"
    if score >= 40:
        return "Bedingt geeignet"
    return "Derzeit nicht geeignet"

# --- Flask Routen ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scenario', methods=['GET', 'POST'])
@app.route('/1_scenario', methods=['GET', 'POST'])
@app.route('/1_scenario.html', methods=['GET', 'POST'])
def scenario_input():
    if request.method == 'POST':
        EVALUATION_DATA['scenario'] = request.form.get('scenario', EVALUATION_DATA['scenario'])
        EVALUATION_DATA['prompt'] = request.form.get('prompt', EVALUATION_DATA['prompt'])
        return redirect(url_for('tools'))
    return render_template('1_scenario.html')

@app.route('/tools', methods=['GET', 'POST'])
@app.route('/2_tools', methods=['GET', 'POST'])
@app.route('/2_tools.html', methods=['GET', 'POST'])
@app.route('/tools.html', methods=['GET', 'POST'])
def tools():
    if request.method == 'POST':
        EVALUATION_DATA['scenario'] = request.form.get('scenario', EVALUATION_DATA['scenario'])
        EVALUATION_DATA['prompt'] = request.form.get('prompt', EVALUATION_DATA['prompt'])
    return render_template('2_tools.html',
                           scenario=EVALUATION_DATA['scenario'],
                           prompt=EVALUATION_DATA['prompt'],
                           tools=TOOLS,
                           results=EVALUATION_DATA['tool_responses'])

@app.route('/save_tools', methods=['POST'])
def save_tools():
    for key in ['chatgpt_response', 'asknature_response', 'bidara_response']:
        if key in request.form:
            tool_id = key.split('_')[0]
            EVALUATION_DATA['tool_responses'][tool_id] = request.form.get(key)
    for key, val in request.form.items():
        if key.endswith('_response') and key.split('_')[0] in TOOLS:
            tid = key.split('_')[0]
            EVALUATION_DATA['tool_responses'][tid] = val
    return ("OK", 204)

@app.route('/evaluation', methods=['GET', 'POST'])
@app.route('/3_evaluation', methods=['GET', 'POST'])
@app.route('/3_evaluation.html', methods=['GET', 'POST'])
@app.route('/evaluation.html', methods=['GET', 'POST'])
def evaluation():
    if request.method == 'GET':
        responses = EVALUATION_DATA.get('tool_responses', {})
        if not responses or not all(responses.get(t, "").strip() for t in TOOLS.keys()):
            return render_template(
                '3_evaluation.html',
                tools=TOOLS,
                criteria_keys=CRITERIA,
                tool_features=None,
                message="⚠️ Bitte fügen Sie im vorherigen Schritt (Schritt 2) die Antworten der drei KI-Tools ein, bevor eine Bewertung möglich ist."
            )
        tool_features = {
            tool_id: evaluate_text_by_heuristics(responses[tool_id])
            for tool_id in TOOLS.keys()
        }
        return render_template(
            '3_evaluation.html',
            tools=TOOLS,
            criteria_keys=CRITERIA,
            tool_features=tool_features,
            message=None
        )

    weights = {}
    ratings = {tool_id: {} for tool_id in TOOLS.keys()}

    for key, value in request.form.items():
        if key.startswith('w_'):
            criterion_key = key[2:]
            try:
                weights[criterion_key] = int(value)
            except:
                weights[criterion_key] = 1
        elif key.startswith('r_'):
            parts = key.split('_', 2)
            if len(parts) == 3:
                tool_id = parts[1]
                criterion_key = parts[2]
                try:
                    ratings[tool_id][criterion_key] = int(value)
                except:
                    ratings[tool_id][criterion_key] = 1

    if not weights:
        weights = {c: 1 for c in CRITERIA}

    final_scores = {}
    for tool_id in TOOLS.keys():
        text = EVALUATION_DATA['tool_responses'][tool_id]
        diversity_bonus = lexical_diversity_score(text) * 0.02  # bis +0.1 %
        score = compute_weighted_score(ratings[tool_id], weights, extra_factor=diversity_bonus)
        final_scores[tool_id] = {
            'name': TOOLS[tool_id],
            'score': score,
            'class': classify(score),
            'features': ratings[tool_id]
        }

    # Sortiert Scores, um Gleichstände auch bei Rundung zu verhindern
    unique_adjustment = 0.0001
    sorted_ids = sorted(final_scores.keys())
    for i, tid in enumerate(sorted_ids):
        final_scores[tid]['score'] += i * unique_adjustment

    EVALUATION_DATA['scores'] = final_scores
    EVALUATION_DATA['weights'] = weights
    return redirect(url_for('results'))

@app.route('/results', methods=['GET'])
@app.route('/4_results', methods=['GET'])
@app.route('/4_results.html', methods=['GET'])
@app.route('/results.html', methods=['GET'])
def results():
    scores = EVALUATION_DATA.get('scores')
    if scores:
        best_tool_id = max(scores, key=lambda k: scores[k]['score'])
        recommendation = (
            f"Auf Basis der von Ihnen gesetzten Gewichtungen ist {scores[best_tool_id]['name']} "
            f"mit einem Gesamtscore von {scores[best_tool_id]['score']}% der höchsteingestufte Tool."
        )
        score_list = [scores[k] for k in TOOLS.keys()]
    else:
        recommendation = None
        score_list = None

    return render_template('4_results.html',
                           recommendation=recommendation,
                           score_list=score_list,
                           tools=TOOLS,
                           criteria=CRITERIA,
                           weights=EVALUATION_DATA.get('weights'))

@app.route('/algorithm', methods=['GET'])
def algorithm_page():
    return render_template("5_algorithm.html")

if __name__ == "__main__":
    app.run(debug=True)
