import pygame, sys, random, copy
from pygame.locals import *
from cards import *
import time
import math
from statistics import mean
import numpy as np

def genCard(cList, xList):
    #Generate and remove an card from cList and append it to xList.
    #Return the card, and whether the card is an Ace
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    #Generates two cards for dealer and user, one at a time for each.
    #Returns if card is Ace and the total amount of the cards per person.
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    #The values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst

def make_state(userSum, userA, dealFirst, dealAFirst):
    #Eliminate duplicated bust cases
    if userSum > 21: 
        userSum = 22
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace   
    return (userSum, userA, dealFirst, dealAFirst)

def policy(userSum):
    if userSum < 17:
        return 0
    else:
        return 1

def simulation_sequence(policy, state, userCard, dealCard, ccards):
    episode = []
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    stand = False
    gameover = False
    # follow the game engine to do simulation
    while True:
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        action = policy(userSum)
        # calculate reward
        if not (gameover or stand):
        #if not gameover and action == 0:
            episode.append((state,0))
        else:
            if userSum == dealSum:
                reward = 0
            elif userSum <= 21 and len(userCard) == 5:
                reward = 1
            elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                reward = 1
            else:
                reward = -1
            episode.append((state,reward))
            return episode
        #action = policy(userSum)
        if not (gameover or stand) and action == 0:
            #Give player a card
            card, cA = genCard(ccards, userCard)
            userA += cA
            userSum += getAmt(card)
            while userSum > 21 and userA > 0:
                userA -= 1
                userSum -= 10
        elif not gameover and action == 1:
            #Dealer plays, user stands
            stand = True
            if dealSum == 21:
                pass
            else:
                while dealSum <= userSum and dealSum < 17:
                    card, cA = genCard(ccards, dealCard)
                    dealA += cA
                    dealSum += getAmt(card)
                    while dealSum > 21 and dealA > 0:
                        dealA -= 1
                        dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)

def simulate_one_step(state, action, userCard, dealCard, ccards, stand):
    #Need to implement this for TD and QL
    episode = []
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    gameover = False
    # Simulate "hit" step
    if action == 0 and stand == False:
        #print("take hit")
        card, cA = genCard(ccards, userCard)
        userA += cA
        userSum += getAmt(card)
        while userSum > 21 and userA > 0:
            userA -= 1
            userSum -= 10
    # Simulate "stand" step
    else:
        if dealSum == 21:
            pass
        else:
            #print("take stand")
            while dealSum <= userSum and dealSum < 17:
                card, cA = genCard(ccards, dealCard)
                dealA += cA
                dealSum += getAmt(card)
                while dealSum > 21 and dealA > 0:
                    dealA -= 1
                    dealSum -= 10
    # Make next state   
    next_state = make_state(userSum, userA, dealFirst, dealAFirst)
    next_userSum = next_state[0]
    next_userA = next_state[1]
    next_dealSum = next_state[2]
    next_dealA = next_state[3]
    # Check if game is over
    if (next_userSum >= 21 and next_userA == 0) or len(userCard) == 5:
        gameover = True
    elif len(userCard) == 2 and next_userSum == 21:
        gameover = True
    elif stand == True:
        gameover = True
    else:
        gameover = False

    reward = 0
    # End game calculate reward
    if gameover == True:
        if userSum == dealSum:
            reward = 0
        elif userSum <= 21 and len(userCard) == 5:
            reward = 1
        elif userSum <= 21 and dealSum < userSum or dealSum > 21 and stand == True:
            reward = 1
        else:
            reward = -1
    return (next_state, reward, gameover)


def reward_to_go(s, gamma, episode):
    # Placeholder, need to implement the right calculation
    result = 0
    for i in range(len(episode)):
        # Find the state that correspond to the input state
        if s == episode[i][0]:
            # For a state that takes a "stand" step, the last two states in episode is actually the same
            if i==len(episode)-2 and episode[i][0] == episode[i+1][0]:
                # A "stand" terminate state should just get the reward value
                return episode[i+1][1]
            k = i
            # Calculate the reward value
            while i!=len(episode):
                new_gamma = math.pow(gamma, i-k)
                reward = episode[i][1]
                result += new_gamma * reward
                i+=1
            return result
    return result

def MC_Policy_Evaluation(policy, states, gamma, MCvalues, G):
    #Perform 50 simulations in each cycle in each game loop (so total number of simulations increases quickly)
    for simulation in range(50):
        # Intialize an starting state
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        episode = simulation_sequence(policy, state, userCard, dealCard, ccards)
        # Calculate utility for the states in episode
        for e in episode:
            # If the simulation ends by a stand, the last state in episode doesn't need to be consider
            if episode.index(e) == len(episode)-1 and episode[len(episode)-1][0] == episode[len(episode)-2][0]:
                break
            value = reward_to_go(e[0], gamma, episode)
            G[e[0]].append(value)
            MCvalues[e[0]] = mean(G[e[0]])
    #for simulation in range(50):
        # generate random game
        #userCard = []
        #dealCard = []
        #ccards = copy.copy(cards)
        #userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        #state = make_state(userSum, userA, dealFirst, dealAFirst)
        # do simulation
        #episode = simulation_sequence(policy, state, userCard, dealCard, ccards)
        # update
        #for e in episode:
            #This line is a placeholder. Remove. Need more lines too, of course. 
            #G[e[0]].append(reward_to_go(e, gamma, episode))
            #MCvalues[e[0]] = mean(G[e[0]])

def TD_Policy_Evaluation(policy, states, gamma, TDvalues, NTD):
    for simulation in range(50):
        # Initial a new start 
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        iteration_stop = False
        # Start simulation
        while iteration_stop == False:
            # Increament 1 on visit at current state
            NTD[state]+=1
            alpha = 10/(9+NTD[state])
            action = policy(state[0])
            if action == 0:
                stand = False
            else:
                stand = True
            # Simulate the next step based on policy
            next_state = simulate_one_step(state, action, userCard, dealCard, ccards, stand)
            # Update utility value
            if stand == False:
                TDvalues[state] = TDvalues[state] + alpha * (next_state[1] + gamma * TDvalues[next_state[0]] - TDvalues[state])
            # When the action is stand, the value of next_state actually doesn't change
            else:
                TDvalues[state] = next_state[1]
            state = next_state[0]
            # If game is over, terminate the loop
            if next_state[2] == True:
                iteration_stop = True

def pick_action(s, eps, Qvalues):
    # Epsilon greedy policy
    if random.random() < eps:
        #print("random pick")
        return random.choice([0,1])
    else:
        #print("pick with the best")
        if Qvalues[s][0]>Qvalues[s][1]:
            return 0
        else:
            return 1

def Q_Learning(states, gamma, Qvalues, NQ):
    for simulation in range(50):
        # Initialize a starting state
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        iteration_stop = False
        eps = 0.43
        while iteration_stop == False:
            # Increment visits and calculate alpha
            NQ[state] += 1
            alpha = 10/(9+NQ[state])
            # Pick an action
            action = pick_action(state, eps, Qvalues)
            if action == 0:
                stand = False
            else:
                stand = True
            # Simulate the next step
            next_state = simulate_one_step(state, action, userCard, dealCard, ccards, stand)
            # Update the Q value according to action
            Qvalues[state][action] = Qvalues[state][action] + alpha * (next_state[1] + gamma * max(Qvalues[next_state[0]][0], Qvalues[next_state[0]][1]) - Qvalues[state][action])
            state = next_state[0]
            if next_state[2] == True:
                iteration_stop = True 

def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    #Initialize Game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    playTxt = font.render('Play', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)
    #Prepare table of utilities
    G = {}
    MCvalues = {}
    R = {}
    TDvalues = {}
    NTD = {}
    Qvalues = {}
    NQ = {}
    #Initialization of the values
    #i iterates through the sum of user's cards. It is set to 22 if the user went bust. 
    #j iterates through the value of the dealer's first card. Ace is eleven. 
    #a1 is the number of Aces that the user has.
    #a2 denotes whether the dealer's first card is Ace. 
    states = []
    for i in range(2,23):
        for j in range(2,12):
            for a1 in range(0,5):
                for a2 in range(0,2):
                    s = (i,a1,j,a2)
                    states.append(s)
                    #utility computed by MC-learning
                    MCvalues[s] = 0
                    G[s] = []
                    #utility computed by TD-learning
                    TDvalues[s] = 0
                    NTD[s] = 0
                    #first element is Q value of "Hit", second element is Q value of "Stand"
                    Qvalues[s] = [0,0]
                    NQ[s] = 0
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealSum: sum of dealer's cards (including hidden one)
    #dealA: number of all dealer's Aces, 
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    #Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    playB = pygame.draw.rect(background, white, (435, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    autoPlay = False
    #Event loop
    while True:
        #Our state information does not take into account of number of cards
        #So it's ok to ignore the rule of winning if getting 5 cards without going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        if autoMC:
            #MC Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            MC_Policy_Evaluation(policy, states, 0.9, MCvalues, G)
        if autoTD:
            #TD Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            TD_Policy_Evaluation(policy, states, 0.9, TDvalues, NTD)
        if autoQL:
            #Q-Learning
            #For each state, compute the Q value of the action "Hit" and "Stand"
            Q_Learning(states, 0.9, Qvalues, NQ)
        if autoPlay:
            state = make_state(userSum, userA, dealFirst, dealAFirst)
            hitQ, standQ = Qvalues[state][0], Qvalues[state][1]
            decision = None
            if hitQ > standQ:
                decision = "hit"
            elif standQ > hitQ:
                decision = "stand"
            else:
                if userSum < 17:
                    decision = "hit"
                else:
                    decision = "stand"
            if (gameover or stand):
                #restart the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif not (gameover or stand) and decision == "hit":
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif not gameover and decision == "stand":
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #Clicking the white buttons can start or pause the learning processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and playB.collidepoint(pygame.mouse.get_pos()):
                autoPlay = not autoPlay
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand) and not autoPlay:
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()) and not autoPlay:
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()) and not autoPlay:
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %f' % MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %f' % TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %f (Stand) %f' % (Qvalues[state][0], Qvalues[state][1]) , 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(playTxt, (444, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()

if __name__ == '__main__':
    main()

