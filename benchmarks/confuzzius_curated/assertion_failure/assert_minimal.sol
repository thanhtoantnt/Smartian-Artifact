/*
 * @source: https://github.com/ConsenSys/evm-analyzer-benchmark-suite
 * @author: Suhabe Bugrara
 * @vulnerable_at_lines: 12
 */

pragma solidity ^0.4.19;

contract AssertMinimal {
    function run() public {
        // <yes> <report> ASSERTION_FAILURE
        assert(false);
    }
}
