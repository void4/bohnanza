import os

import pygame

from game import Game, beanstats

game = Game(nplayers=5, debug=True)

pygame.init()
pygame.display.set_caption("Bohnanza")

w = 640*2
h = 480*2

clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))

imagecache = {}

scale = 0.2

for name in list(beanstats.keys()) + ["Rückseite"]:
	imagecache[name] = pygame.transform.scale(pygame.image.load(os.path.join("img", name + ".png")), (int(182*scale),int(280*scale)))

fontcache = {}

def loadfont(fontname, size):
	key = (fontname,size)
	if key not in fontcache:
		fontcache[key] = pygame.font.Font(fontname, size)
	return fontcache[key]

def text(xy, text, color=(255,255,255), fontname=pygame.font.get_default_font(), size=12):
	font = loadfont(fontname, size)
	text = font.render(text, True, color)
	screen.blit(text, xy)

color = (0, 0, 0)

i = 0
running = True
while running:
	screen.fill(color)

	#pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(i, i, 40, 30))
	i += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			print(pos)

	text((w//2,h//2), "test")

	for p, player in enumerate(game.players):
		px = p * 200
		py = 100
		for f, field in enumerate(player.fields):
			if len(field) > 0:
				cardtype = field[0]
				for c in range(len(field)):
					screen.blit(imagecache[cardtype], (px+50*f, py+100+10*c))

		for c, cardtype in enumerate(player.cards):
			if player.name == "Spieler1":
				screen.blit(imagecache[cardtype], (px+20*c, py))
			else:
				screen.blit(imagecache["Rückseite"], (px+20*c, py))

		for t, cardtype in enumerate(player.trading):
			screen.blit(imagecache[cardtype], (px+20*t, py+200))

		for d in range(len(game.deck)):
			screen.blit(imagecache["Rückseite"], (w//2, h//2+d*2))

		for d in range(len(game.discard)):
			screen.blit(imagecache["Rückseite"], (w//2+100, h//2+d*2))

	if game.winner is None:
		game.next()

	#print(pygame.key.get_pressed()[pygame.K_UP])

	pygame.display.flip()
	clock.tick(60)
