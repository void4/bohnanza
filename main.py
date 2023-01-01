from random import shuffle, choice
from collections import Counter

from dotdict import DotDict

BEANTEXT = """Coffee Bean	Kaffeebohne	24	4	7	10	12
Wax Bean	Weinbrandbohne	22	4	7	9	11
Blue Bean	Blaue Bohne	20	4	6	8	10
Chili Bean	Feuerbohne	18	3	6	8	9
Stink Bean	Saubohne	16	3	5	7	8
Green Bean	Brechbohne	14	3	5	6	7
Soy Bean	Sojabohne	12	2	4	6	7
Black-eyed Bean	Augenbohne	10	2	4	5	6
Red Bean	Rote Bohne	8	2	3	4	5
Garden Bean	Gartenbohne	6	-	2	3	-
Cocoa Bean	Kakaobohne	4	2	-	3	4"""

beanstats = {}

def dashtonone(v):
	if v == "-":
		return None
	else:
		return int(v)

for line in BEANTEXT.split("\n"):
	name_en, name, total, h1, h2, h3, h4 = line.split("\t")
	print(name)
	beanstats[name] = {
		"name_en": name_en,
		"name": name,
		"total": int(total),
		"h1": dashtonone(h1),
		"h2": dashtonone(h2),
		"h3": dashtonone(h3),
		"h4": dashtonone(h4),
	}

beanstats = DotDict(beanstats)

def t(s):
	return s

def howmanycoins(cardtype, cardnum):
	if cardnum == 0:
		return 0

	bs = beanstats[cardtype]
	lastindex = None
	for index, count in enumerate([bs.h1, bs.h2, bs.h3, bs.h4]):
		if count is not None and cardnum >= count:
			lastindex = index

	if lastindex is None:
		coins = 0
	else:
		coins = lastindex + 1
	return coins

ALGO_RANDOM, ALGO_SMART = range(2)

class Player:
	def __init__(self, name, algo=ALGO_RANDOM):
		self.name = name
		self.algo = algo
		self.cards = []
		self.fields = [[], []]
		self.treasury = 0
		self.trading = []

	def canplant(self):
		if all(map(lambda field:len(field)==1, self.fields)):
			return list(range(len(self.fields)))
		else:
			return [f for f, field in enumerate(self.fields) if len(field) != 1]

	def harvest(self, index):
		toreturn = []
		field = self.fields[index]
		if len(field) > 0:
			cardtype = field[0]
			cardnum = len(field)
			self.treasury += howmanycoins(cardtype, cardnum)
			toreturn = self.fields[index]
			self.fields[index] = []
		return toreturn

	def plant(self, index, toplant):
		field = self.fields[index]
		toreturn = []
		if len(field) > 0:
			if field[0] != toplant:
				toreturn = self.harvest(index)
				self.fields[index] = [toplant]
			else:
				field.append(toplant)
		else:
			self.fields[index] = [toplant]

		return toreturn

	def choice(self, toplant):
		if self.algo == ALGO_RANDOM:
			return self.choice_random(toplant)
		elif self.algo == ALGO_SMART:
			return self.choice_smart(toplant)
		else:
			raise Exception(f"No such algorithm: {self.algo}")

	def choice_random(self, toplant):
		return choice(self.canplant())

	def choice_smart(self, toplant):
		canplant = self.canplant()
		sameplant_fields = [index for index in canplant if len(self.fields[index]) > 0 and self.fields[index][0] == toplant]
		empty_fields = [index for index in canplant if len(self.fields[index]) == 0]

		if len(sameplant_fields) > 0:
			return sameplant_fields[0]

		if len(empty_fields) > 0:
			return empty_fields[0]

		return choice(canplant)

	def hasPlanted(self, card):
		return card in [field[0] for field in self.fields if len(field)>0]

	def getOffers(self):
		if self.algo == ALGO_RANDOM:
			return []
		elif self.algo == ALGO_SMART:
			return self.getOffers_smart()
		else:
			raise Exception(f"No such algorithm: {self.algo}")

	def getOffers_smart(self):
		return [card for card in self.trading if not self.hasPlanted(card)]

	def getCounterOffers(self, offers):
		if self.algo == ALGO_RANDOM:
			return []
		elif self.algo == ALGO_SMART:
			return self.getCounterOffers_smart(offers)
		else:
			raise Exception(f"No such algorithm: {self.algo}")

	def getCounterOffers_smart(self, offers):
		counteroffer = []
		for card in offers:
			if self.hasPlanted(card):
				for mycard in self.cards:
					if not self.hasPlanted(mycard):
						counteroffer.append({"buy": card, "sell": mycard})
				counteroffer.append({"buy": card, "sell": None})
		return counteroffer

	def considerOffers(self, counteroffers):
		if self.algo == ALGO_RANDOM:
			return []
		elif self.algo == ALGO_SMART:
			return self.considerOffers_smart(counteroffers)
		else:
			raise Exception(f"No such algorithm: {self.algo}")

	def considerOffers_smart(self, counteroffers):
		for player, counteroffer in counteroffers.items():
			for coffer in counteroffer:
				if self.hasPlanted(coffer["sell"]) or coffer["sell"] is None:#TODO should consider good trade first
					if coffer["buy"] in self.trading and coffer["sell"] in player.cards:
						print(f"{self.name} verkauft seine {coffer['buy']} an {player.name} für {coffer['sell']}")
						self.trading.remove(coffer["buy"])
						player.cards.append(coffer["buy"])
						if coffer["sell"] is not None:
							self.trading.append(coffer["sell"])
							player.cards.remove(coffer["sell"])

INITIALCARDS = 5

class Game:
	def __init__(self, nplayers=5, debug=False):
		self.debug = debug

		self.round = 0

		self.players = [Player(f"Player{n}", ALGO_RANDOM if n>1 else ALGO_SMART) for n in range(nplayers)]
		self.turn = 0

		self.totalturns = 0

		self.deck = []
		self.discard = []

		for bs in beanstats.values():
			self.deck += [bs["name"] for t in range(bs["total"])]

		shuffle(self.deck)
		print(self.deck)
		print(len(self.deck))

		for player in self.players:
			for i in range(INITIALCARDS):
				player.cards.append(self.deck.pop(0))

		self.winner = None

	def newround(self):

		shuffle(self.discard)
		self.deck = self.discard
		self.discard = []
		self.round += 1

		if self.round == 3:
			# Game end

			for player in self.players:
				for index in range(len(player.fields)):
					player.harvest(index)

			self.winner = max(self.players, key=lambda player:player.treasury)
			print(f"{self.winner.name} hat das Spiel nach {self.totalturns} Runden gewonnen!")
			for name, coins in Counter({player.name:player.treasury for player in self.players}).most_common():
				print(f"{coins}\t{name}")
			return True

		return False

	def draw(self, n=1):

		if n == 1:
			cardtype = self.deck.pop(0)
			if len(self.deck) == 0:
				gameend = self.newround()
				if gameend:
					return None
			return cardtype
		else:
			newround = False
			if len(self.deck) < n:
				n = len(self.deck)
				newround = True
			cards = [self.deck.pop(0) for i in range(n)]
			if newround:
				gameend = self.newround()
				if gameend:
					return None

			return cards

	def next(self):
		active = self.players[self.turn]
		toplant = active.cards.pop(0)

		index = active.choice(toplant)
		self.discard += active.plant(index, toplant)
		print(f"{active.name} {t('pflanzt')} {toplant}")

		index = active.choice(toplant)
		self.discard += active.plant(index, toplant)
		print(f"{active.name} {t('pflanzt')} {toplant}")

		drawn = self.draw(2)
		if drawn is None:
			return
		active.trading = drawn
		# TODO trading
		offers = active.getOffers()

		if offers:
			print(f"{active.name} bietet {offers}")
			counteroffers = {}
			for player in self.players:
				if player == active:
					continue
				counteroffer = player.getCounterOffers(offers)
				if len(counteroffer) > 0:
					print(f"{player.name} bietet {counteroffer}")
				counteroffers[player] = counteroffer

			active.considerOffers(counteroffers)
		else:
			print(f"{active.name} möchte nicht handeln")

		while len(active.trading) > 0:
			toplant = active.trading.pop(0)
			index = active.choice(toplant)
			self.discard += active.plant(index, toplant)
			print(f"{active.name} {t('pflanzt')} {toplant}")

		drawn = self.draw(2)
		if drawn is None:
			return
		active.cards += drawn

		self.turn = (self.turn + 1) % len(self.players)
		self.totalturns += 1

game = Game(nplayers=5, debug=True)

while game.winner is None:
	game.next()
