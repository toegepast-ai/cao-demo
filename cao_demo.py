import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium", layout_file="layouts/cao_demo.slides.json")


@app.cell
def _(mo):
    mo.md(
        """
    # CAO → JSON Demo 

    Upload een CAO PDF bestand om basisinformatie te extraheren met behulp van regex-patronen. 
    Dit voorbeeld demonstreert een data model voor CAO-informatie en hoe deze gestructureerd kan worden in JSON-format.

    💡 **Automatisch geladen**: Bij opstarten wordt een voorbeeld CAO (Bouw & Infra) gebruikt om de functionaliteit te demonstreren.

    ### Instructies
    1. Upload een CAO PDF bestand met de bestandskiezer hieronder (optioneel - voorbeeld is al geladen)
    2. De stappen in deze notebook extraheert tekst en zoekt naar veelvoorkomende CAO bepalingen
    3. Resultaten worden getoond in een tabel en JSON formaat

    **Ondersteunde REGEX patronen:**
    - Vakantietoeslag: percentage vermeldingen
    - Werktijd: uren per week
    - Reiskosten: vergoedingstarief
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import io
    import re
    import json
    import datetime

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
    return datetime, io, json, mo, pdf_available, pypdf, re


@app.cell
def _(mo):
    # Bestand upload interface
    file_upload = mo.ui.file(filetypes=[".pdf"], label="Upload CAO document")
    file_upload
    return (file_upload,)


@app.cell
def _(file_upload, io, mo, pdf_available, pypdf):
    # Extraheer tekst uit geüpload bestand of gebruik voorbeeld
    import os
    
    acc_text = None
    if not file_upload.contents():
        # Gebruik voorbeeld PDF als geen bestand is geüpload
        voorbeeld_path = "cao_voorbeeld/Cao Bouw en Infra 2025 - 2027.pdf"
        if os.path.exists(voorbeeld_path) and pdf_available:
            try:
                with open(voorbeeld_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                filename = "Voorbeeld: Cao Bouw en Infra 2025 - 2027.pdf"
                mo.callout("📋 Voorbeeld data geladen! Upload je eigen CAO PDF om andere data te analyseren.", kind="info")
            except Exception as e:
                text = f"Voorbeeld PDF fout: {e}"
                filename = ""
        else:
            text = ""
            filename = ""
    else:
        filename = file_upload.name()
        raw_data = file_upload.contents()

        if filename.lower().endswith(".pdf") and pdf_available:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(raw_data))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                text = f"PDF extractie fout: {e}"
        elif filename.lower().endswith(".txt"):
            try:
                text = raw_data.decode("utf-8", errors="ignore")
            except Exception as e:
                text = f"Tekst extractie fout: {e}"
        else:
            text = "Niet-ondersteund bestandsformaat"

    if text and len(text) > 500:
        acc_text = mo.accordion(
            {
                f"📄 Geëxtraheerde Tekst ({filename})": mo.ui.text_area(
                    value=text[:500] + "...", disabled=True
                )
            }
        )
    elif text:
        acc_text = mo.accordion(
            {f"📄 Geëxtraheerde Tekst ({filename})": mo.ui.text_area(value=text, disabled=True)}
        )
    else:
        acc_text = mo.md(
            "👆 Upload een PDF bestand om de geëxtraheerde tekst te zien"
        )
    acc_text
    return (text,)


@app.cell
def _(mo, re, text):
    # Eenvoudige CAO informatie extractie
    if not text:
        findings = []
    else:
        findings = []

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

    if findings:
        mo.md(f"## {len(findings)} CAO bevindingen:")
        mo.ui.table(findings)
    else:
        mo.md("## Geen CAO bevindingen gevonden")
    return (findings,)


@app.cell
def _(datetime, findings, json, mo):
    # Genereer eenvoudige JSON uitvoer
    cao_data = None
    if findings:
        cao_data = {
            "geëxtraheerd_op": datetime.datetime.now().isoformat(),
            "bepalingen": findings,
            "totaal_gevonden": len(findings)
        }

        acc = mo.accordion(items={
            "📋 JSON Ouput": mo.ui.code_editor(json.dumps(cao_data, indent=2, ensure_ascii=False), language="json")
            },lazy=True)
    else:
        acc = mo.md("*Geen data om te exporteren*")
    acc
    return


if __name__ == "__main__":
    app.run()
