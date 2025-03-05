from d4k_sel.error_location import ErrorLocation
from d4k_sel.errors import Errors


class ValidationLocation(ErrorLocation):
    def __init__(
        self, rule: str, rule_text: str, klass: str, attribute: str, path: str
    ):
        self.rule = rule
        self.rule_text = rule_text
        self.klass = klass
        self.attribute = attribute
        self.path = path

    def to_dict(self):
        return {
            "rule": self.rule,
            "rule_text": self.rule_text,
            "klass": self.klass,
            "attribute": self.attribute,
            "path": self.path,
        }

    @classmethod
    def headers(self):
        return ["rule", "rule_text", "klass", "attribute", "path"]

    def __str__(self):
        return f"{self.rule} [{self.rule_text}]: {self.klass}.{self.attribute} at {self.path}"


class RuleTemplate:
    """
    Base class for rule templates
    """

    ERROR = Errors.ERROR
    WARNING = Errors.WARNING

    def __init__(self, rule: str, level: int, rule_text: str):
        self._errors = Errors()
        self._rule = rule
        self._level = level
        self._rule_text = rule_text

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")

    def errors(self) -> Errors:
        return self._errors

    def _add_failure(self, message: str, klass: str, attribute: str, path: str):
        location = ValidationLocation(
            self._rule, self._rule_text, klass, attribute, path
        )
        self._errors.add(message, location, self._level)

    def _result(self) -> bool:
        return self._errors.count() == 0

    def _ct_check(self, config: dict, klass: str, attribute: str) -> bool:
        data = config["data"]
        ct = config["ct"]
        items = data.instances_by_klass(klass)
        codelist = ct.klass_and_attribute(klass, attribute)
        codes, decodes = self._codes_and_decodes(codelist)
        print(codes, decodes)
        for item in items:
            if attribute in item:
                code = item[attribute]["code"]
                decode = item[attribute]["decode"]
                code_index = self._find_index(codes, code)
                decode_index = self._find_index(decodes, decode)
                if code_index is None and decode_index is not None:
                    self._add_failure(
                        f"Invalid code '{code}', the code is not in the codelist",
                        klass,
                        attribute,
                        data.path_by_id(item["id"]),
                    )
                elif code_index is not None and decode_index is None:
                    self._add_failure(
                        f"Invalid decode '{decode}', the decode is not in the codelist",
                        klass,
                        attribute,
                        data.path_by_id(item["id"]),
                    )
                elif code_index is None and decode_index is None:
                    self._add_failure(
                        f"Invalid code and decode '{code}' and '{decode}', neither the code and decode are in the codelist",
                        klass,
                        attribute,
                        data.path_by_id(item["id"]),
                    )
                elif code_index != decode_index:
                    self._add_failure(
                        f"Invalid code and decode pair '{code}' and '{decode}', the code and decode do not match",
                        klass,
                        attribute,
                        data.path_by_id(item["id"]),
                    )
            else:
                self._add_failure(
                    "Missing attribute", klass, attribute, data.path_by_id(item["id"])
                )
        return self._result()

    def _codes_and_decodes(self, codelist: dict) -> tuple[list[str], list[str]]:
        if "terms" not in codelist:
            return [], []
        codes = [x["code"] for x in codelist["terms"]]
        decodes = [x["decode"] for x in codelist["terms"]]
        return codes, decodes

    def _find_index(self, items: list[str], value: str) -> int | None:
        try:
            return items.index(value)
        except ValueError:
            return None
