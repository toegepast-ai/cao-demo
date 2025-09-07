import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import io
    import re
    import json
    import datetime
    import os

    # Probeer optionele afhankelijkheden te importeren
    try:
        import pypdf
        pdf_available = True
    except ImportError:
        pypdf = None
        pdf_available = False

    try:
        import jsonschema
        schema_available = True
    except ImportError:
        jsonschema = None
        schema_available = False
    return datetime, json, mo, os, pdf_available, pypdf, re


@app.cell
def _(mo):
    mo.md(
        """
    # CAO → JSON Demo 

    Upload een CAO PDF bestand om basisinformatie te extraheren met behulp van regex-patronen. 
    Dit voorbeeld demonstreert een data model voor CAO-informatie en hoe deze gestructureerd kan worden in JSON-format.

    💡 **Demo Mode**: Deze versie toont automatisch resultaten van een voorbeeld CAO (Bouw & Infra 2025-2027).

    ### Data Model
    - **Vakantietoeslag**: percentage vermeldingen
    - **Werktijd**: uren per week  
    - **Reiskosten**: vergoedingstarief
    """
    )
    return


@app.cell
def _(mo, os, pdf_available, pypdf):
    # Extraheer tekst uit voorbeeld bestand (voor static demo)
    text = ""
    filename = ""

    # Gebruik voorbeeld PDF voor demo
    voorbeeld_path = "cao_voorbeeld/Cao Bouw en Infra 2025 - 2027.pdf"
    if os.path.exists(voorbeeld_path) and pdf_available:
        try:
            with open(voorbeeld_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            filename = "Cao Bouw en Infra 2025 - 2027.pdf"
        except Exception as e:
            text = f"PDF fout: {e}"
            filename = "Error"

    # Toon tekst zonder accordion (static-friendly)
    if text and len(text) > 1000:
        mo.md(f"""
        ## 📄 Geëxtraheerde Tekst ({filename})

        ```
        {text[:1000]}...

        [Tekst ingekort voor weergave - totaal {len(text)} karakters]
        ```
        """)
    elif text:
        mo.md(f"""
        ## 📄 Geëxtraheerde Tekst ({filename})

        ```
        {text}
        ```
        """)
    else:
        mo.md("❌ Geen tekst gevonden")
    return (text,)


@app.cell
def _(mo, re, text):
    # CAO informatie extractie
    findings = []

    if text:
        # Zoek naar vakantietoeslag
        vacation_match = re.search(r'vakantie(?:toeslag|geld).*?(\d+(?:[.,]\d+)?)\s*%', text, re.IGNORECASE)
        if vacation_match:
            findings.append({
                "type": "Vakantietoeslag",
                "value": vacation_match.group(1) + "%",
                "found_in": vacation_match.group(0)[:100]
            })

        # Zoek naar werktijden
        hours_match = re.search(r'(?:werk|arbeid).*?(\d+)\s*(?:uur|u).*?(?:week|pw)', text, re.IGNORECASE)
        if hours_match:
            findings.append({
                "type": "Werktijd", 
                "value": hours_match.group(1) + " uur per week",
                "found_in": hours_match.group(0)[:100]
            })

        # Zoek naar reiskostenvergoeding
        travel_match = re.search(r'(?:reis|km).*?(\d+(?:[.,]\d+)?)\s*(?:cent|€)', text, re.IGNORECASE)
        if travel_match:
            findings.append({
                "type": "Reiskosten",
                "value": travel_match.group(1),
                "found_in": travel_match.group(0)[:100]
            })

    # Toon resultaten zonder table widget (static-friendly)
    output_md = ""
    if findings:
        mo.md(f"""
        ## ✅ {len(findings)} CAO Bevindingen Gevonden:
        """)

        # Maak markdown tabel
        rows = []
        for find in findings:
            rows.append(f"| {find['type']} | {find['value']} | {find['found_in'][:50]}... |")

        table_md = """
    | Type | Waarde | Gevonden in tekst |
    |------|--------|-------------------|
    """ + "\n".join(rows)

        output_md = mo.md(table_md)
    else:
        output_md = mo.md("## ❌ Geen CAO bevindingen gevonden")
    output_md
    return (findings,)


@app.cell
def _(datetime, findings, json, mo):
    # JSON uitvoer (static-friendly)
    cao_data = None
    json_output = ""

    if findings:
        cao_data = {
            "geëxtraheerd_op": datetime.datetime.now().isoformat(),
            "bepalingen": findings,
            "totaal_gevonden": len(findings)
        }

        # Netjes geformatteerde JSON output
        json_output = json.dumps(cao_data, indent=2, ensure_ascii=False)

    else:
        mo.md("## 📋 JSON Output\n\n*Geen data om te exporteren*")

    print(json_output)
    return


if __name__ == "__main__":
    app.run()
