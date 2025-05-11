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
- play_turn: called by the current player specifying a coordinate <row, column> and will emit the
event turn_played, catched by the opponent for retrieving the torpedo coordinates
- check_move: called by the opponent after a turn played, checks whether the opponent’s response
is legitimate through a proof verification using the provided proof, the value (1 or 0 – Hit or Miss),
the index and the root hash uploaded within the match. If the verification goes well, there are two
cases: 1) the opponent has no remaining ships and the current player wins (emit match_ended(0)
for board verification), 2) will be emitted your_turn for the turn change. If the opponent tries to
cheat, it will be emitted a match_ended(-1) sending the reward to the current player
- check_board: called when a player wins a match, checks whether the ships on the board were
correctly placed, by checking that the provided board (in clear) contains a number of ships equal to
total_ships. If the check goes well, it will be emitted a match_ended (1) sending the reward to the
winner, otherwise it will be emitted a match_ended (-1) sending the reward to the opponent
- accuse_player: called whenever a player has the suspect that the opponent left the game, saving
the current block number and emitting the event accuse
- accuse_response: called whenever the opponent accused the current player of inactivity to address
the accuse, resetting all the accuse parameters
- withdraw: called in case of inactivity accuse after the 5 blocks delay. Once the time has passed, the
accuser is declared a winner and will be able to claim the entire reward.
- Remove_match: called whenever a match has to be deleted from the list of matches, reorganizing
other elements to remove eventual gaps

### Board.py

The front-end part of the system offers the player a set of functions allowing the players to interact with the
deployed smart contract. There are some utility functions and main functions.
The main functions are:
- create_board: create an empty data frame representing the board and based on the dimensions
calls the function fill_board with the predetermined number/type of ships. Once the board is filled,
the root hash is computed through a call to the merkle_tree function
- fill_board: for each ship checks whether the provided coordinates are valid (there’s enough room
for the ship, do not intersect with other ships, it is not diagonal, the distance among the
coordinates is equal to the length of the ship). Once all ships are placed, prints the resulting board
- new_match: makes a call to the smart contract invoking create_match passing the root hash, the
size of the board and the total number of ships; returns the id of the created match
- log_loop: an async function for waiting for a player to join the match and start the game. It loops
over an event filter created on the match_ready event, exiting the loop on reception
- place_bet: async function for the bet placement phase, in which the first player who puts the bet in
the smart contract waits for either bid_placed event (meaning that the opponent placed its bet
correctly) or match_ended (meaning that the bets were not as agreed)
- play_game: async function implementing the game itself looping on several event filters, one for
each event emitted during the match. For each event received, based on the actual player’s turn it
will ask for a coordinate to hit (calling the play_turn function of the smart contract) or a response
subsequent to a shot (calling the check_move function of the smart contract). After 10 seconds of
inactivity asks the waiting player if it wants to perform a liveness check on the opponent (eventually
calling the accuse_player function and saving the current last block number). At this point the front-
end code starts polling the blockchain every couple of seconds checking the last block number.
Once the difference between the previously saved block number and the polled one is greater or
equals to 5, the player will automatically win the match and it will be able to call the withdraw
function of the smart contract, claiming the reward

The utility functions are:

- df_toArray: converts a Pandas DataFrame into a python int array
- readContractData: retrieve the json object of the contract
- print_available: in the ship placement phase prints the remaining ships to place
- merkle_tree: builds a merkle tree of the board and returns its root hash
- get_proof: provides an inclusion proof for a specified key
- print_menu_1/2/3: print front-end menus
- convert_to_wei: converts the specified amount to wei for match rewards

