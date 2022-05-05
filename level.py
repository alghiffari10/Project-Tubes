import pygame
from enemy import Enemy
from support import import_csv_layout, import_cut_graphics
from settings import tile_size,screen_height, screen_width
from tiles import Coin, Crate, StaticTile, Tile, Tree
from decoration import Clouds, Sky, Water   
from player import Player
from particles import ParticleEffect
from game_data import levels
class Level:
    def __init__(self,current_level,surface,create_overworld):
        # general setup
        self.__display_surface = surface
        self.__world_shift = 0
        self.__current_x = None


        #overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # player 
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        #dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        
        #terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprite = self.create_tile_group(terrain_layout,'terrain')

        # crates
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprite = self.create_tile_group(crates_layout,'crates')


        #bg tree
        bgtree_layout = import_csv_layout(level_data['bg tree'])
        self.bgtree_sprite = self.create_tile_group(bgtree_layout,'bg tree')

        # coins
        coins_layout = import_csv_layout(level_data['coins'])
        self.coins_sprite = self.create_tile_group(coins_layout,'coins')

        # enemies
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprite = self.create_tile_group(enemies_layout,'enemies')

        #constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprite = self.create_tile_group(constraint_layout,'constraints')

        #decoration 
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 20,level_width)
        self.clouds = Clouds(400,level_width,30)
        

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    if type == 'terrain':
                        #interaksi antar object
                        terrain_tile_list = import_cut_graphics('Tiles/1.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                    if type == 'crates':
                        #interaksi antar object
                        sprite = Crate(tile_size,x,y)
                    
                    if type == 'coins':
                        #interaksi antar object
                        if val == '0': sprite = Coin(tile_size,x,y,'coins/gold')
                        if val == '1': sprite = Coin(tile_size,x,y,'coins/silver')
                    
                    
                    if type == 'bg tree':
                        #interaksi antar object
                       if val == '0': sprite = Tree(tile_size,x,y,'decoration/Tree_2.png')
                       if val == '1': sprite = Tree(tile_size,x,y,'decoration/Tree_3.png')
                    
                    if type == 'enemies':
                        #interaksi antar object
                        sprite = Enemy(tile_size,x,y)
                    
                    if type == 'constraints':
                        #interaksi antar object
                        sprite = Tile(tile_size,x,y)
                    
                    sprite_group.add(sprite)                  
                        
        return sprite_group

    def player_setup(self,layout):
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    #interaksi antar object
                    sprite = Player((x,y),self.__display_surface,self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('decoration/Sign_1.png').convert_alpha()
                    #interaksi antar object
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)
        
    def enemy_collision_reverse(self):
        for enemy in self.enemies_sprite.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprite,False):
                enemy.reverse()
                
    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(7,2)
        else:
            pos += pygame.math.Vector2(7,-5)
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprite = self.terrain_sprite.sprites() + self.crates_sprite.sprites()
        for sprite in collidable_sprite:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: 
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.__current_x = player.rect.left
                    player.direction.x = 0
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.direction.x = 0
                    player.on_right = True
                    self.__current_x = player.rect.right
        
        if player.on_left and (player.rect.left < self.__current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.__current_x or player.direction.x <= 0):
            player.on_right = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width / 4 and direction_x < 0:
            self.__world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.__world_shift = -8
            player.speed = 0
        else:
            self.__world_shift = 0
            player.speed = 8
            
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)
            
    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        for sprite in self.terrain_sprite.sprites() + self.crates_sprite.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: 
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
                    
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False 
    
    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)
    
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)
            
    

    def run(self):

        #sky
        self.sky.draw(self.__display_surface)
        self.clouds.draw(self.__display_surface,self.__world_shift)
        #Tree
        self.bgtree_sprite.update(self.__world_shift)
        self.bgtree_sprite.draw(self.__display_surface)
        #terrain
        self.terrain_sprite.update(self.__world_shift)
        self.terrain_sprite.draw(self.__display_surface)
        #enemy
        self.enemies_sprite.update(self.__world_shift)
        self.constraint_sprite.update(self.__world_shift)
        self.enemy_collision_reverse()
        self.enemies_sprite.draw(self.__display_surface)
        #crates
        self.crates_sprite.update(self.__world_shift)
        self.crates_sprite.draw(self.__display_surface)
        #coins
        self.coins_sprite.update(self.__world_shift)
        self.coins_sprite.draw(self.__display_surface)

        # dust particles 
        self.dust_sprite.update(self.__world_shift)
        self.dust_sprite.draw(self.__display_surface)

        #player
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.scroll_x()
        self.player.draw(self.__display_surface)
        self.goal.update(self.__world_shift)
        self.goal.draw(self.__display_surface)

        self.check_death()
        self.check_win()

        #Water
        self.water.draw(self.__display_surface,self.__world_shift)

