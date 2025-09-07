# CAO → JSON Demo

Een Marimo notebook die CAO documenten analyseert en structureert in JSON format.

## 🚀 Quick Start

### Lokaal runnen:
```bash
pip install marimo pypdf jsonschema
marimo edit cao_demo.py
```

### Online gebruiken:
Ga naar [Marimo Cloud link] (na publishing)

## 📋 Features

- PDF tekst extractie
- Regex pattern matching voor CAO bepalingen  
- JSON data model voor gestructureerde output
- Voorbeeld CAO data (Bouw & Infra)

## 🔍 Ondersteunde Patronen

- **Vakantietoeslag**: Percentage detectie
- **Werktijd**: Uren per week detectie  
- **Reiskosten**: Vergoedingstarief detectie

## 📊 Data Model

```json
{
  "geëxtraheerd_op": "2025-09-07T...",
  "bepalingen": [
    {
      "type": "Vakantietoeslag",
      "value": "8%", 
      "found_in": "De vakantietoeslag bedraagt 8%..."
    }
  ],
  "totaal_gevonden": 1
}
```

## 🛠️ Tech Stack

- [Marimo](https://marimo.io) - Interactive notebook
- [pypdf](https://pypdf.readthedocs.io/) - PDF text extraction
- [jsonschema](https://python-jsonschema.readthedocs.io/) - JSON validation

## 📝 License

MIT License - zie LICENSE bestand
