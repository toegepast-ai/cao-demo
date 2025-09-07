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

    # Try importing optional dependencies
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
    # CAO → JSON Demo (Simplified)

    Upload a CAO PDF or TXT file to extract basic information using regex patterns.
    """
    )
    return


@app.cell
def _(mo):
    # File upload interface
    file_upload = mo.ui.file(filetypes=[".pdf"], label="Upload CAO document")
    file_upload
    return (file_upload,)


@app.cell
def _(file_upload, io, mo, pdf_available, pypdf):
    # Extract text from uploaded file
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
                text = f"PDF extraction error: {e}"
        elif filename.lower().endswith('.txt'):
            try:
                text = raw_data.decode('utf-8', errors='ignore')
            except Exception as e:
                text = f"Text extraction error: {e}"
        else:
            text = "Unsupported file format"

    if text and len(text) > 500:
        acc_text = mo.accordion({"📄 Extracted Text": mo.ui.text_area(value=text[:500] + "...", disabled=True)})
    elif text:
        acc_text = mo.accordion({"📄 Extracted Text": mo.ui.tex_area(value=text, disabled=True)})
    else:
        acc_text = mo.md("👆 Upload a file to see extracted text")
    acc_text
    return (text,)


@app.cell
def _(mo, re, text):
    # Simple CAO information extraction
    if not text:
        findings = []
    else:
        findings = []

        # Look for vacation allowance (vakantietoeslag)
        vacation_match = re.search(r'vakantie(?:toeslag|geld).*?(\d+(?:[.,]\d+)?)\s*%', text, re.IGNORECASE)
        if vacation_match:
            findings.append({
                "type": "Vakantietoeslag",
                "value": vacation_match.group(1) + "%",
                "found_in": vacation_match.group(0)[:100]
            })

        # Look for working hours (werktijd)
        hours_match = re.search(r'(?:werk|arbeid).*?(\d+)\s*(?:uur|u).*?(?:week|pw)', text, re.IGNORECASE)
        if hours_match:
            findings.append({
                "type": "Werktijd",
                "value": hours_match.group(1) + " uur per week",
                "found_in": hours_match.group(0)[:100]
            })

        # Look for travel allowance (reiskosten)
        travel_match = re.search(r'(?:reis|km).*?(\d+(?:[.,]\d+)?)\s*(?:cent|€)', text, re.IGNORECASE)
        if travel_match:
            findings.append({
                "type": "Reiskosten",
                "value": travel_match.group(1),
                "found_in": travel_match.group(0)[:100]
            })

    if findings:
        mo.md(f"## Found {len(findings)} CAO provisions:")
        mo.ui.table(findings)
    else:
        mo.md("## No CAO provisions found")
    return (findings,)


@app.cell
def _(datetime, findings, json, mo):
    # Generate simple JSON output
    cao_data = None
    if findings:
        cao_data = {
            "extracted_at": datetime.datetime.now().isoformat(),
            "provisions": findings,
            "total_found": len(findings)
        }

        acc = mo.accordion(items={
            "📋 JSON Output": mo.ui.code_editor(json.dumps(cao_data, indent=2, ensure_ascii=False), language="json")
            },lazy=True)
    else:
        acc = mo.md("*No data to export*")
    acc
    return


@app.cell
def _(mo):
    mo.md(
        """
    ---

    ### Instructions
    1. Upload a CAO PDF file using the file picker above
    2. The app will extract text and search for common CAO provisions
    3. Results are shown in a table and JSON format

    **Supported patterns:**
    - Vakantietoeslag: percentage mentions
    - Werktijd: hours per week
    - Reiskosten: travel allowance rates
    """
    )
    return


if __name__ == "__main__":
    app.run()
