# Peer-to-Peer-project-a.y.-2023-24

This project is a Proof of Concept of a possible implementation of the game Battleships developed on the
Ethereum blockchain, with the purpose of solving the problems derived from the standard centralized
implementation of the game. In particular, in a centralized server scenario, the players must rely on the
information coming from the server (which acts as a mediator), and if it is not trusted, it may decide to send
wrong information to the players; the problem aggravates if the game involves a reward for the winner.
The aim of this project was to implement a decentralized version of the game on the Ethereum blockchain
taking advantage of all its security properties: tamper-freeness, auditing, instant and secure payments and
so on, without the need of a central authority.

## System architecture
The system provides functionality for creating a new match and joining an existing one, and in both cases each player places the ships on the board (locally), computes the Merkle hash root of the board and send it to the match within the smart contract. Once the boards have been uploaded, the players make a joint decision on the amount of value to commit to the game, corresponding to the winning prize (amount * 2). As soon as both the bet have been placed (must be equal) the match starts, and both players (once per turn) make their guesses on the opponents’ board launching torpedoes and replying with “hit” or “miss”; the system checks that every response is legitimate, otherwise the match will end, and the cheater will lose the match. The game ends as soon as one player manages to sink all the opponents’ ships, gaining the prize. At any point of the match a player can accuse the opponent of inactivity and if the accuse is not addressed
within 5 blocks interval, the player can claim the match reward. 

The system is composed of two elements:
- A smart contract Battleships.sol (implemented in Solidity) that implements the game logic
- A front-end module board.py (implemented in Python) that offers all the functions and utilities to interact with the deployed smart contract and play the game

### Battleships.sol
The Battleship smart contract constitutes the core of the system managing all the different steps of the
game. Its structure can be analyzed in three sections: Data structures, Events and Functions.


### Data structures

The logic of the smart contract rotates around three main structures:
▪ Match: a struct representing an idle/ongoing match composed of:
▪ Accuse: a boolean flag used within the accusation phase during a match
▪ Curr_block_num: the number of the current block saved whenever an accuse is issued, used
to check the 5 blocks time limit
▪ Accuser: the address of the accuser (either Player_1 or Player_2)
▪ Full: for distinguishing among idle and ongoing matches
▪ Size: the size of the board
▪ Turn: represents the current turn of the player (-1 for player_1, 1 for player_2)
▪ Player_1: the address of the player 1
▪ Board_2: the Merkle root hash of the player_1’s board
▪ Player_2: the address of the player 2
▪ Board_2: the Merkle root hash of the player_1’s board
▪ Ships_1: number of remaining ships on the player_1’s board
▪ Ships_2: number of remaining ships on the player_2's board
▪ Total_ships: total number of ships of a match
▪ Reward: winner prize
▪ Games: a mapping <id, match> that stores all the pending/ongoing matches
▪ Games_index: an auxiliary array that stores the ids of pending/ongoing matches, used for iterating
over games.
