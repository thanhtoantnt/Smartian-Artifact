/*
 * @source: ChainSecurity
 * @author: Anton Permenev
 * @vulnerable_at_lines: 12
 */
pragma solidity ^0.4.19;

contract RuntimeUserInputCall{

    function check(address b){
        // <yes> <report> ASSERTION_FAILURE
        assert(B(b).foo() == 10);
    }

}

contract B{
    function foo() returns(uint);
}
