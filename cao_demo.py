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
    mo.md(
        """
    # CAO → JSON Demo 

    Upload een CAO PDF bestand om basisinformatie te extraheren met behulp van regex-patronen. 
    Dit voorbeeld illustreert hoe CAO-informatie kan worden gestructureerd in een gestandaardiseerd JSON-format.
    """
    )
    return


@app.cell
def _(mo):
    # Bestand upload interface
    file_upload = mo.ui.file(filetypes=[".pdf"], label="Upload CAO document")
    file_upload
    return (file_upload,)


@app.cell
def _(file_upload, io, mo, pdf_available, pypdf):
    # Extraheer tekst uit geüpload bestand
    acc_text = None
    if not file_upload.value:
        text = ""
        filename = ""
    else:
        filename = file_upload.name()
        raw_data = file_upload.contents()

        if filename.lower().endswith('.pdf') and pdf_available:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(raw_data))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                text = f"PDF extractie fout: {e}"
        elif filename.lower().endswith('.txt'):
            try:
                text = raw_data.decode('utf-8', errors='ignore')
            except Exception as e:
                text = f"Tekst extractie fout: {e}"
        else:
            text = "Niet-ondersteund bestandsformaat"

    if text and len(text) > 500:
        acc_text = mo.accordion({"📄 Geëxtraheerde Tekst": mo.ui.text_area(value=text[:500] + "...", disabled=True)})
    elif text:
        acc_text = mo.accordion({"📄 Geëxtraheerde Tekst": mo.ui.tex_area(value=text, disabled=True)})
    else:
        acc_text = mo.md("👆 Upload een PDF bestand om de geëxtraheerde tekst te zien")
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


@app.cell
def _(mo):
    mo.md(
        """
    ---

    ### Instructies
    1. Upload een CAO PDF bestand met de bestandskiezer hierboven
    2. De app extraheert tekst en zoekt naar veelvoorkomende CAO bepalingen
    3. Resultaten worden getoond in een tabel en JSON formaat

    **Ondersteunde patronen:**
    - Vakantietoeslag: percentage vermeldingen
    - Werktijd: uren per week
    - Reiskosten: vergoedingstarief
    """
    )
    return


if __name__ == "__main__":
    app.run()
