import os
import pathlib
from usdm3.rules.rules_validation import RulesValidation
from usdm3.rules.rules_validation_results import RulesValidationResults


class USDM3:
    def validate(self, file_path: str) -> RulesValidationResults:
        validator = RulesValidation(self._library_path(), "usdm3.rules.library")
        return validator.validate_rules(file_path)

    def _library_path(self) -> str:
        root = pathlib.Path(__file__).parent.resolve()
        return os.path.join(root, "rules/library")
