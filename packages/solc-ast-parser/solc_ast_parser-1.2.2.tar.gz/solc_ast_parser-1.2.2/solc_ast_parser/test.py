import json
from os import listdir
import os
# from solc_ast_parser.enrichment import restore_ast
from solc_ast_parser.enrichment import restore_storages
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.ast_parser import parse_ast_to_solidity
from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.utils import compile_contract_with_standart_input, update_node_fields
from solc_ast_parser.comments import insert_comments_into_ast
from solc_ast_parser.utils import create_ast_from_source, create_ast_with_standart_input
from solcx.exceptions import SolcError

def create_contract(pseudocode: str) -> str:
    return f"// SPDX-License-Identifier: MIT\npragma solidity ^0.8.28;\ncontract PseudoContract {{\n\n{pseudocode}\n}}"

# ast = create_ast_with_standart_input(vuln_template)
# path = "../../../pycryptor/data/"
# vuln_files = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith("userx-")]
path = "./"
vuln_files = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".sol")]
success = 0

# for file in vuln_files:
#     with open(os.path.join(path, file), "r") as f:
vuln_template = create_contract("""
// Unguarded function
mapping(address => bool) isCapsule;
mapping(address => mapping(uint256 => address)) private capsuleCollection;
mapping(address => uint256) private capsuleOwnershipCount;

event CapsuleOwnerUpdated(address indexed capsule, address indexed previousOwner, address indexed newOwner);

function updateCapsuleCollectionOwner(address _previousOwner, address _newOwner) external {
    address _capsule = _msgSender();
    require(isCapsule[_capsule], "NOT_CAPSULE");
    require(removeCapsule(_previousOwner, _capsule), "ADDRESS_DOES_NOT_EXIST");
    require(addCapsule(_newOwner, _capsule), "ADDRESS_ALREADY_EXIST");
    emit CapsuleOwnerUpdated(_capsule, _previousOwner, _newOwner);
}

function _msgSender() internal view returns (address) {
    return msg.sender;
}

function addCapsule(address owner, address capsule) private returns (bool) {
    if (!isCapsule[capsule]) {
        return false;
    }
    capsuleCollection[owner][capsuleOwnershipCount[owner]] = capsule;
    capsuleOwnershipCount[owner]++;
    return true;
}

function removeCapsule(address owner, address capsule) private returns (bool) {
    for (uint256 i = 0; i < capsuleOwnershipCount[owner]; i++) {
        if (capsuleCollection[owner][i] == capsule) {
            capsuleCollection[owner][i] = capsuleCollection[owner][capsuleOwnershipCount[owner] - 1];
            delete capsuleCollection[owner][capsuleOwnershipCount[owner] - 1];
            capsuleOwnershipCount[owner]--;
            return true;
        }
    }
    return false;
}

                                """)
ast = create_ast_with_standart_input(vuln_template)
# ast = SourceUnit(**ast)
# update_node_fields(ast, {"node_type": [NodeType.VARIABLE_DECLARATION.value, NodeType.IDENTIFIER.value], "name": "lpToken"}, {"name": "<|random:collateralId|collId|id>"})
# update_node_fields(ast, {"node_type": [NodeType.FUNCTION_DEFINITION.value, NodeType.IDENTIFIER.value], "name": "addLPToken"}, {"name": "<|random:tokenExists|exists|check>"})
with open("contract.json", "w+") as f:
    f.write(ast.model_dump_json())

# new_ast = restore_ast(ast)
new_ast = ast
with open("new_contract.json", "w+") as f:
    f.write(json.dumps(new_ast.model_dump(), indent=4))
code = insert_comments_into_ast(vuln_template, new_ast)
new_ast = restore_storages(new_ast)
code = parse_ast_to_solidity(new_ast)
with open("new_contract.sol", "w+") as f:
    f.write(code)
ast = create_ast_from_source(code)
# parse_ast_to_solidity(new_ast)
success += 1
# print(f"Success: {success}/{len(vuln_files)}")

# VALIDATOR INFO + TIME + STATUS