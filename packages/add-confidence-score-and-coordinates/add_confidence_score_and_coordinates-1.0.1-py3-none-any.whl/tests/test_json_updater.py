import pytest
from add_confidence_and_coordinates.openai_json_updater import JSONUpdater

def test_update_confidence_score_with_coordinates():
    json_updater = JSONUpdater()
    openai_json_response = {
        "balance_sheet": {
            "assets": {
                "cash": [
                    {
                        "1120 - Operating Trust Account": {
                            "value": "-4960.59",
                            "page_number": 3
                        }
                    }
                ]
            }
        }
    }
    ocr_response = {
        "azure_ocr_pages_response": {
            "3": {
                "pages": [
                    {
                        "words": [
                            {
                                "content": "1120 - Operating Trust Account",
                                "confidence": 0.99,
                                "polygon": [0, 0, 1, 1]
                            },
                            {
                                "content": "-4960.59",
                                "confidence": 0.98,
                                "polygon": [0, 0, 1, 1]
                            }
                        ],
                        "width": 1000,
                        "height": 1000
                    }
                ]
            }
        }
    }
    response = json_updater.update_confidence_score_with_coordinates(openai_json_response, ocr_response, "doc_intelligence")
    assert "confidence_score" in response["balance_sheet"]["assets"]["cash"][0]["1120 - Operating Trust Account"]
    assert "coordinates_list" in response["balance_sheet"]["assets"]["cash"][0]["1120 - Operating Trust Account"]