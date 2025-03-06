from huggingface_hub import hf_hub_download
from transformers import Pipeline, AutoModelForSequenceClassification, AutoTokenizer
from transformers.pipelines import PIPELINE_REGISTRY, SUPPORTED_TASKS
from typing import List, Dict, Union, Optional, Tuple
import unicodedata
from huggingface_hub import hf_hub_download
from pybloomfilter import BloomFilter
import unicodedata
from typing import Optional
from huggingface_hub import hf_hub_download
from pybloomfilter import BloomFilter

from glebs_package.langident.langident_pipeline import LangIdentPipeline




def get_bloomfilter(model_id: str, filename: str):
        return BloomFilter.open(hf_hub_download(repo_id=model_id, filename=filename))

class OCRQAPipeline:   
    def __init__(self):
        pass

    def __call__(self, text, language = None, version = "1.0.6", diagnostics = False):
        self.language = language
        self.version = version
        self.diagnostics = diagnostics
        
        if self.language == None:
            # exec(open(hf_hub_download("Maslionok/sudo_pipelines", "floret_language_recognition.py")).read())

            lang_model = LangIdentPipeline()

            self.language = lang_model(text)

        if self.language not in self.SUPPORTED_LANGUAGES:
          raise ValueError(f"Unsupported language: {self.language}")
        
        bf = get_bloomfilter("impresso-project/OCR-quality-assessment-unigram", f"ocrqa-wp_v{self.version}-{self.language}.bloom")

        output = self.filter_text(text, bf)

        return output
    
    # Add all supported languages here
    SUPPORTED_LANGUAGES = {
        "fr", 
        "de"
    }

    
    # Define normalization table
    QUOTES_PUNCT = "„•<>!\"#%&'’"
    ASCII_PUNCT = "()*,./:;?"
    BRACKETS_SPECIAL = "[]\\~_{}"
    UNICODE_PUNCT = "\xa1\xab\xb7\xbb\xbf"
    DASH_CARET = "—^`"
    SPECIAL_SYMBOLS = "¦§£="
    HYPHEN = "-"
    DIGITS = "0123456789"

    NORMALIZATION_TABLE = str.maketrans(
        {
            char: " "
            for char in (
                QUOTES_PUNCT
                + ASCII_PUNCT
                + BRACKETS_SPECIAL
                + UNICODE_PUNCT
                + DASH_CARET
                + SPECIAL_SYMBOLS
                + HYPHEN
            )
        }
        | {char: "0" for char in DIGITS}
    )


    def normalize_text(self, s: str, unicode_normalize: Optional[str] = "NFKC") -> str:
        """Normalize text by replacing punctuation with spaces and digits with '0'."""
        if unicode_normalize:
            s = unicodedata.normalize(unicode_normalize, s).lower()
        return s.translate(self.NORMALIZATION_TABLE)


    def filter(self, text: str, bloom_filter: BloomFilter):
        # Normalize and tokenize text
        normalized_text = self.normalize_text(text)
        tokens = normalized_text.split()

        # Check tokens against the bloom filter
        for token in tokens:
            if self.diagnostics:
                if token in bloom_filter:
                    print(f"'{token}' is in the bloom filter.")
                else:
                    print(f"'{token}' is NOT in the bloom filter.")


    def filter_text(self, DE_TEXT: str, bloom_filter: BloomFilter):

        knowns = set()
        unknowns = set()

        # Normalize and tokenize text
        normalized_text = self.normalize_text(DE_TEXT)
        tokens = normalized_text.split()

        # Check tokens against the bloom filter
        for token in tokens:
            if token in bloom_filter:
                # if self.diagnostics:
                #     print(f"'{token}' is in the bloom filter.")
                knowns.add(token)
            else:
                # if self.diagnostics:
                #     print(f"'{token}' is NOT in the bloom filter.")
                unknowns.add(token)
        
        # result = {"knowns": knowns, "unknowns": unknowns}

        bloom_filter = f"ocrqa-wp_v{self.version}-{self.language}.bloom"

        # Compute the score
        score = len(knowns) / (len(knowns) + len(unknowns)) if (len(knowns) + len(unknowns)) > 0 else 0
        score = round(score, 1)
        
        output = ({"language": self.language, "score": score})
        
        if self.diagnostics:
            output = ({"language": self.language, "score": score, "diagnostics": {"known_tokens": list(knowns), "unknowns_tokens": list(unknowns), "bloom_filter": bloom_filter}})

        return output
