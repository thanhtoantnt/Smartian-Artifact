/*
 * @source: Unknown
 * @author: Unknown
 * @vulnerable_at_lines: 19
 */
pragma solidity ^0.4.22;

contract TwoMappings{

    mapping(uint=>uint) m;
    mapping(uint=>uint) n;

    constructor(){
        m[10] = 100;
    }

    function check(uint a){
        // <yes> <report> ASSERTION_FAILURE
        assert(n[a] == 0);
    }

}
