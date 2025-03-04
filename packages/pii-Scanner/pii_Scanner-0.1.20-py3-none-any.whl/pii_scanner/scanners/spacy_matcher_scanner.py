import time
import logging
import random
import asyncio
import spacy
from spacy.matcher import Matcher
from typing import Dict, List, Union
from functools import lru_cache
from itertools import islice
from pii_scanner.regex_patterns.matcher_patterns import patterns
from pii_scanner.check_digit_warehouse.validate_entity_type import validate_entity_check_digit

logger = logging.getLogger(__name__)

class SpacyMatchScanner:
    """
    SpacyMatch Scanner for Named Entity Recognition (NER) and Regex-based entity detection.
    """

    SPACY_EN_MODEL = "en_core_web_lg"

    def __init__(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @lru_cache(maxsize=1)
    def _initialize(self, region: str):
        """Lazy initialization of the SpaCy model and Matcher with region-specific patterns."""
        try:
            nlp_engine = spacy.load(self.SPACY_EN_MODEL)
        except OSError:
            self.logger.warning("Downloading en_core_web_lg language model for SpaCy")
            from spacy.cli import download
            download(self.SPACY_EN_MODEL)
            nlp_engine = spacy.load(self.SPACY_EN_MODEL)

        matcher = Matcher(nlp_engine.vocab)
        combined_patterns = {**patterns.get("GLOBAL", {}), **patterns.get(region, {})}

        if not combined_patterns:
            self.logger.warning(f"No patterns found for region: {region}")

        for label, pattern in combined_patterns.items():
            try:
                matcher.add(label, [[{"TEXT": {"REGEX": pattern}}]])
            except Exception as e:
                self.logger.error(f"Failed to add pattern for {label}: {e}")

        return nlp_engine, matcher

    def _chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """Splits the text into smaller chunks for processing."""
        words = text.split()
        return [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]

    async def _scan_text_async(self, data: str, nlp_engine, matcher) -> List[Dict[str, Union[str, List[Dict[str, Union[str, int, float]]]]]]:
        """Asynchronously process a single text chunk using SpaCy and Matcher."""
        doc = nlp_engine(data)
        matched_patterns = []

        entity_matches = {ent.start_char: ent for ent in doc.ents}
        regex_matches = {start: (nlp_engine.vocab.strings[match_id], doc[start:end].text, start, end)
                         for match_id, start, end in matcher(doc)}

        for start in sorted(set(entity_matches.keys()) | set(regex_matches.keys())):
            if start in entity_matches:
                ent = entity_matches[start]
                matched_patterns.append({
                    'text': ent.text,
                    'entity_detected': [{
                        'type': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'score': 0.95
                    }]
                })
            if start in regex_matches:
                pattern_id, entity, start, end = regex_matches[start]
                matched_patterns.append({
                    'text': entity,
                    'entity_detected': [{
                        'type': pattern_id,
                        'start': start,
                        'end': end,
                        'score': round(random.uniform(0.8, 1.0), 2)
                    }]
                })

        return matched_patterns

    async def scan_async(self, data: str, region: str) -> List[Dict[str, Union[str, List[Dict[str, Union[str, int, float]]]]]]:
        """
        Asynchronously processes large text by splitting it into chunks and processing each chunk in parallel.
        """
        nlp_engine, matcher = self._initialize(region)
        start_time = time.time()

        text_chunks = self._chunk_text(data)
        chunk_tasks = [asyncio.create_task(self._scan_text_async(chunk, nlp_engine, matcher)) for chunk in text_chunks]
        chunk_results = await asyncio.gather(*chunk_tasks)

        final_results = [item for sublist in chunk_results for item in sublist]

        validation_tasks = [
            asyncio.create_task(validate_entity_check_digit(entity["text"], entity["entity_detected"][0]["type"], region))
            for entity in final_results if entity.get("entity_detected")
        ]

        validation_results = await asyncio.gather(*validation_tasks)

        for entity, validation_result in zip(final_results, validation_results):
            entity["validated"] = {
                "entity_detected": entity.get("entity_detected", []),
                "check_digit": validation_result.get("check_digit", False)
            }

        self.logger.info(f"Processing completed in {time.time() - start_time:.2f} seconds.")
        return final_results
