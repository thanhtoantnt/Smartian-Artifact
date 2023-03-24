/*
 * @source: ChainSecurity
 * @author: Anton Permenev
 * @vulnerable_at_lines: 15
 */
pragma solidity ^0.4.21;

contract GasModel{
    uint x = 100;
    function check(){
        uint a = gasleft();
        x = x + 1;
        uint b = gasleft();
        // <yes> <report> ASSERTION_FAILURE
        assert(b > a);
    }
}
