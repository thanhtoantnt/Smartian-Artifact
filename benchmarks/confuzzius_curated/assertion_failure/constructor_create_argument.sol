/*
 * @source: ChainSecurity
 * @author: Anton Permenev
 * @vulnerable_at_lines: 13
 */
pragma solidity ^0.4.22;

contract ConstructorCreateArgument{
    B b = new B(11);

    function check(){
        // <yes> <report> ASSERTION_FAILURE
        assert(b.foo() == 10);
    }

}

contract B{

    uint x_;
    constructor(uint x){
        x_ = x;
    }

    function foo() returns(uint){
        return x_;
    }
}
