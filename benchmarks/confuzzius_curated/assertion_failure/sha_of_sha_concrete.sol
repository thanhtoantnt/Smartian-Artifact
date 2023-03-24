/*
 * @source: ChainSecurity
 * @author: Anton Permenev
r * @vulnerable_at_lines: 19
 */
pragma solidity ^0.4.22;

contract ShaOfShaConcrete{

    mapping(bytes32=>uint) m;
    uint b;

    constructor(){
        b = 1;
    }

    function check(uint x){
        // <yes> <report> ASSERTION_FAILURE
        assert(m[keccak256(abi.encodePacked(x, "B"))] == 0);
    }

}
