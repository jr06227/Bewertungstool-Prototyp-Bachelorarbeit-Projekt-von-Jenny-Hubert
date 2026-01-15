# Tool zur Bewertung generativer KI im Innovationsprozess

Dieses Repository beinhaltet den Quellcode des webbasierten Bewertungstools, das im Rahmen der Bachelorarbeit von Jenny Hubert entwickelt wurde. 
Das Tool dient der systematischen Analyse und Evaluation von KI-Sprachmodellen im Kontext bionischer Fragestellungen.

## Ziel des Projekts

Das Tool ermöglicht eine systematische Bewertung von KI-Tools (ChatGPT, AskNature Chat und BIDARA) anhand eines einheitlichen Szenarios.  
Es bietet Forschenden und Studierenden eine transparente Entscheidungsgrundlage für den Einsatz KI-basierter Tools in der Bionik.
Kern des Tools ist ein heuristisches Modell, das qualitative Kriterien in messbare Punkte übersetzt. 
Der Code ist modular strukturiert, damit der Prototyp für zukünftige Projekte einfach angepasst werden kann.

## Technische Grundlage

- Programmiersprache: Python
- Webframework: Flask
- Frontend: HTML / CSS
- Bewertungslogik: Regelbasierte heuristische Analyse

## Installation und Start

### Voraussetzungen
- Python 3.9 oder höher
- pip (Python Package Manager)

### Installation
```bash
pip install -r requirements.txt
python app.py