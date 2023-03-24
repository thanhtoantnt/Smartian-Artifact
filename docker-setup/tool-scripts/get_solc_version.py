# Standard Library
import os
import sys
from typing import List, Union
from dataclasses import dataclass
import nodesemver
import semantic_version

from lark import Lark, Transformer, ast_utils, v_args

########################################
# Some constants

PARSER_DIR = os.path.dirname(__file__)
THIS_MODULE = sys.modules[__name__]

########################################
# Source code and AST


@dataclass
class AST(ast_utils.Ast):
    """Empty class represent an AST node"""


@dataclass
class SolidityPragma(AST):
    """Class representing a `pragma` version.

    This class corresponds to the rule `solidity_grammar` when
    `ast_utils.create_transformer(this_module, ...)` is called.
    """

    version: str


@dataclass
class SourceUnit(AST):
    """Class representing a source unit.

    This class corresponds to the rule `source_unit` when
    `ast_utils.create_transformer(this_module, ...)`.
    """

    solidity_pragmas: List[SolidityPragma]


########################################
# Other transformer to generate AST


class ASTTransformer(Transformer):
    """Class to define extra rules to transform the parsed tree to AST.

    These rules are the rules that do not correspond to any dataclass defined
    above.
    """

    @v_args(inline=True)
    def source_unit(self, *elements):
        """Parse rule `source_unit`"""
        pragmas = [elem for elem in elements if elem is not None]
        return SourceUnit(pragmas)

    @v_args(inline=True)
    def solidity_pragma(self, version) -> SolidityPragma:
        """Parse rule `solidity_pragma`"""
        return SolidityPragma(version)

    @v_args(inline=True)
    def pragma_version_info(self, version) -> str:
        """Parse rule `pragma_version_info`"""
        version = str(version)
        return version.strip()

    # @v_args(inline=True)
    def non_solidity_pragma(self, non_solidity_pragma):
        """Parse rule `non_solidity_pragma`"""
        # Do not capture `non-solidity-pragma` elements
        return None


########################################
# Parse Solidity `pragma`

# Initialize grammar and parser
grammar_file = os.path.join(PARSER_DIR, "pragma_grammar.lark")
with open(grammar_file, "r", encoding="utf-8") as file:
    grammar = file.read()
parser = Lark(grammar, start="source_unit")

def init_all_solidity_versions() -> List[str]:
    """Enumerate all Solidity versions.

    All Solidity releases: https://blog.soliditylang.org/category/releases/"""

    solidity_0_4 = ["0.4.%d" % i for i in range(27)]  # 0.4.0 --> 0.4.26
    solidity_0_5 = ["0.5.%d" % i for i in range(18)]  # 0.5.0 --> 0.5.17
    solidity_0_6 = ["0.6.%d" % i for i in range(13)]  # 0.6.0 --> 0.6.12
    solidity_0_7 = ["0.7.%d" % i for i in range(7)]  # 0.7.0 --> 0.7.6
    solidity_0_8 = ["0.8.%d" % i for i in range(20)]  # 0.8.0 --> 0.8.19

    all_versions = (
        solidity_0_4 + solidity_0_5 + solidity_0_6 + solidity_0_7 + solidity_0_8
    )

    return all_versions

def find_best_solc_version_for_pragma(pragma_versions) -> Union[str, None]:
    """Find the best version of Solc compiler for a pragma version."""
    all_versions = init_all_solidity_versions()
    constraint = " ".join(pragma_versions)
    try:
        # Use `semantic_version` to find the best version first
        all_semvers = [semantic_version.Version(v) for v in all_versions]
        version_spec = semantic_version.NpmSpec(constraint)
        best_version = version_spec.select(all_semvers)
        return str(best_version)
    except ValueError:
        # If errors occur, use `node_semver` to find the best version
        best_version = nodesemver.max_satisfying(all_versions, constraint)
        return str(best_version)

def parse_solidity_version_from_content(content):
    """Parse `pragma` string in a Solidity source code string."""
    parsed_tree = parser.parse(content)
    source_unit = ASTTransformer().transform(parsed_tree)
    return [pragma.version for pragma in source_unit.solidity_pragmas]

def parse_solidity_version(input_file):
    """Parse `pragma` string in a Solidity source code file."""
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()
    return parse_solidity_version_from_content(content)

def find_best_solc_version(input_file) -> Union[str, None]:
    """Find the best version of Solc compiler for a smart contract."""
    pragma_versions = parse_solidity_version(input_file)
    return find_best_solc_version_for_pragma(pragma_versions)

test_file = sys.argv[1]
version = find_best_solc_version(test_file)
print(version)
