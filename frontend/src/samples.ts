export const SAMPLE_VULNERABLE_CONTRACT = `// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABILITY: reentrancy — sends ETH before updating balance
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");

        // BUG: External call BEFORE state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] = 0; // Too late — attacker already re-entered
    }

    // VULNERABILITY: anyone can drain the vault
    function emergencyDrain() public {
        payable(msg.sender).transfer(address(this).balance);
    }

    // VULNERABILITY: tx.origin authentication
    function adminAction() public {
        require(tx.origin == address(0xDEAD), "Not admin");
        selfdestruct(payable(msg.sender));
    }
}`;

export const SAMPLE_PR_URL = "https://github.com/expressjs/express/pull/5703";
