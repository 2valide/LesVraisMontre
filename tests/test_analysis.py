import pytest
from unittest.mock import patch, MagicMock
from ai.analysis import analyze_watch

@pytest.fixture
def mock_image():
    with patch("ai.analysis.Image") as mock_img:
        mock_instance = MagicMock()
        mock_img.open.return_value = mock_instance
        mock_instance.convert.return_value = mock_instance
        yield mock_instance

@patch("ai.analysis.classifier")
@patch("ai.analysis.find_watch_model")
@patch("ai.analysis.assess_reality")
def test_analyze_watch_with_watch(mock_assess, mock_find, mock_classifier, mock_image):
    """Test analyze_watch lorsqu'une montre est détectée"""
    # Configuration des mocks
    mock_classifier.return_value = [
        {"label": "wristwatch", "score": 0.9},
        {"label": "something else", "score": 0.1}
    ]
    mock_find.return_value = [("Rolex Submariner", 0.8)]
    mock_assess.return_value = 95.5

    # Appel de la fonction à tester
    result = analyze_watch("test_image.jpg")

    # Vérifications
    assert result["is_watch"] == True
    assert result["watch_models"] == [("Rolex Submariner", 0.8)]
    assert result["reality_score"] == 95.5
    mock_find.assert_called_once_with("test_image.jpg")
    mock_assess.assert_called_once_with("test_image.jpg")

@patch("ai.analysis.classifier")
def test_analyze_watch_no_watch(mock_classifier, mock_image):
    """Test analyze_watch lorsqu'aucune montre n'est détectée"""
    # Configuration du mock pour simuler qu'aucune montre n'est détectée
    mock_classifier.return_value = [
        {"label": "phone", "score": 0.9},
        {"label": "computer", "score": 0.1}
    ]

    # Appel de la fonction à tester
    result = analyze_watch("test_image.jpg")

    # Vérifications
    assert result == {"is_watch": False}
