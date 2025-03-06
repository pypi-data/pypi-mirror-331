from baseTest import BaseTestCase
from jstreams.ioc import StrVariable, injector, resolveDependencies, resolveVariables


@resolveVariables(
    {
        "label": StrVariable("label"),
    }
)
class MockWithVariables:
    label: str

    def __init__(self, value: int) -> None:
        self.value = value

    def printValues(self) -> str:
        return self.label + str(self.value)


@resolveDependencies(
    {
        "label": str,
    }
)
class MockWithDependencies:
    label: str

    def __init__(self, value: int) -> None:
        self.value = value

    def printValues(self) -> str:
        return self.label + str(self.value)


@resolveDependencies(
    {
        "label1": str,
    }
)
@resolveVariables(
    {
        "label2": StrVariable("label"),
    }
)
class MockWithDependenciesAndVariables:
    label1: str
    label2: str

    def __init__(self, value: int) -> None:
        self.value = value

    def printValues(self) -> str:
        return self.label1 + str(self.value) + self.label2


class TestComplexIoc(BaseTestCase):
    def test_resolve_variables(self) -> None:
        injector().provideVar(str, "label", "labelValue")
        mock = MockWithVariables(12)
        self.assertEqual(mock.printValues(), "labelValue12")

    def test_resolve_dependency(self) -> None:
        injector().provide(str, "labelValue")
        mock = MockWithDependencies(10)
        self.assertEqual(mock.printValues(), "labelValue10")

    def test_resolve_variables_and_dependencies(self) -> None:
        injector().provideVar(str, "label", "labelValueVar")
        injector().provide(str, "labelValueDep")
        mock = MockWithDependenciesAndVariables(7)
        self.assertEqual(mock.printValues(), "labelValueDep7labelValueVar")
