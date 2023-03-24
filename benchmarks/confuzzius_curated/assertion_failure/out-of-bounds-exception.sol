/*
 * @source: Unknown
 * @author: Unknown
 * @vulnerable_at_lines: 14
 */
pragma solidity ^0.4.25;

contract OutOfBoundsException {

	uint256[] private array;

	function getArrayElement(uint256 idx) public returns (uint256) {
		// <yes> <report> ASSERTION_FAILURE
		return array[idx];
	}

}
