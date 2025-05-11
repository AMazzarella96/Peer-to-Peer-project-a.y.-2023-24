#Author: Alessandro Mazzarella
#Title: board
#notice: Front-End for Battleships game on Ethereum

import math
import secrets
import time
import pandas as pd
import numpy as np
import asyncio
import warnings
from web3 import Web3
import json



#--------------------------|Convert DataFrame to Array
#args: board (DataFrame)

#returns: board_array (Int[])
def df_toArray(board): 
    board_array = []
    size = len(board)
    for i in range(size):
        for j in range(size):
            board_array.append(board.iat[i,j].item())
    return board_array


#--------------------------|Read contract json
#returns: Contract ABI, Bytecode
def readContractData(path): 
    with open(path) as obj:
        jsonContract = json.load(obj)
        return jsonContract["abi"], jsonContract["bytecode"]


#--------------------------|Prints the list of available ships for the current match
#args: d (Dictionary <ship -> number_available>)
def print_available(d): 
    if(d):
        print("\nAvailable ships:\n")
        for k,v in d.items():
            if v>0:
                print("[ ", k, " By 1 ] (x",v,")", sep='')
    else:
        print("\nNo more ships")


#--------------------------|Fills the board with all the positioning checks
#args: ships (Dictionary)
#      board (DataFrame)
def fill_board(ships, board): 
    lenght = len(board)
    while(ships):
        print_available(ships)
        ship = str(input("\nSelect the length of the ship to place: "))
        while(ship not in ships):
            print("Invalid ship")
            print_available(ships)
            ship = str(input("\nSelect the length of the ship to place: "))
        print("Select coordinates for placement\n")
        print(board)
        ship_int = int(ship)
        
        #--------------------------------1st coordinate
        first_row = -1
        first_col = -1
        while(first_row < 0 or first_row > lenght-1 or first_col < 0 or first_col > lenght-1):
            first = str(input("\nStarting point:\n").upper())
            if(len(first)<2):
                print("Invalid placement - Select a correct cordinate!\n")
            else:
                first_row = ord(first[0])-65
                try:
                    first_col = int(first[1:])
                except ValueError:
                    first_col = -1
                    first_row = -1
                if(first_row < 0 or first_row > lenght-1 or first_col < 0 or first_col > lenght-1):
                    print("Invalid placement - Select a correct cordinate!\n")
                    first_col = -1
                    first_row = -1
                elif(board.iat[first_row, first_col] != 0):
                    print("Invalid placement - Select a correct cordinate!\n")
                    first_col = -1
                    first_row = -1

                #Check wether there's room for the selected ship
                else:
                    
                    #top -> down
                    if(first_row + (ship_int - 1) < lenght):
                        sum = 0
                        for i in range (first_row, first_row + ship_int):
                            sum += board.iat[i, first_col]
                        if(sum == 0):
                            break
                    
                    #bottom -> up
                    elif(first_row - (ship_int - 1) >= 0):
                        sum = 0
                        for i in range(first_row, first_row - ship_int):
                            sum += board.iat[i, first_col]
                        if(sum == 0):
                            break

                    #left -> right  
                    elif(first_col + (ship_int - 1) < lenght):
                        sum = 0
                        for i in range(first_col, first_col + ship_int):
                            sum += board.iat[first_row, i]
                        if(sum == 0):
                            break
                    
                    #right -> left
                    elif(first_col - (ship_int - 1) >= 0):
                        sum = 0
                        for i in range(first_col, first_col - ship_int):
                            sum += board.iat[first_row, i]
                        if(sum == 0):
                            break
                    print("Invalid Placement - Not enough space")
                    first_col = -1
                    first_row = -1

        #-----------------------------------2nd coordinate
        second_row = -1
        second_col = -1 
        while(second_row < 0 or second_row > lenght-1 or second_col < 0 or second_col > lenght-1):
            print("\nEnding point:", first,"- ", end='')
            second = str(input().upper())
            second_row = ord(second[0])-65
            try:
                second_col = int(second[1:])
            except ValueError:
                second_col = -1
                second_row = -1
            if(second_row < 0 or second_row > lenght-1 or second_col < 0 or second_col > lenght-1 or
               (first_col != second_col and first_row != second_row) or 
               (first_col == second_col and abs(first_row-second_row) != ship_int-1) or 
               (first_row == second_row and abs(first_col-second_col) != ship_int-1)):
                print("Invalid placement - Select a correct cordinate!\n")
                second_row = -1
                second_col = -1
            else:

                #Check intersection with other ships
                sum = 0
                if(first_col == second_col and abs(first_row-second_row) == ship_int-1):
                    #top -> down
                    if(first_row < second_row):
                        for i in range(first_row, second_row+1):
                            sum += board.iat[i,first_col]
                    #bottom -> up
                    else:
                        for i in range(second_row, first_row+1):
                            sum += board.iat[i,first_col]
                elif(first_row == second_row and abs(first_col-second_col) == ship_int-1):
                    #left -> right
                    if(first_col < second_col):
                        for i in range(first_col, second_col+1):
                            sum += board.iat[first_row, i]
                    #right -> left
                    else:
                        for i in range(second_col, first_col+1):
                            sum += board.iat[first_row, i]
                if(sum!=0):
                    print("Invalid placement - Select a correct cordinate!\n")
                    second_row = -1
                    second_col = -1
                #Placement
                else:
                    if(first_row == second_row):
                        #left -> right
                        if(first_col < second_col):
                            for i in range (first_col, second_col+1):
                                board.iat[first_row,i] = 1
                        #right -> left
                        else:
                            for i in range (second_col, first_col+1):
                                board.iat[first_row, i] = 1
                    elif(first_col == second_col):
                        #top -> down
                        if(first_row < second_row):
                            for j in range (first_row, second_row+1):
                                board.iat[j, first_col] = 1
                        #bottom -> up
                        else:
                            for j in range (second_row, first_row+1):
                                board.iat[j, first_col] = 1
                    if(ships[ship] > 1):
                        ships[ship] -= 1
                    else:
                        ships.pop(ship)
            print(board)


#--------------------------|Create and fill a board, and computes merkle root
# args: size            Board size (Int)

#returns: board (DataFrame)
#         merkle_root (Bytes)
#         board_nonces (Int[])
def create_board(n):
    size = n*n
    tmp_board = np.array([0]*size).reshape(n,n)
    board = pd.DataFrame(tmp_board, columns = [str(x) for x in range(len(tmp_board))], index=[chr(i+65) for i in range(len(tmp_board))])
    print(board)
    match n:
        case 2:
            ships = {'2': 1}
            fill_board(ships, board)
        case 4:
            ships = {'2': 2,'3': 1}
            fill_board(ships,board)
        case 8:
            ships = {'2': 1,'3': 2,'4': 1,'5': 1}
            fill_board(ships,board)
        case 16:
            ships = {'2': 3,'3': 4,'4': 2,'5': 3}
            fill_board(ships,board)
    
    arr = []
    board_nonces = []

    for ind in range(n):
            for cl in range(n):
                arr.append(board.iat[ind, cl].item()) #DataFrame -> Int[]
                nonce = secrets.randbits(32)
                board_nonces.append(nonce)
               
    r = merkle_tree(arr, board_nonces)
    
    return board, r, board_nonces


#--------------------------|Calls Solidity function to start a new match
#args: gan                      Blockchain instance (Web3.HTTP_Provider)
#      merkle_root              Root hash of the board (Bytes)
#      contract_battleship      Contract instance (Web3.eth.contract)
#      usr_addr                 User address (Bytes)
#      size                     Board size (Int)

#returns: match_id (Bytes)
def new_match(gan ,root, contract_battleships, usr_addr, size):
    match size:
        case 2:
            n_ships = 2
        case 4:
            n_ships = 7
        case 8:
            n_ships = 17
        case 16:
            n_ships = 41

    tx_hash = contract_battleships.functions.create_match(root, size, n_ships).transact({'from': usr_addr})
    tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
    logs = contract_battleships.events.newMatch().process_receipt(tx_receipt)
    match_id = logs[0]['args']['id']
    return(match_id)


#--------------------------|Creates a merkle tree from an array
#args: board_array (Int[])
#      board_nonce (Int[])

#returns: merkle_root (Bytes)
def merkle_tree(board_array, board_nonces):
    size = int(len(board_array))
    if(size == 2):
        a = Web3.solidity_keccak(['uint256','uint256'], [board_array[0],board_nonces[0]])
        b = Web3.solidity_keccak(['uint256','uint256'], [board_array[1],board_nonces[1]])
        root = Web3.solidity_keccak(['bytes32','bytes32'], [a,b])
        return root
    sx = merkle_tree(board_array[0:int(size/2)], board_nonces[0:int(size/2)])
    dx = merkle_tree(board_array[int(size/2):size], board_nonces[int(size/2):size])
    root = Web3.solidity_keccak(['bytes32','bytes32'], [sx,dx])
    return root


#--------------------------|Creates a merkle proof for a specific key
#args: board_array   (Int[])
#      k             (Int)
#      proof[]       (Bytes[])

#returns: proof[]    (Bytes[])
def get_proof(board_array, k, proof, board_nonces):
    size = len(board_array)
    depth = math.log2(size)
    if(k>=int(size/2)):
        root = merkle_tree(board_array[0:int(size/2)], board_nonces[0:int(size/2)])
        proof.insert(0, bytes(root))
        if(depth == 2):
            if(k % 2 == 0):
                el = Web3.solidity_keccak(['uint256','uint256'], [board_array[abs(1-k)+int(size/2)], board_nonces[abs(1-k)+int(size/2)]])
            else:
                el = Web3.solidity_keccak(['uint256', 'uint256'], [board_array[abs(1-k)], board_nonces[abs(1-k)]])
            proof.insert(0, bytes(el))
            return proof
        else:
            k = int(k%int(size/2))
            get_proof(board_array[int(size/2) : size], k, proof, board_nonces[int(size/2) : size])
            return proof
    else:
        root = merkle_tree(board_array[int(size/2):size], board_nonces[int(size/2):size])
        proof.insert(0, bytes(root))
        if(depth == 2):
            el = Web3.solidity_keccak(['uint256', 'uint256'], [board_array[abs(1-k)], board_nonces[abs(1-k)]])
            proof.insert(0, bytes(el))
            return proof
        else:
            k = int(k%(size/2))
            get_proof(board_array[0 : int(size/2)], k, proof, board_nonces[0 : int(size/2)])
            return proof


#--------------------------|Front end menus
def print_menu_1():
    print("\n\n|/\/\/\/\/\/\/\/\/\/\/\/\/|BATTLESHIPS|\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    print("1) New Game")
    print("2) Join Game\n")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")

def print_menu_2():
    print("\n\n|/\/\/\/\/\/\/\/\/\/\/\/\/|BATTLESHIPS|\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    print("Select board dimension:")
    print("1) 2x2")
    print("2) 4x4")
    print("3) 8x8")
    print("4) 16x16")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")

def print_menu_3():
    print("\n\n|/\/\/\/\/\/\/\/\/\/\/\/\/|BATTLESHIPS|\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    print("1) I already have a MatchID")
    print("2) Join random match")
    print("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")


#--------------------------|Loop waiting for other player to join our match
async def log_loop(event_filter, poll_interval, id):
    while True:
        for ev in event_filter.get_new_entries():
            if(ev['args']['id'] == id):
                return
        await asyncio.sleep(poll_interval)


#Convert the amount in wei
def convert_to_wei(amount):
    return Web3.to_wei(amount, 'Ether')


#--------------------------|Loop waiting for betting phase
#returns: -1 (Bets do not correspond - Refund)
#          1 (Same bet - Match start)
async def place_bet(filter_bid, filter_end, poll_interval, id):
    while True:
        for ev1 in filter_end.get_new_entries():
            if(ev1['args']['id'] == id):
                print("Match Ended")
                return -1
        for ev2 in filter_bid.get_new_entries():
            if(ev2['args']['id'] == id):
                if(ev2['args']['bid']==2):
                    print("Match Start")
                    return 1
        await asyncio.sleep(poll_interval)


#--------------------------|Match logic loop
#args: filter_end       (match_ended event filter)
#      filter_accuse    (accse event filter)
#      filter_res       (turn_response event filter)
#      filter_play      (turn_playes event filter)
#      filter_turn      (your_turn event filter)
#      poll_interval    (Int)
#      turn             (Int) 1(your turn) / -1 (opponents' turn)
#      board_1          (DataFrame)
#      board_2          (DaraFrame)
#      gan              (Web3.HTTP_Povider)
#      contract         (Web3.eth.contract)
#      id               (Bytes)
#      usr_addr         (Bytes)
async def play_game(filter_end, filter_accuse, filter_res, filter_play, filter_turn, poll_interval, turn, board_1, board_2, nonces, gan, contract, id, usr_addr):
    lenght = len(board_1)
    board_array = df_toArray(board_1)
    live_check = 0 #Inactivity flag check
    while True:

        # Event Match ended 
        for ev1 in filter_end.get_new_entries():
            if(ev1['args']['id'] == id):
                if(ev1['args']['outcome'] == -1): #cheating
                    if(turn == 1):
                        print("The opponent tried to cheat - You WON!")
                    else:
                        print("No cheating allowed - You LOOSE!")
                    return
                
                elif(ev1['args']['outcome'] == -2): #inactivity
                    if(turn == 1):
                        print("Inactivity penalty! - You LOOSE!")
                    else:
                        print("Opponent left the game - You WON!")
                    return

                elif(ev1['args']['outcome'] == 0): #legit match
                    if(turn == 1):
                        print("All enemy ships destroyed! - Verifying your board...")
                        tx_hash = contract.functions.check_board(id, df_toArray(board_1)).transact({'from': usr_addr})
                        tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                elif(ev1['args']['outcome'] == 1):
                    if(turn == 1):
                        print("\nCongratulations - You WON!")
                    else:
                        print("\nGame Over - You LOOSE...")
                    return
                
        #Event Accuse
        for ev2 in filter_accuse.get_new_entries():
            if(ev2['args']['id'] == id):
                live_check = 2
                if(turn == -1):
                    curr_block_num = ev2['args']['block_num']
                if(turn == 1):
                    tx_hash = contract.functions.accuse_res(id).transact({'from': usr_addr})
                    tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                    live_check = 0
                    curr_block_num = 0
                    latest_block_num = 0

        #Event Turn_Response
        for ev3 in filter_res.get_new_entries():
            if(ev3['args']['id'] == id):
                if(turn == 1):
                    res = ev3['args']['res']
                    if(res == 1):
                        print("\n|----- HIT! -----|")
                        board_2.iat[row,col] = "H"
                    else:
                        print("\n|----- MISS -----|")
                        board_2.iat[row,col] = "M"

        #Event Your_turn
        for ev4 in filter_turn.get_new_entries():
            if(ev4['args']['id'] == id):
                turn *= -1
                if(turn == 1): #our turn
                    print("YOUR BOARD")
                    print(board_1)
                    print("\nADVERSAY BOARD")
                    print(board_2,"\n")
                    row = -1
                    col = -1
                    while(row < 0 or row > lenght-1 or col < 0 or col > lenght-1):
                        coord = str(input("Fire Torpedo - Select coordinates: ").upper())
                        if(len(coord)<2):
                            print("Invalid placement - Select a correct cordinate!\n")
                        else:
                            row = ord(coord[0])-65
                            try:
                                col = int(coord[1:])
                            except ValueError:
                                col = -1
                                row = -1
                            if(row < 0 or row > lenght-1 or col < 0 or col > lenght-1):
                                print("Invalid placement - Select a correct cordinate!\n")
                                row = -1
                                col = -1
                            elif(board_2.iat[row,col]!=0):
                                print("Invalid placement - Coordinate already hit!\n")
                                col = -1
                                row = -1
                    try:
                        tx_hash = contract.functions.play_turn(id, row, col).transact({'from': usr_addr})
                        tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                    except:
                        pass
                    
                else:
                    print("\nOpponent's turn...")
                    t1 = time.time()
                    live_check = 1

        #Event Turn_played
        for ev5 in filter_play.get_new_entries():
            if(ev5['args']['id'] == id):
                if(turn==-1): #Opponents made its move
                    live_check = 0
                    row = ev5['args']['row']
                    col = ev5['args']['col']
                    res = -1
                    while(res > 1 or res < 0):
                        print("The opponent shot at: " + str(chr(row+65))+str(col))
                        print("\nYOUR BOARD")
                        print(board_1,"\n")
                        print("Hit(1) or Miss(0)?: ")
                        try:
                            res = int(input())
                        except ValueError:
                            print("invalid option - Select Hit(1) or Miss(0)")
                            res = -1
                    k = (row*lenght)+col
                    proof = get_proof(board_array,k,[], nonces)
                    tx_hash = contract.functions.check_move(id, res, k, nonces[k], proof).transact({'from': usr_addr})
                    tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                else:
                    print("Waiting for response...")
                
        await asyncio.sleep(poll_interval)
        if(live_check == 1 and turn == -1):
            t2 = time.time()
            if(t2 - t1 > 10):
                print("Do you want to check if opponent is still online? Y - N")
                check = str(input()).upper()
                while(check != "Y" and check != "N"):
                    print("Invalid response - Select Y - N!")
                    check = str(input()).upper()
                if(check == "Y"):
                    tx_hash = contract.functions.accuse_player(id).transact({'from': usr_addr})
                    tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                else:
                    t1 = time.time()
                    t2 = t1
        elif(live_check == 2 and turn == -1):
            latest_block_num = gan.eth.block_number
            if(latest_block_num - curr_block_num >= 5):
                tx_hash = contract.functions.withdraw(id).transact({'from': usr_addr})
                tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)


def main():
    warnings.filterwarnings("ignore","The log with transaction hash")
    warnings.simplefilter(action='ignore', category=FutureWarning)
    url = "HTTP://127.0.0.1"
    port = 7545
    gan = Web3(Web3.HTTPProvider(url + ":" + str(port)))
    
    #Create the contract instance
    _abi, _bytecode = readContractData("build/contracts/Battleships.json")
    contract_instance = gan.eth.contract(abi = _abi, bytecode = _bytecode)
    filter = contract_instance.events.BattleshipsCreated.create_filter(fromBlock = 0, toBlock = 'latest')
    evs = filter.get_all_entries()
    _address = evs[0]['args']['addr']
    contract_battleships = gan.eth.contract(abi = _abi, address = _address)

    print_menu_1()
    opt_1 = -1
    while(opt_1<1 or opt_1>2):
        try:
            opt_1 = int(input())
        except TypeError:
            print("Invalid Operation! Select 1) or 2)")
            opt_1 = -1
        except ValueError:
            print("Invalid Operation! Select 1) or 2)")
            opt_1 = -1
        
    # ----------------------------------| NEW GAME |----------------------------------
    if(opt_1==1):
        turn = 1
        usr_addr = gan.eth.accounts[0]
        print_menu_2()
        opt_2 = -1
        while(opt_2<1 or opt_2>4):
            try:
                opt_2 = int(input())
            except TypeError:
                print("Invalid size! Select one of the valid sizes:")
                opt_2 = -1
            except ValueError:
                print("Invalid size! Select one of the valid sizes:")
                opt_1 = -1
        
        size = pow(2,opt_2)
        board, root, nonces = create_board(size)
        match_id = new_match(gan, root, contract_battleships, usr_addr, size)
        print("Your Match_ID: ", match_id.hex())

        #Waiting for opponent
        event_filter = contract_battleships.events.match_ready.create_filter(fromBlock = 'latest')
        loop = asyncio.new_event_loop()
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    log_loop(event_filter, 3, match_id)
                )
            )
        except RuntimeError as re:
            print(re)
        
        
    # ----------------------------------| JOIN GAME |----------------------------------
    elif(opt_1==2):
        turn = -1
        usr_addr = gan.eth.accounts[1]
        print_menu_3()
        opt_3 = -1
        while(opt_3 < 1 or opt_3 > 2):
            try:
                opt_3 = int(input())
            except ValueError:
                print("Invalid option - Select a valid one!")
                print_menu_3()
                opt_3 = -1
            except TypeError: 
                print("Invalid option - Select a valid one!")
                print_menu_3()
                opt_3 = -1
            
        match opt_3:
            case 1: #Have Match_ID
                print("Insert MatchID: ")
                ctrl = -1
                while(ctrl == -1):
                    try:
                        match_id = bytes.fromhex(input())
                        tx_hash = contract_battleships.functions.join_match_id(match_id).transact({'from': usr_addr})
                        tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                        ctrl = 1
                    except KeyboardInterrupt:
                        return
                    except:
                        print("Invalid ID! - Insert a valid one: ")
                        ctrl = -1

                logs = contract_battleships.events.size_only().process_receipt(tx_receipt)
                size = logs[0]['args']['size']

            case 2: #Don't have Match_ID
                tx_hash = contract_battleships.functions.join_match().transact({'from': usr_addr})
                tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
                logs = contract_battleships.events.size_ID().process_receipt(tx_receipt)
                size = logs[0]['args']['size']
                match_id = logs[0]['args']['id']
        board, root, nonces = create_board(size)
        tx_hash = contract_battleships.functions.upload_board(match_id, root).transact({'from': usr_addr})
        tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)

    print("\nYOUR BOARD")
    print(board)
    tmp_board = np.array([0]*(size*size)).reshape(size,size)
    board_2 = pd.DataFrame(tmp_board, columns = [str(x) for x in range(len(tmp_board))], index=[chr(i+65) for i in range(len(tmp_board))])
    print("\nOPPONENT'S BOARD")
    print(board_2)


    filter_bet = contract_battleships.events.bid_placed.create_filter(fromBlock = 'latest')
    filter_end = contract_battleships.events.match_ended.create_filter(fromBlock = 'latest')
    filter_turn = contract_battleships.events.your_turn.create_filter(fromBlock = 'latest')
    filter_res = contract_battleships.events.turn_response.create_filter(fromBlock = 'latest')
    filter_play = contract_battleships.events.turn_played.create_filter(fromBlock = 'latest')
    filter_accuse = contract_battleships.events.accuse.create_filter(fromBlock = 'latest')

# ----------------------------------| MATCH FULL |----------------------------------

    #Reward selection
    b = -1
    while (b < 0):
        print("Insert reward: ")
        try:
            b = int(str(input()))
        except ValueError:
            print("Invalid reward - Must be a positive value!")
            b = -1
    bet = convert_to_wei(b)
    tx_hash = contract_battleships.functions.bet(match_id).transact({'from': usr_addr, 'value': bet})
    tx_receipt = gan.eth.wait_for_transaction_receipt(tx_hash)
    logs = contract_battleships.events.bid_placed().process_receipt(tx_receipt)
    if(not logs):
        logs = contract_battleships.events.match_ended().process_receipt(tx_receipt)
        print("Match Ended - Reward Mismatch")
        loop.close()
        return

    #Waiting for the opponent to palce bet
    loop = asyncio.new_event_loop()
    loop = asyncio.get_event_loop()
    res = 0
    try:
        res = loop.run_until_complete(
                asyncio.gather(
                    place_bet(filter_bet, filter_end, 3, match_id)
                )
            )
    finally:
        #reward mismatch
        if(res == -1):
            return
    
    #Waits for game start event
    logs = contract_battleships.events.your_turn().process_receipt(tx_receipt)
    loop = asyncio.new_event_loop()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                play_game(filter_end, filter_accuse, filter_res, filter_play, filter_turn, 3, turn, board, board_2, nonces, gan, contract_battleships, match_id, usr_addr)
            )
        )
    finally:
        pass
    loop.close() 

if __name__ == "__main__":
    main()