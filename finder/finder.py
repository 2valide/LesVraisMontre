import os
import requests
import io
import json
import logging
from typing import Dict, List, Tuple, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WatchFinder:
    def __init__(self, api_key="AIzaSyA9MJP64sXt4vBeN8TSiVtCJLWY6WVtusA", search_engine_id="a49533e42ffa94a30"):
        self.api_key = api_key or os.environ.get("SEARCH_API_KEY")
        self.search_engine_id = search_engine_id or os.environ.get("SEARCH_ENGINE_ID")

        if not self.api_key:
            logger.warning("Aucune clé API fournie. La fonctionnalité de recherche peut être limitée.")

    def search_authentic_watches(self, metadata: Dict[str, Any],
                                max_results: int = 5) -> List[Dict[str, Any]]:
        try:
            search_terms = []

            if metadata.get("brand") and metadata.get("brand") != "Inconnu":
                search_terms.append(metadata.get("brand", ""))

            if metadata.get("model") and metadata.get("model") != "Inconnu":
                search_terms.append(metadata.get("model", ""))

            if metadata.get("series"):
                search_terms.append(metadata.get("series"))

            if metadata.get("year"):
                search_terms.append(str(metadata.get("year")))

            if metadata.get("color"):
                search_terms.append(metadata.get("color"))

            if not search_terms:
                search_terms.append("montre luxe")

            search_terms.extend(["montre authentique", "montre originale", "official watch"])
            search_query = " ".join([term for term in search_terms if term])

            if not self.api_key:
                logger.warning("Clé API Google manquante. Utilisation du mode simulation.")
                return self._simulate_search_results(max_results)

            base_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": search_query,
                "key": self.api_key,
                "cx": self.search_engine_id,
                "searchType": "image",
                "num": max_results
            }

            logger.info(f"Recherche avec les termes: {search_query}")

            response = requests.get(base_url, params=params)

            if response.status_code != 200:
                logger.error(f"Erreur API: {response.status_code}, {response.text}")
                return self._simulate_search_results(max_results)

            search_data = response.json()
            results = []

            if "items" in search_data:
                for item in search_data["items"][:max_results]:
                    result = {
                        "title": item.get("title", ""),
                        "source_url": item.get("contextLink", ""),
                        "image_url": item.get("link", ""),
                        "source_name": self._extract_domain(item.get("displayLink", "")),
                    }
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'images: {str(e)}")
            return self._simulate_search_results(max_results)

    def _extract_domain(self, display_link: str) -> str:
        if not display_link:
            return "Source inconnue"
        return display_link.replace("www.", "")

    def download_images(self, search_results: List[Dict[str, Any]],
                        output_dir: str) -> List[Dict[str, Any]]:
        os.makedirs(output_dir, exist_ok=True)

        for i, result in enumerate(search_results):
            try:
                response = requests.get(result["image_url"], stream=True)
                if response.status_code == 200:
                    img_path = os.path.join(output_dir, f"authentic_watch_{i+1}.jpg")
                    with open(img_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    result["local_path"] = img_path
                    logger.info(f"Image téléchargée: {result['local_path']}")
                else:
                    logger.warning(f"Échec du téléchargement de l'image: {response.status_code}")
                    result["local_path"] = None
            except Exception as e:
                logger.error(f"Erreur lors du téléchargement de l'image {i}: {str(e)}")
                result["local_path"] = None

        return search_results


def find_authentic_watches(input_image_path: str,
                         metadata: Dict[str, Any] = None,
                         output_dir: str = None,
                         payload: Dict[str, Any] = None) -> Dict[str, Any]:
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'static', 'authentic_references')

    combined_metadata = {}

    if metadata:
        combined_metadata.update(metadata)

    if payload:
        if 'input' in payload and 'metadata' in payload['input']:
            payload_metadata = payload['input']['metadata']
            for key, value in payload_metadata.items():
                if key not in combined_metadata:
                    combined_metadata[key] = value

    finder = WatchFinder()

    search_results = finder.search_authentic_watches(combined_metadata)

    downloaded_results = finder.download_images(search_results, output_dir)

    result = {
        "input_image": input_image_path,
        "metadata": combined_metadata,
        "authentic_references": downloaded_results,
        "summary": {
            "brand": combined_metadata.get("brand", "Non spécifié"),
            "model": combined_metadata.get("model", "Non spécifié"),
            "references_found": len(downloaded_results),
        }
    }

    return result


if __name__ == "__main__":
    test_metadata = {"brand": "Rolex", "model": "Submariner", "color": "bleu"}
    results = find_authentic_watches("test_watch.jpg", metadata=test_metadata)
    print(json.dumps(results, indent=2))
