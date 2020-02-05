# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
# Os comentarios presentes neste codigo foram traduzidos pela academica de Ciencia da Computacao - Isadora Garcia Ferrao (Universidade Federal do Pampa, Campus Alegrete, Brasil).

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
     Um agente reflexo escolhe uma acao em cada ponto de escolha examinando
     suas alternativas atraves de uma funcao de avaliacao de estado.
     O codigo abaixo e fornecido como um guia. Voce pode mudar
     de qualquer forma que voce entender, desde que voce nao toque em nosso metodo
     Cabecalhos
  """


  def getAction(self, gameState):
    """
     Voce nao precisa alterar esse metodo, mas voce e bem vindo.

     GetAction escolhe entre as melhores opcoes de acordo com a funcao de avaliacao.
     Assim como no projeto anterior, getAction tem um GameState e retorna
     alguns directions X para algum X no conjunto {norte, sul, oeste, leste, parada}
    """

    # Coletar movimentos legais e estados sucessores
    legalMoves = gameState.getLegalActions()

    # Coletar uma das melhores acoes
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Escolher aleatoriamente entre os melhores

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design uma funcao de avaliacao melhor aqui.

    A funcao de avaliacao assume o sucessor atual e proposto
    GameStates (pacman.py) e retorna um numero, onde numeros maiores sao melhores.

    O codigo abaixo extrai algumas informacoes uteis do estado, como o
    restante alimento (oldFood) e posicao Pacman apos a mudanca (newPos).
    NewScaredTimes mantem o numero de movimentos que cada fantasma permanecera
    assustado por causa de Pacman ter comido um pellet poder.

    Imprima essas variaveis para ver o que voce esta recebendo, em seguida, combina-los
    para criar uma funcao de avaliacao magistral.
    """

    # Informacoes uteis que voce pode extrair de um GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action) # Proximo estado
    newPos = successorGameState.getPacmanPosition() #posicao Pacman apos a mudanca
    oldFood = currentGameState.getFood() #Restante do alimento
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates] #Numero de movimentos


    if successorGameState.isWin():
        return float("inf") - 20
    ghostposition = currentGameState.getGhostPosition(1)
    distfromghost = util.manhattanDistance(ghostposition, newPos)
    score = max(distfromghost, 3) + successorGameState.getScore()
    foodlist = oldFood.asList()
    closestfood = 100
    for foodpos in foodlist:
        thisdist = util.manhattanDistance(foodpos, newPos)
        if (thisdist < closestfood):
            closestfood = thisdist
    if (currentGameState.getNumFood() > successorGameState.getNumFood()):
        score += 100
    if action == Directions.STOP:
        score -= 3
    score -= 3 * closestfood
    capsuleplaces = currentGameState.getCapsules()
    if successorGameState.getPacmanPosition() in capsuleplaces:
        score += 120
    return score
    return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
  """
    Essa funcao de avaliacao padrao apenas retorna a pontuacao do estado.
    A pontuacao e a mesma exibida na GUI do Pacman.

    Esta funcao de avaliacao destina-se a ser utilizada com agentes de pesquisa
    (Nao agentes de reflexo).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    Esta classe fornece alguns elementos comuns a todos os
    multi-agente pesquisadores. Todos os metodos aqui definidos estarao disponiveis
    para o MinimaxPacmanAgent, AlphaBetaPacmanAgent e ExpectimaxPacmanAgent.

    Voce * nao * precisa fazer qualquer alteracao aqui, mas voce pode, se voce quiser
    adicionar funcionalidade a todos os seus agentes de busca adversarial. Por favor nao
    remover qualquer coisa, entretanto.

    Nota: esta e uma classe abstrata: uma que nao deve ser instanciada. Esta
    apenas parcialmente especificado e concebido para ser alargado. Agent (game.py)
    e outra classe abstrata.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman e sempre agente indice 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)
    self.agentCount = 0

  def result(self,state,agent,action):
    return state.generateSuccessor(agent,action)

  def utility(self,state):
    return self.evaluationFunction(state)

  def terminalTest(self,state,depth):
    if depth == (self.depth*self.agentCount) or state.isWin() or state.isLose():
        return True
    else:
        return False


class MinimaxAgent(MultiAgentSearchAgent):
  """
    Seu agente minimax (questao 2)
  """

  def getAction(self, gameState):
    """
       Retorna a acao minimax do gameState atual usando self.depth
       E self.evaluationFunction.

       Aqui estao algumas chamadas de metodo que podem ser uteis ao implementar minimax.

       GameState.getLegalActions (agentIndex):
         Retorna uma lista de acoes legais para um agente
         AgentIndex = 0 significa Pacman, fantasmas sao > = 1

       Directions.STOP:
         A direcao de parada, que e sempre legal

       GameState.generateSuccessor (agentIndex, acao):
         Retorna o estado do jogo sucessor apos um agente tomar uma acao

       GameState.getNumAgents ():
         Retorna o numero total de agentes no jogo
    """

    def minvalue(gameState, depth, agentindex, numghosts): #agente de busca competitivo
        "numghosts = len(gameState.getGhostStates())"
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = float("inf")
        legalActions = gameState.getLegalActions(agentindex)
        if agentindex == numghosts:
            for action in legalActions:
                v = min(v, maxvalue(gameState.generateSuccessor(agentindex, action), depth - 1, numghosts))
        else:
            for action in legalActions:
                v = min(v, minvalue(gameState.generateSuccessor(agentindex, action), depth, agentindex + 1, numghosts))
        return v

    def maxvalue(gameState, depth, numghosts):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = -(float("inf"))
        legalActions = gameState.getLegalActions(0)
        for action in legalActions:
            v = max(v, minvalue(gameState.generateSuccessor(0, action), depth - 1, 1, numghosts))
        return v
    
    legalActions = gameState.getLegalActions()
    numghosts = gameState.getNumAgents() - 1
    bestaction = Directions.STOP
    score = -(float("inf"))
    for action in legalActions:
        nextState = gameState.generateSuccessor(0, action)
        prevscore = score
        score = max(score, minvalue(nextState, self.depth, 1, numghosts))
        if score > prevscore:
            bestaction = action
    return bestaction
        
    util.raiseNotDefined()
    

class AlphaBetaAgent(MultiAgentSearchAgent): #Explorar a arvore minimax de maneira mais eficiente
  """
    Seu agente minimax com alfa-beta (questao 3)
  """

  def getAction(self, gameState):
    """
      Retorna a acao minimax usando self.depth e self.evaluationFunction
    """
    def maxvalue(gameState, depth, numghosts):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = -(float("inf"))
        legalActions = gameState.getLegalActions(0)
        for action in legalActions:
            v = max(v, minvalue(gameState.generateSuccessor(0, action), depth - 1, 1, numghosts))
        return v
    
    def minvalue(gameState, depth, agentindex, numghosts):
        "numghosts = len(gameState.getGhostStates())"
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = float("inf")
        legalActions = gameState.getLegalActions(agentindex)
        if agentindex == numghosts:
            for action in legalActions:
                v = min(v, maxvalue(gameState.generateSuccessor(agentindex, action), depth - 1, numghosts))
        else:
            for action in legalActions:
                v = min(v, minvalue(gameState.generateSuccessor(agentindex, action), depth, agentindex + 1, numghosts))
        return v
    legalActions = gameState.getLegalActions()
    numghosts = gameState.getNumAgents() - 1
    bestaction = Directions.STOP
    score = -(float("inf"))
    for action in legalActions:
        nextState = gameState.generateSuccessor(0, action)
        prevscore = score
        score = max(score, minvalue(nextState, self.depth, 1, numghosts))
        if score > prevscore:
            bestaction = action
    return bestaction
        
    util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Seu agente Expectimax (questao 4)
  """

  def getAction(self, gameState):
    """
     Retorna a acao expectimax usando self.depth e self.Evaluation 
     Funcao Todos os fantasmas devem ser modelados como escolhendo uniformemente aleatoriamente de seus movimentos legais.
    """

    def expectedvalue(gameState, agentindex, depth):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        numghosts = gameState.getNumAgents() - 1
        legalActions = gameState.getLegalActions(agentindex)
        numactions = len(legalActions)
        totalvalue = 0
        for action in legalActions:
            nextState = gameState.generateSuccessor(agentindex, action)
            if (agentindex == numghosts):
                totalvalue += maxvalue(nextState, depth - 1)
            else:
                totalvalue += expectedvalue(nextState, agentindex + 1, depth)
        return totalvalue / numactions
    def maxvalue(gameState, depth):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        legalActions = gameState.getLegalActions(0)
        bestAction = Directions.STOP
        score = -(float("inf"))
        for action in legalActions:
            prevscore = score
            nextState = gameState.generateSuccessor(0, action)
            score = max(score, expectedvalue(nextState, 1, depth))
        return score
    if gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    legalActions = gameState.getLegalActions(0)
    bestaction = Directions.STOP
    score = -(float("inf"))
    for action in legalActions:
        nextState = gameState.generateSuccessor(0, action)
        prevscore = score
        score = max(score, expectedvalue(nextState, 1, self.depth))
        if score > prevscore:
            bestaction = action
    return bestaction
    
    util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    Sua extrema caca fantasma, pellet-nabbing, comida-gobbling, imparavel
    Avaliacao (questao 5).

     DESCRICAO: <escrever algo aqui para que saibamos o que voce fez>
  """

  util.raiseNotDefined()

# Abreviacao
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Seu agente para o mini-concurso
  """

  def getAction(self, gameState):
    """
      Retorna uma acao. Voce pode usar qualquer metodo que voce quiser e pesquisar a qualquer profundidade que voce deseja.
      Basta lembrar que o mini-concurso e cronometrado, entao voce tem que trocar velocidade e computacao.

      Os fantasmas nao se comportam mais aleatoriamente, mas tambem nao sao perfeitos - eles costumam
      Basta fazer uma linha reta em direcao a Pacman (ou longe dele, se eles estao com medo!)
    """
    "*** Seu codigo aqui ***"
    util.raiseNotDefined()

