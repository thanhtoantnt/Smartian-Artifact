/*
 * @source: https://github.com/ConsenSys/evm-analyzer-benchmark-suite
 * @author: Suhabe Bugrara
 * @vulnerable_at_lines: 12
 */

pragma solidity ^0.4.19;

contract AssertConstructor {
    function AssertConstructor() public {
        // <yes> <report> ASSERTION_FAILURE
        assert(false);
    }
}
