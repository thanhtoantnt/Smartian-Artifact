/*
 * @source: https://swcregistry.io/docs/SWC-105
 * @author: SWC Registry
 * @vulnerable_at_lines: 13
 */

pragma solidity ^0.4.22;

contract SimpleEtherDrain {

  function withdrawAllAnyone() {
    // <yes> <report> LEAKING_ETHER
    msg.sender.transfer(this.balance);
  }

  function () public payable {
  }

}
