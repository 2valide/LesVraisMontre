import pytest
from unittest.mock import patch, MagicMock
from ai.findWatch import find_watch_model, assess_reality, WATCH_LABELS, FAKE_LABELS

@pytest.fixture
def mock_image():
    with patch("ai.findWatch.Image") as mock_img:
        mock_instance = MagicMock()
        mock_img.open.return_value = mock_instance
        mock_instance.convert.return_value = mock_instance
        yield mock_instance

@patch("ai.findWatch.watch_model_classifier")
def test_find_watch_model(mock_classifier, mock_image):
    """Test la fonction find_watch_model"""
    # Configuration du mock
    mock_classifier.return_value = [
        {"label": "Rolex Submariner", "score": 0.8},
        {"label": "Rolex Daytona", "score": 0.5}
    ]

    # Appel de la fonction à tester
    result = find_watch_model("test_image.jpg")

    # Vérifications
    assert result == [("Rolex Submariner", 0.8), ("Rolex Daytona", 0.5)]
    mock_classifier.assert_called_once()
    args, kwargs = mock_classifier.call_args
    assert kwargs["candidate_labels"] == WATCH_LABELS

@patch("ai.findWatch.fake_detector")
def test_assess_reality_real(mock_detector, mock_image):
    """Test la fonction assess_reality avec une montre authentique"""
    # Configuration du mock pour simuler une montre réelle
    mock_detector.return_value = [
        {"label": "real watch", "score": 0.85},
        {"label": "fake watch", "score": 0.15}
    ]

    # Appel de la fonction à tester
    result = assess_reality("test_image.jpg")

    # Vérifications
    assert result == 85.0
    mock_detector.assert_called_once()
    args, kwargs = mock_detector.call_args
    assert kwargs["candidate_labels"] == FAKE_LABELS

@patch("ai.findWatch.fake_detector")
def test_assess_reality_fake(mock_detector, mock_image):
    """Test la fonction assess_reality avec une montre contrefaite"""
    # Configuration du mock pour simuler une montre contrefaite
    mock_detector.return_value = [
        {"label": "fake watch", "score": 0.95},
        {"label": "real watch", "score": 0.05}
    ]

    # Appel de la fonction à tester
    result = assess_reality("test_image.jpg")

    # Vérifications
    assert result == 5.0
    mock_detector.assert_called_once()
