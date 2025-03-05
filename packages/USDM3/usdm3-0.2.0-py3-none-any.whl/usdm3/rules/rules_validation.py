import inspect
import importlib
import sys
import traceback
from pathlib import Path
from typing import List, Type
from usdm3.rules.library.rule_template import RuleTemplate
from usdm3.data_store.data_store import DataStore, DecompositionError
from usdm3.ct.cdisc.library import Library
from usdm3.rules.rules_validation_results import RulesValidationResults
from usdm3.base.singleton import Singleton


class RulesValidation(metaclass=Singleton):
    def __init__(self, library_path: str, package_name: str):
        self.library_path = Path(library_path)
        self.package_name = package_name
        # print(f"library_path: {self.library_path}, {self.package_name}")
        self.rules: List[Type[RuleTemplate]] = []
        self._load_rules()

    def validate_rules(self, filename: str) -> RulesValidationResults:
        data_store, e = self._data_store(filename)
        if data_store:
            ct = Library()
            ct.load()
            config = {"data": data_store, "ct": ct}
            results = self._execute_rules(config)
        else:
            results = RulesValidationResults()
            results.add_exception("Decomposition", e)
        return results

    def _data_store(self, filename: str) -> DataStore:
        try:
            data_store = DataStore(filename)
            data_store.decompose()
            return data_store, None
        except DecompositionError as e:
            return None, e

    def _load_rules(self) -> None:
        # Iterate through all .py files in the library directory
        for file in self.library_path.glob("rule_*.py"):
            # print(f"file: {file}")
            if file.name.startswith("rule_ddf") and file.name.endswith(".py"):
                try:
                    # Create module name from file name
                    module_name = f"{self.package_name}.{file.stem}"

                    # Load module using absolute path
                    spec = importlib.util.spec_from_file_location(
                        module_name, str(file)
                    )
                    if spec is None or spec.loader is None:
                        continue

                    # print(f"SPEC: {spec}")
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        # print(f"INSPECT")
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, RuleTemplate)
                            and obj != RuleTemplate
                        ):
                            try:
                                self.rules.append(obj)
                                # print(f"LOADED: {obj}")
                            except Exception:
                                # print(f"FAILED: {str(e)}")
                                continue

                except Exception as e:
                    print(f"FAILED: {str(e)}")
                    continue

    def _execute_rules(self, config: dict) -> RulesValidationResults:
        results = RulesValidationResults()
        for rule_class in self.rules:
            try:
                # Execute the rule
                rule: RuleTemplate = rule_class()
                passed = rule.validate(config)
                print(f"RULE: {rule._rule}, {passed}")
                if passed:
                    results.add_success(rule._rule)
                else:
                    results.add_failure(rule._rule, rule.errors())
            except NotImplementedError:
                # Rule not implemented yet
                results.add_not_implemented(rule._rule)
            except Exception as e:
                print(f"RULE: {rule._rule} exception: {e}")
                print(traceback.format_exc())
                results.add_exception(rule._rule, e)
        return results
