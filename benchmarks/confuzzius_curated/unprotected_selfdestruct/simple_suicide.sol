pragma solidity ^0.4.22;

contract SimpleSuicide {

  function sudicideAnyone() {
    // <yes> <report> UNPROTECTED_SELFDESTRUCT
    selfdestruct(msg.sender);
  }

}
