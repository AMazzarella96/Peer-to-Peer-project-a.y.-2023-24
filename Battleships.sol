// SPDX-License-Identifier: UNLICENSED 
pragma solidity >=0.4.22 <0.9.0;

///@author Alessandro Mazzarella
///@title Battleships
///@notice Contract for Battleships matches management

contract Battleships{

    event newMatch(bytes32 id);
    event size_ID(uint8 size, bytes32 id);
    event size_only(uint8 size, bytes32 id);
    event match_ready(bytes32 id);
    event noMatches(uint res);
    event BattleshipsCreated(address addr);
    event turn_played(bytes32 id, uint row, uint col);
    event turn_response(bytes32 id, uint res);
    event your_turn(bytes32 id);
    event match_ended(bytes32 id, int outcome);
    event bid_placed(bytes32 id, int bid);
    event accuse(bytes32 id, uint256 block_num);


    ///@notice Struct representing a single match
    struct Match{
            bool accuse;                //Flag for accusation
            uint256 curr_block_num;     //Current block number
            address payable accuser;    //Accuser address
            bool full;                  //Flag for tracking full matches
            uint8 size;                 //Match board size
            int turn;                   //Regulate player turns: -1 (player_1) / 1 (player_2)
            address payable player_1;   //Player_1 address
            bytes32 board_1;            //Player_1 board Merkle root
            address payable player_2;   //Player_2 address
            bytes32 board_2;            //Player_2 board Merkle root
            uint64 ships_1;             //Player_1 current ships
            uint64 ships_2;             //Player_2 current ships
            uint64 total_ships;         //Match total ship number
            uint reward;                //Winner prize
    }

    mapping (bytes32 => Match) games;   //Dictionary ID -> Match
    bytes32[] games_index;              //Auxiliary array for iterations over mapping
    uint private len = 0;               //Auxiliary array length


    constructor(){
        emit BattleshipsCreated(address(this));
    }

    ///@dev modifier checking whether the match exists and it's not already full
    ///@param id Match_id
    modifier isValid(bytes32 id){
        require(games[id].player_1 != address(0), "No match found");
        require(games[id].full == false, "Match already full");
        _;
    }

    ///@dev modifier checking wether it's the correct player turn
    ///@param id Match_id
    modifier validTurn(bytes32 id){
        require(games[id].player_1 != address(0), "No match found");
        require(games[id].player_2 != address(0), "Match still pending");
        require(games[id].player_1 != msg.sender || games[id].player_2 != msg.sender, ("User not allowed"));
        require((msg.sender == games[id].player_1 && games[id].turn == -1) || 
                (msg.sender == games[id].player_2 && games[id].turn == 1), 
                "Not your turn - Wait for the opponent");
        _;
    }

    ///@notice Function to remove elements from the array of matches
    ///@param id Match_id
    function remove_match(bytes32 id)
    private
    {
        delete games[id];
        if(games_index.length == 1){
            games_index.pop();
            return;
        }
        uint i = 0;
        while(games_index[i] != id && i<games_index.length){
            i++;
        }
        if(i == games_index.length){
            games_index.pop();
            return;
        }
        if (games_index[i] == id){
            for(uint j = i; j<games_index.length-1; j++){
                games_index[j] = games_index[j+1];
            }
            games_index.pop();
            return;
        }
    }

    ///@notice Function for match creation
    ///@param board_1 Player_1's board merkle root
    ///@param _size Board size
    ///@param n_ships Total number of ships
    function create_match(bytes32 board_1, uint8 _size, uint64 n_ships)
    public{
        bytes32 id = keccak256(abi.encodePacked(msg.sender, board_1, block.number));
        Match memory new_match = Match(false, 0, payable(address(0)), false, _size, 1, payable(msg.sender), board_1, payable(address(0)), 0x0, n_ships, n_ships, n_ships, 0);
        games[id] = new_match;
        games_index.push(id);
        len += 1;
        emit newMatch(id);
    }
    
    ///@notice Function for match join with known ID
    ///@param id Match_id
    function join_match_id(bytes32 id)
    public
    isValid(id)
    {
        emit size_only(games[id].size, id);
    }

    ///@notice Function for joining a random match
    function join_match()
    public{
        uint i = 0;
        bytes32 id;
        bool found = false;
        
        //looks for the first pending match in the mapping
        while(i<games_index.length && found == false){
            if(games[games_index[i]].full == false /*&& games[games_index[i]].size != 0*/){
                found = true;
                id = games_index[i];
            }
            i+=1;
        }
        if(found == false){
            emit noMatches(len); 
        }
        else{
            emit size_ID(games[id].size, id);
        }
    }

    ///@notice Function for uploading Player_2's board merkle root
    ///@param id Match_id
    ///@param board Board's Merkle root
    function upload_board(bytes32 id, bytes32 board)
    public
    isValid(id)
    {
        games[id].player_2 = payable(msg.sender);
        games[id].board_2 = board;
        games[id].full = true;
        emit match_ready(id);
    }

    ///@notice Function for making a move
    ///@param id Match_ic
    ///@param row row
    ///@param col col
    function play_turn(bytes32 id, uint row, uint col)
    public
    validTurn(id){
        emit turn_played(id, row, col);
    }

    ///@notice Function for updating boards and checking that the opponent won't cheat
    ///@param id Match_id
    ///@param res Hit(1) or Miss(0)
    ///@param index Position of value in the matrix
    ///@param nonce Nonce used for leaf hash generation
    ///@param proof Opponent's Merkle proof
    function check_move(bytes32 id, uint256 res, uint index, uint256 nonce, bytes32[] calldata proof) 
    public 
    {
        require((msg.sender == games[id].player_1 && games[id].turn == 1) || 
                (msg.sender == games[id].player_2 && games[id].turn == -1), 
                "Not your turn - Wait for the opponent");
        
        bytes32 leaf = keccak256(abi.encode(res, nonce));
        bytes32 _hash = leaf;
        for(uint i = 0; i<proof.length; i++){
            if(index % 2 == 0){
                _hash = keccak256(abi.encode(_hash,proof[i]));
            }
            else{
                _hash = keccak256(abi.encode(proof[i],_hash));
                
            }
            index = index/2;   
        }

        bytes32 root;
        if(msg.sender == games[id].player_1){
            root = games[id].board_1;
        }
        else{
            root = games[id].board_2;
        }

        //Genuine response
        if(_hash == root){
            if(res == 1){
                if(games[id].turn == -1){
                    //Player_1 Turn
                    if(games[id].ships_2>1){
                        games[id].ships_2 --;
                    }
                    else{
                        //Match ended: Player_1 won
                        games[id].ships_2 --;
                        emit match_ended(id, 0);
                        return;
                    }
                }
                else{
                    //Player_2 Turn
                    if(games[id].ships_1>1){
                        games[id].ships_1 --;
                    }
                    else{
                        //Match ended: Player_2 won
                        games[id].ships_1 --;
                        emit match_ended(id, 0); 
                        return;
                    }
                }
            }
            //Change turn
            games[id].turn *= -1; 
            emit turn_response(id, res);
        }

        //Cheating attempt
        else{
            emit match_ended(id, -1);
            if(games[id].turn == 1){
                payable(games[id].player_1).transfer(games[id].reward);
            }
            else{
                payable(games[id].player_2).transfer(games[id].reward);
            }

            remove_match(id);
            return;
        }
        
        emit your_turn(id);
    }

    ///@notice Function for board verification after the match ended
    ///@param id Match_id
    ///@param board List of ships placed
    function check_board(bytes32 id, uint64[] calldata board)
    public
    {   
        require((games[id].player_1 == msg.sender && games[id].ships_2 == 0) ||
                (games[id].player_2 == msg.sender && games[id].ships_1 == 0),
                "Match still not finished!");
        
        uint64 sum = 0;
        for(uint i = 0; i< board.length; i++){
            sum += board[i];
        }
        
        if(sum == games[id].total_ships){ //Legit Board
            emit match_ended(id, 1);
            payable(msg.sender).transfer(games[id].reward);
            remove_match(id);
        }
        else{ //Invalid board
            emit match_ended(id, -1);
            if(games[id].turn == 1){
                payable(games[id].player_1).transfer(games[id].reward);
            }
            else{
                payable(games[id].player_2).transfer(games[id].reward);
            }
            remove_match(id);
        }
        return;
    }

    ///@notice Function for bet placement; refunds in case of mismatch
    ///@param id Match_id
    function bet(bytes32 id)
    public
    payable{
        require(msg.sender == games[id].player_1 || msg.sender == games[id].player_2, "User not allowed");
        if(games[id].reward == 0){
            games[id].reward = msg.value;
            emit bid_placed(id, 1);
        }
        else{
            uint256 bid = msg.value;
            if(bid == games[id].reward){
                games[id].reward += bid;
                emit bid_placed(id, 2);
                emit your_turn(id); 
            }
            else{
                //Player_1 wrong bid - Game over
                if(msg.sender == games[id].player_1){                            
                    payable(games[id].player_1).transfer(bid);
                    payable(games[id].player_2).transfer(games[id].reward);
                }
                //Player_2 wrong bid - Game over
                else{                                                           
                    payable(games[id].player_2).transfer(bid);
                    payable(games[id].player_1).transfer(games[id].reward);
                }
                emit match_ended(id, -1);
                remove_match(id);
            }
        }
    }

    ///@notice Function for accusing the opponent for inactivity
    ///@param id Match_id
    function accuse_player(bytes32 id)
    public{
        require((msg.sender == games[id].player_1 && games[id].turn == 1) || 
                (msg.sender == games[id].player_2 && games[id].turn == -1), 
                "You cannot accuse yourself");
        require(games[id].accuse == false, "Accuse already done!");
        games[id].accuse = true;
        games[id].curr_block_num = block.number;
        games[id].accuser = payable(msg.sender);
        emit accuse(id, games[id].curr_block_num);
    }

    ///@notice Function for reward withdraw in case of victory due inactivity
    ///@param id Match_id
    function withdraw(bytes32 id)
    payable
    public{
        require((msg.sender == games[id].player_1 && games[id].turn == 1) || 
                (msg.sender == games[id].player_2 && games[id].turn == -1), 
                "Invalid Operation!");
        require(games[id].accuse = true && (block.number - games[id].curr_block_num >= 5), "Invalid Withdraw");
        payable(games[id].accuser).transfer(games[id].reward);
        emit match_ended(id, -2);
        remove_match(id);
    }

    ///@notice Function for responding to inactivity accuse
    ///@param id Match_id
    function accuse_res(bytes32 id)
    public{
        require((msg.sender == games[id].player_1 && games[id].turn == -1) || 
                (msg.sender == games[id].player_2 && games[id].turn == 1), 
                "Invalid response!");
        require(games[id].accuse == true, "No accuse pending!");
        games[id].accuse = false;
        games[id].curr_block_num = 0;
        games[id].accuser = payable(address(0));
    }
}