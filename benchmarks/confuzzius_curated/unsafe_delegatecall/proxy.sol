pragma solidity ^0.4.24;

contract Proxy {

  address owner;

  constructor() public {
    owner = msg.sender;
  }

  function forward(address callee, bytes _data) public {
    // <yes> <report> UNSAFE_DELEGATECALL
    require(callee.delegatecall(_data));
  }

}
