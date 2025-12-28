from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class PIIScrubber:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def scrub(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return text
        
        # Analyze the text for PII
        results = self.analyzer.analyze(text=text, language='en', 
                                        entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "URL"])
        
        # Anonymize the detected PII
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "PERSON": OperatorConfig("replace", {"new_value": "[ANONYMIZED_NAME]"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[ANONYMIZED_PHONE]"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[ANONYMIZED_EMAIL]"}),
                "LOCATION": OperatorConfig("replace", {"new_value": "[ANONYMIZED_LOCATION]"}),
                "URL": OperatorConfig("replace", {"new_value": "[ANONYMIZED_URL]"}),
            }
        )
        
        return anonymized_result.text

if __name__ == "__main__":
    scrubber = PIIScrubber()
    sample_text = "Hi, my name is John Doe and my phone number is 123-456-7890. I live in Singapore near Orchard Road. My email is john.doe@example.com."
    print("Original:", sample_text)
    print("Scrubbed:", scrubber.scrub(sample_text))
