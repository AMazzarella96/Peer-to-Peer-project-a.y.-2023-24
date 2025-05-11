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


**Data structures**

The logic of the smart contract rotates around three main structures:
- Match: a struct representing an idle/ongoing match composed of:
- Accuse: a boolean flag used within the accusation phase during a match
- Curr_block_num: the number of the current block saved whenever an accuse is issued, used to check the 5 blocks time limit
- Accuser: the address of the accuser (either Player_1 or Player_2)
- Full: for distinguishing among idle and ongoing matches
- Size: the size of the board
- Turn: represents the current turn of the player (-1 for player_1, 1 for player_2)
- Player_1: the address of the player 1
- Board_2: the Merkle root hash of the player_1’s board
- Player_2: the address of the player 2
- Board_2: the Merkle root hash of the player_1’s board
- Ships_1: number of remaining ships on the player_1’s board
- Ships_2: number of remaining ships on the player_2's board
- Total_ships: total number of ships of a match
- Reward: winner prize
- Games: a mapping <id, match> that stores all the pending/ongoing matches
- Games_index: an auxiliary array that stores the ids of pending/ongoing matches, used for iterating over games.

**Events**

The smart contract provides several events used for managing the different phases of the match:
- BattleshipsCreated: emitted on contract creation; returns the contract address
- newMatch: emitted as soon a new game has been created which returns the match id to the issuer
- size_ID: emitted in the joining phase when the issuer does not know the match id; returns the board size and the id
- size_only: emitted in the joining phase when the issuer knows the match id; returns the board size
- match_ready: emitted as soon the player 2 uploads its board leading to the bidding phase; returns the id
- noMatches: emitted in case the specified id does not correspond to any current match or there is no available match
- Turn_played: emitted as soon the current player make its move; returns the id, row and column
- Turn_response: emitted when the other player specifies Hit or Miss after receiving the coordinates, after the proof verification goes well; returns id and the response
- Your_turn: emitted the first time in the bidding phase after the second bet placement for starting the game, and then it is emitted at each turn-response interaction
- Match_ended: emitted when the match ends correctly or whenever something bad happens; returns: 0 - a player wins but its board must be checked, 1 – board check is ok, the player won, -1 – cheating attempt, -2 - inactivity
- Bid_placed: emitted in the bidding phase regulating the two-way bet; returns: 1 – the first bet has been placed but the second is still missing, 2 - the second bet has been placed and the match can start
- Accuse: emitted whenever a player accuses the opponent of inactivity

**Functions**
The smart contract provides the following functions:
- Create_match: called whenever a player creates a new match, specifying the size of the board, the total number of ships and the root hash of its board. This call will create a new match inside the games mapping, setting the appropriate parameters as the ones passed by the player (which will be considered as player_1) and setting to null all the information related to player_2
- join_match_id: called by a player who wants to join an existing match and already knows the id. The function will emit size_only specifying the size of the board
- join_match: called by a player who wants to join an existing match but does not know the id
already, so the contract iterates over the games mapping (through games_index) looking for a
pending match. Once found, it emits the event size_ID specifying both the board size and the match
id
- upload_board: called as soon as a player has joined a match, uploading its board’s root hash within
the contract, setting the full flag of the match, and saving the player address as player_2
- bet: called once all the parameters have been uploaded, used for transferring the agreed amount to
the smart contract emitting bid_placed(1) in case of only one bet has been placed, bid_placed(2) as
soon as the second bet has been placed (and then also your_turn is emitted) or match_ended(-1) in
case the bets are not the same, sending a refund to both players

