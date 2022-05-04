import pygame 
from tiles import AnimatedTile
from random import randint

class Enemy(AnimatedTile):
	def __init__(self,size,x,y):
		super().__init__(size,x,y,'enemies/run')
		self.__speed = randint(3,5)
		self.rect.y += size - self.image.get_size()[1]

	def move(self):
		self.rect.x += self.__speed

	def reverse_image(self):
		if self.__speed > 0:
			self.image = pygame.transform.flip(self.image,True,False)

	def reverse(self):
		self.__speed *= -1

	def update(self,shift):
		self.rect.x += shift
		self.animate()
		self.move()
		self.reverse_image()