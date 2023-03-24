/*
 * @source: TrailofBits workshop at TruffleCon 2018
 * @author: Josselin Feist (adapted for SWC by Bernhard Mueller)
 * @vulnerable_at_lines: 30
 * Assert violation with 3 message calls:
 * - airdrop()
 * - backdoor()
 * - test_invariants()
 */
pragma solidity ^0.4.22;

contract Token{

    mapping(address => uint) public balances;
    function airdrop() public{
        balances[msg.sender] = 1000;
    }

    function consume() public{
        require(balances[msg.sender]>0);
        balances[msg.sender] -= 1;
    }

    function backdoor() public{
        balances[msg.sender] += 1;
    }

   function test_invariants() {
      // <yes> <report> ASSERTION_FAILURE
      assert(balances[msg.sender] <= 1000);
  }
}
