# Author : hejiachen23 a.k.a. 锕系元素镤
# LICENSE : GPL 3.0
import pygame
import sys
from typing import *
from functools import lru_cache

pygame.init()
screen = pygame.display.set_mode((720,780))
pygame.display.set_caption("联机游戏-中国象棋")

running = True
pieces_name = {"红":["帅","士","相","馬","炮","車","兵"],"黑":["将","士","象","馬","炮","車","卒"]}
pieces_image = {"红":[],"黑":[]}
piece_width = 60
for piece in pieces_name["红"]:
    pieces_image["红"].append(pygame.transform.scale(pygame.image.load(f"./Image/红-{piece}.png"),(piece_width,piece_width)))
for piece in pieces_name["黑"]:
    pieces_image["黑"].append(pygame.transform.scale(pygame.image.load(f"./Image/黑-{piece}.png"),(piece_width,piece_width)))
background = pygame.transform.scale(pygame.image.load("./Image/棋盘.png"),(632,720))
pygame.display.update()

class Piece:
    def __init__(self,mode:int,team:int,pos:Tuple[int,int]) -> None:
        self.mode = mode
        self.team = team # 0为红,1为黑
        self.pos = pos
        if self.team == 0:
            self.name = pieces_name["红"][self.mode]
            self.image = pieces_image["红"][self.mode]
        else:
            self.name = pieces_name["黑"][self.mode]
            self.image = pieces_image["黑"][self.mode]
        self.mask = pygame.mask.from_surface(self.image)

    def show(self) -> None:
        pos_x = 55
        pos_y = 30
        screen.blit(self.image,(pos_x+self.pos[0]*77-piece_width//2,pos_y+self.pos[1]*77-piece_width//2))
    
    # @lru_cache
    def get_route(self) -> List[Tuple[int,int]]:
        res = []
        # 帅/将
        if self.mode == 0:
            routes = [(self.pos[0]-1,self.pos[1]),(self.pos[0]+1,self.pos[1]),(self.pos[0],self.pos[1]-1),(self.pos[0],self.pos[1]+1)]
            col = Piece.get_column(self.pos[0])
            while None in col:
                col.remove(None)
            idx = col.index(self)
            if idx + 1 < len(col) and col[idx+1].mode == 0:
                res.append(col[idx+1].pos)
            if idx - 1 >= 0 and col[idx-1].mode == 0:
                res.append(col[idx-1].pos)
            if len(col) == 1 and col[0].mode == 0:
                res.append(col[0].pos)
            if self.team == 0:
                for i in routes:
                    if self.is_in_area(i,(3,7,5,9)) and self.is_not_team_piece(i):
                        res.append(i)
            else:
                for i in routes:
                    if self.is_in_area(i,(3,0,5,2)) and self.is_not_team_piece(i):
                        res.append(i)
            return res
        
        # 士
        elif self.mode == 1:
            routes = [(self.pos[0]-1,self.pos[1]-1),(self.pos[0]-1,self.pos[1]+1),(self.pos[0]+1,self.pos[1]-1),(self.pos[0]+1,self.pos[1]+1)]
            if self.team == 0:
                for i in routes:
                    if self.is_in_area(i,(3,7,5,9)) and self.is_not_team_piece(i):
                        res.append(i)
            else:
                for i in routes:
                    if self.is_in_area(i,(3,0,5,2)) and self.is_not_team_piece(i):
                        res.append(i)
            return res
        
        # 相/象
        elif self.mode == 2:
            routes = [(self.pos[0]-2,self.pos[1]-2),(self.pos[0]-2,self.pos[1]+2),(self.pos[0]+2,self.pos[1]-2),(self.pos[0]+2,self.pos[1]+2)]
            if self.team == 0:
                for i in routes:
                    if self.is_in_area(i,(0,5,8,9)) and self.is_not_team_piece(i):
                        res.append(i)
            else:
                for i in routes:
                    if self.is_in_area(i,(0,0,8,4)) and self.is_not_team_piece(i):
                        res.append(i)
            return res
        
        # 马
        elif self.mode == 3:
            routes = [(self.pos[0]-2,self.pos[1]-1),(self.pos[0]-2,self.pos[1]+1),(self.pos[0]+2,self.pos[1]-1),(self.pos[0]+2,self.pos[1]+1),(self.pos[0]-1,self.pos[1]-2),(self.pos[0]+1,self.pos[1]-2),(self.pos[0]-1,self.pos[1]+2),(self.pos[0]+1,self.pos[1]+2)]
            for i in routes:
                if self.is_in_area(i,(0,0,8,9)) and self.is_not_team_piece(i):
                    side = (i[0]-self.pos[0],i[1]-self.pos[1])
                    if abs(side[0]) > abs(side[1]):
                        if not chess_map[self.pos[1]][side[0]//2+self.pos[0]]:
                            res.append(i)
                    else:
                        if not chess_map[side[1]//2+self.pos[1]][self.pos[0]]:
                            res.append(i)
            return res
        
        # 炮
        elif self.mode == 4:
            row = Piece.get_row(self.pos[1])
            column = Piece.get_column(self.pos[0])
            x = self.pos[0]
            y = self.pos[1]
            left,right = x-1,x+1
            plflag,prflag = False,False
            for _ in range(len(row)-1):
                if left > -1:
                    if not row[left]:
                        if not plflag:
                            res.append((left,self.pos[1]))
                    else:
                        if not plflag:
                            plflag = True
                        else:
                            if row[left].team != self.team:
                                res.append((left,self.pos[1]))
                            left = -1
                    left -= 1
                if right < len(row):
                    if not row[right]:
                        if not prflag:
                            res.append((right,self.pos[1]))
                    else:
                        if not prflag:
                            prflag = True
                        else:
                            if row[right].team != self.team:
                                res.append((right,self.pos[1]))
                            right = len(row)
                    right += 1
            left,right = y-1,y+1
            plflag,prflag = False,False
            for _ in range(len(column)):
                if left>-1:
                    if not column[left]:
                        if not plflag:
                            res.append((self.pos[0],left))
                    else:
                        if not plflag:
                            plflag = True
                        else:
                            if column[left].team != self.team:
                                res.append((self.pos[0],left))
                            left = -1
                    left -= 1
                if right<len(column):
                    if not column[right]:
                        if not prflag:
                            res.append((self.pos[0],right))
                    else:
                        if not prflag:
                            prflag = True
                        else:
                            if column[right].team != self.team:
                                res.append((self.pos[0],right))
                            right = len(column)
                    right += 1
            return res
        
        # 車
        elif self.mode == 5:
            row = Piece.get_row(self.pos[1])
            column = Piece.get_column(self.pos[0])
            x = self.pos[0]
            y = self.pos[1]
            left,right = x-1,x+1
            plflag,prflag = False,False
            for _ in range(len(row)-1):
                if left > -1 and not plflag:
                    res.append((left,self.pos[1]))
                    if row[left]:
                        plflag = True
                        if row[left].team == self.team:
                            res.remove((left,self.pos[1]))
                    left -= 1
                if right < len(row) and not prflag:
                    res.append((right,self.pos[1]))
                    if row[right]:
                        prflag = True
                        if row[right].team == self.team:
                            res.remove((right,self.pos[1]))
                    right += 1
            left,right = y-1,y+1
            plflag,prflag = False,False
            for _ in range(len(column)):
                if left > -1 and not plflag:
                    res.append((self.pos[0],left))
                    if column[left]:
                        plflag = True
                        if column[left].team == self.team:
                            res.remove((self.pos[0],left))
                    left -= 1
                if right < len(column) and not prflag:
                    res.append((self.pos[0],right))
                    if column[right]:
                        prflag = True
                        if column[right].team == self.team:
                            res.remove((self.pos[0],right))
                    right += 1
            return res

        # 兵/卒
        elif self.mode == 6:
            if self.team == 0:
                if self.is_in_area(self.pos,(0,5,8,9)) and self.is_not_team_piece((self.pos[0],self.pos[1]-1)):
                    res.append((self.pos[0],self.pos[1]-1))
                else:
                    routes = [(self.pos[0],self.pos[1]-1),(self.pos[0]+1,self.pos[1]),(self.pos[0]-1,self.pos[1])]
                    for i in routes:
                        if self.is_in_area(i,(0,0,8,9)) and self.is_not_team_piece(i):
                            res.append(i)
            else:
                if self.is_in_area(self.pos,(0,0,8,4)) and self.is_not_team_piece((self.pos[0],self.pos[1]+1)):
                    res.append((self.pos[0],self.pos[1]+1))
                else:
                    routes = [(self.pos[0],self.pos[1]+1),(self.pos[0]+1,self.pos[1]),(self.pos[0]-1,self.pos[1])]
                    for i in routes:
                        if self.is_in_area(i,(0,0,8,9)) and self.is_not_team_piece(i):
                            res.append(i)
            return res
        return []
    
    def show_route(self) -> None:
        global route_surface,route_mask
        route_mask,route_surface = [],[]
        routes = self.get_route()
        draw()
        for i in routes:
            route_surface.append(pygame.Surface((20,20),pygame.SRCALPHA))
            route_surface[-1].set_colorkey((0,0,0))
            route_mask.append((pygame.mask.from_surface(route_surface[-1]),self))
            if not chess_map[i[1]][i[0]]:
                pygame.draw.circle(route_surface[-1],(0,0,255),(10,10),10)
            else:
                pygame.draw.circle(route_surface[-1],(255,0,0),(10,10),10)
            screen.blit(route_surface[-1],Piece.get_real_pos(i[0],i[1],(20,20)))
        pygame.display.update()

    def is_in_area(self,target:Tuple[int,int],area:Tuple[int,int,int,int]) -> bool:
        return target[0] >= area[0] and target[1] >= area[1] and target[0] <= area[2] and target[1] <= area[3]
    
    def is_not_team_piece(self,pos) -> bool:
        if chess_map[pos[1]][pos[0]]:
            return chess_map[pos[1]][pos[0]].team != self.team
        return True
    
    def is_clicked(self, mouse_pos):
        local_pos = (mouse_pos[0] - Piece.get_real_pos(self.pos[0],self.pos[1],(piece_width,piece_width))[0], mouse_pos[1] - Piece.get_real_pos(self.pos[0],self.pos[1],(piece_width,piece_width))[1])
        if 0 <= local_pos[0] < self.image.get_width() and 0 <= local_pos[1] < self.image.get_height():
            return self.mask.get_at(local_pos)
        return False

    def move(self,pos:Tuple[int,int]) -> None:
        global chess_map,route_mask,route_surface,rounds
        target = chess_map[pos[1]][pos[0]]
        if target:
            if target in red_pieces:
                red_pieces.remove(target)
                if target.mode == 0:
                    print("黑方胜利")
                    sys.exit()
            else:
                black_pieces.remove(target)
                if target.mode == 0:
                    print("红方胜利")
                    sys.exit()
        chess_map[self.pos[1]][self.pos[0]] = None
        chess_map[pos[1]][pos[0]] = self
        self.pos = pos[0],pos[1]
        route_surface,route_mask = [],[]
        draw()
        rounds += 1
    
    @staticmethod
    def get_column(column):
        return [n[column] for n in chess_map]
    
    @staticmethod
    def get_row(row):
        return chess_map[row]
    
    @staticmethod
    def get_real_pos(x:int,y:int,size:Tuple[int,int]) -> Tuple[int,int]:
        return 55+x*77-size[0]//2,30+y*77-size[1]//2

chess_map = [
    [ 5, 3, 2, 1, 0, 1, 2, 3, 5],
    [-1,-1,-1,-1,-1,-1,-1,-1,-1],
    [-1, 4,-1,-1,-1,-1,-1, 4,-1],
    [ 6,-1, 6,-1, 6,-1, 6,-1, 6],
    [-1,-1,-1,-1,-1,-1,-1,-1,-1],
    [-1,-1,-1,-1,-1,-1,-1,-1,-1],
    [ 6,-1, 6,-1, 6,-1, 6,-1, 6],
    [-1, 4,-1,-1,-1,-1,-1, 4,-1],
    [-1,-1,-1,-1,-1,-1,-1,-1,-1],
    [ 5, 3, 2, 1, 0, 1, 2, 3, 5],
]

# chess_map = [
#     [ 5, 3, 2, 1, 0, 1, 2, 3, 5],
#     [-1,-1,-1,-1,-1,-1,-1,-1,-1],
#     [-1, 4,-1,-1,-1,-1,-1, 4,-1],
#     [ 6,-1, 6,-1, 6,-1, 6,-1, 6],
#     [-1,-1,-1,-1,-1,-1,-1,-1,-1],
#     [ 6,-1,-1,-1,-1,-1,-1,-1,-1],
#     [-1,-1, 6,-1, 6,-1, 6,-1, 6],
#     [-1, 4,-1,-1,-1,-1,-1, 4,-1],
#     [-1,-1,-1,-1,-1,-1,-1,-1,-1],
#     [ 5, 3, 2, 1, 0, 1, 2, 3, 5],
# ]

chess_map:List[Piece]
for i in range(10):
    for j in range(9):
        if chess_map[i][j] == -1:
            chess_map[i][j] = None
        else:
            if i > 4:
                chess_map[i][j] = Piece(chess_map[i][j],0,(j,i))
            else:
                chess_map[i][j] = Piece(chess_map[i][j],1,(j,i))

red_pieces = [chess_map[9][4],chess_map[9][3],chess_map[9][5],chess_map[9][2],chess_map[9][6],chess_map[9][1],chess_map[9][7],chess_map[9][0],chess_map[9][8],chess_map[7][1],chess_map[7][7],chess_map[6][0],chess_map[6][2],chess_map[6][4],chess_map[6][6],chess_map[6][8]]
black_pieces = [chess_map[0][4],chess_map[0][3],chess_map[0][5],chess_map[0][2],chess_map[0][6],chess_map[0][1],chess_map[0][7],chess_map[0][0],chess_map[0][8],chess_map[2][1],chess_map[2][7],chess_map[3][0],chess_map[3][2],chess_map[3][4],chess_map[3][6],chess_map[3][8]]
route_mask = []
route_surface = []
general = (red_pieces[0],black_pieces[0])

def draw():
    screen.fill((255,255,255))
    screen.blit(background,(44,20))
    for i in chess_map:
        for j in i:
            if j:
                j.show()
    pygame.display.update()

draw()
rounds = 0
flag = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rounds%2 == 0:
                for i in red_pieces:
                    if i.is_clicked(event.pos):
                        if not flag:
                            i.show_route()
                            flag = True
                        else:
                            draw()
                            flag = False
            else:
                for i in black_pieces:
                    if i.is_clicked(event.pos):
                        if not flag:
                            i.show_route()
                            flag = True
                        else:
                            draw()
                            flag = False
            for i,j in enumerate(route_mask):
                routes = j[1].get_route()
                r_pos = Piece.get_real_pos(routes[i][0],routes[i][1],(20,20))
                if 0 <= event.pos[0] - r_pos[0]  < 20 and 0 <= event.pos[1] - r_pos[1] < 20:
                    if j[0].get_at((event.pos[0] - r_pos[0], event.pos[1] - r_pos[1])):
                        j[1].move(routes[i])
                        flag = False
                        break
