from tools.validate_etf_eu_routine_pdf_client_grade import validate_language_contract


def test_dutch_client_language_contract_passes_clean_surface() -> None:
    markdown = "| Handelslijn | ISIN | Peildatum | Slot | Valuta | Status |"
    result = validate_language_contract(
        markdown_text=markdown,
        html_text="<th>Handelslijn</th><th>Peildatum</th>",
        pdf_text="Handelslijn ISIN Peildatum Slot Valuta Status",
        language="nl",
    )
    assert result["semantic_pricing_header_passed"] is True
    assert result["residual_client_language_defects"] == []
    assert result["client_language_contract_passed"] is True


def test_dutch_client_language_contract_rejects_old_visible_defects() -> None:
    result = validate_language_contract(
        markdown_text="| Trading line | ISIN | Markt | Slot | Valuta | Status |",
        html_text="broker- en bevestiging van de handelslijn",
        pdf_text="Geen portefeuillewijziging zonder afzonderlijke afzonderlijk besluit.",
        language="nl",
    )
    assert result["semantic_pricing_header_passed"] is False
    assert "Trading line" in result["residual_client_language_defects"]
    assert "broker- en bevestiging" in result["residual_client_language_defects"]
    assert "afzonderlijke afzonderlijk" in result["residual_client_language_defects"]
    assert result["client_language_contract_passed"] is False


def test_english_client_language_contract_requires_pricing_date_header() -> None:
    result = validate_language_contract(
        markdown_text="| Trading line | ISIN | Pricing date | Close | Currency | Status |",
        html_text="Pricing date",
        pdf_text="Trading line ISIN Pricing date Close Currency Status",
        language="en",
    )
    assert result["client_language_contract_passed"] is True
