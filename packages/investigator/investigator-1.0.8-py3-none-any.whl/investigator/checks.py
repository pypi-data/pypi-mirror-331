from dataclasses import dataclass
import inspect
from typing import Any


_checks = {"github_repo": {}, "test2": {}, "test3": {}}


def _get_parameters(function):
    return [
        parameter.name
        for parameter in inspect.signature(function).parameters.values()
        if parameter.kind == parameter.POSITIONAL_OR_KEYWORD
    ]


def register_check(check, codes=None):
    """Register a new check object."""

    def _add_check(check, kind, codes, args):
        if check in _checks[kind]:
            _checks[kind][check][0].extend(codes or [])
        else:
            _checks[kind][check] = (codes or [""], args)

    if inspect.isfunction(check):
        args = _get_parameters(check)
        if args and args[0] in ("github_repo", "test2"):
            if codes is None:
                codes = ERRORCODE_REGEX.findall(check.__doc__ or "")
            _add_check(check, args[0], codes, args)
    elif inspect.isclass(check):
        if _get_parameters(check.__init__)[:2] == ["self", "tree"]:
            _add_check(check, "tree", codes, None)
    return check


########################################################################
# Plugins (check functions) for physical lines
########################################################################


@register_check
def tabs_or_spaces(github_repo, indent_char):
    r"""Never mix tabs and spaces.

    The most popular way of indenting Python is with spaces only.  The
    second-most popular way is with tabs only.  Code indented with a
    mixture of tabs and spaces should be converted to using spaces
    exclusively.  When invoking the Python command line interpreter with
    the -t option, it issues warnings about code that illegally mixes
    tabs and spaces.  When using -tt these warnings become errors.
    These options are highly recommended!

    Okay: if a == 0:\n    a = 1\n    b = 1
    """
    indent = INDENT_REGEX.match(physical_line).group(1)
    for offset, char in enumerate(indent):
        if char != indent_char:
            return offset, "E101 indentation contains mixed spaces and tabs"


@dataclass
class GithubPoliciesObject:
    default_branch_protection: bool
    default_branch_requires_approving_reviews: bool


def github_policies(repository: GithubPoliciesObject):
    """Validates a parsed GitHub repository against these policies

    :return: Policy with results
    """

    def policy01(repo):
        return repo.default_branch_protection is not None

    def policy02(repo):
        if repo.default_branch_protection is not None:
            return repo.default_branch_requires_approving_reviews
        return False

    return [
        Policy(
            "policy01",
            "main_branch_protection",
            "Branch protection rule for default branch must be enabled",
            policy01(repository),
        ),
        Policy(
            "policy02",
            "pull_request_review_before_merge",
            "Pull request reviews before merge are required",
            policy02(repository),
        ),
    ]


@dataclass
class Policy:
    policy_id: str
    name: str
    description: str
    compliant: bool

    def in_violation(self):
        return not self.compliant


class ResultSet:
    def __init__(self, reference: dict[Any]):
        self.reference = reference
        self.__results = []
        self.__exclusions = []

    def add_results(self, results: list[Policy]):
        self.__results += results

    def add_exclusions(self, exclusions):
        self.__exclusions += [exclusion.casefold() for exclusion in exclusions]

    def results(self) -> list[Policy]:
        return list(
            filter(
                lambda p: p.policy_id.casefold() not in self.__exclusions,
                self.__results,
            )
        )

    def policy_violations(self) -> list[Policy]:
        return list(filter(lambda p: p.in_violation() is True, self.results()))
