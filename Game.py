import pygame
import math
from pygame.locals import *
import random

        
def getRestrictedPos(fieldW,fieldH):
    return(random.randrange(0,fieldW),random.randrange(0,fieldH))

def loadImage(filePath):
    return pygame.image.load("assets/"+filePath).convert_alpha()

def loadSound(filePath):
    return pygame.mixer.Sound("assets/"+filePath)

def getRandomPoint(maxX,maxY):
    x=random.randrange(0,maxX)
    y=random.randrange(0,maxY)
    return Vector2(x,y)

def getMoveToPointVel(curPos,targetPos,speed = 1):
    toPoint=Vector2(targetPos.x-curPos.x,targetPos.y-curPos.y)
    toPointMag=toPoint.magnitude()
    if toPointMag < speed:
        return toPoint
    toPointNorm=Vector2(toPoint.x/toPointMag,toPoint.y/toPointMag)
    return Vector2(toPointNorm.x*speed,toPointNorm.y*speed)

class GameRect:
    def __init__(self,nx,ny,nw,nh):
        self.x=nx
        self.y=ny
        self.w=nw
        self.h=nh
    def pointInside(self,x,y):
        return (x > self.x) & (x < self.x + self.w) & (y > self.y) &(y < self.y + self.h)
        
class Vector2:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def magnitude(self):
        return math.sqrt(self.x*self.x+self.y*self.y)
    def equals(self,v2):
        tol=2
        return (abs(self.x-v2.x)<tol) & (abs(self.y-v2.y)<tol)
    def toString(self):
        return str(self.x)+","+str(self.y)
    def distanceTo(self,v2):
        toPoint=Vector2(v2.x-self.x,v2.y-self.y)
        toPointMag=toPoint.magnitude()
        return toPointMag

class EntityBehavior:
    def __init__(self):
        self._time=0
        self._timeLimit=0
        self._velocity=Vector2(0,0)
    def getVelocity(self):
        return self._velocity
    def onUpdate(self):
        self._time+=1
    def isDone(self):
        if(self._timeLimit > 0):
            return self._time > self._timeLimit
        return False
    
class BehaviorMoveToPoint(EntityBehavior):
    def __init__(self,startPoint = None, startPointFunc = None, targetPoint = None, targetPointFunc = None, speed = 0, stopFunc = None):
        EntityBehavior.__init__(self)
        self._startPos=startPoint
        self._targetPos=targetPoint
        self._startPointFunc=startPointFunc
        self._targetPointFunc=targetPointFunc
        self._speed=speed
        self._curPos=startPoint
        self._stopFunc=stopFunc
    def onUpdate(self):
        if self._targetPointFunc != None:
            target=self._targetPointFunc()
        else:
            target=self._targetPos
        if self._startPointFunc != None:
            curPos=self._startPointFunc()
        else:
            curPos=self._curPos
            self._curPos.x+=self._velocity.x
            self._curPos.y+=self._velocity.y
        self._velocity=getMoveToPointVel(curPos,target,self._speed)
    def isDone(self):
        if self._stopFunc != None:
            if self._stopFunc():
                return True;
        if self._startPointFunc != None:
            curPos=self._startPointFunc()
        else:
            curPos=self._curPos
            self._curPos.x+=self._velocity.x
            self._curPos.y+=self._velocity.y
        if self._targetPointFunc != None:
            target=self._targetPointFunc()
        else:
            target=self._targetPos
        return curPos.equals(target)
        #return self._velocity.equals(Vector2(0,0))
        #return (self._velocity.x < 0.02) & (self._velocity.y < 0.02)

class BehaviorWait(EntityBehavior):
    def __init__(self,waitTime):
        EntityBehavior.__init__(self)
        self._timeLimit=waitTime
        self._velocity=Vector2(0,0)
    def onUpdate(self):
        EntityBehavior.onUpdate(self)
        self._velocity=Vector2(0,0)
        
class Visual:
    def __init__(self):
        self._surface = None
        self._xFlip = False
        self._yFlip = False
    def getSurface(self):
        return self._surface
    def setBaseSurface(self,filePath):
        self._surface = loadImage(filePath)
    def setXFlip(self,flip):
        if self._xFlip != flip:
            self._xFlip = flip
            self._surface=pygame.transform.flip(self._surface, True, False)
    def setYFlip(self,flip):
        if self._yFlip != flip:
            self._yFlip = flip
            self._surface=pygame.transform.flip(self._surface, False, True)
    
class Transform:
    def __init__(self):
        self._pos=Vector2(0,0)
        self._velocity=Vector2(0,0)
        
    def setPos(self,p):
        self._pos=p
    def setPosXY(self,x,y):
        self._pos=Vector2(x,y)
    def getPos(self):
        return self._pos
    
    def setVelocity(self,vel):
        self._velocity=vel
    def setVelocityXY(self,x,y):
        self._velocity.x=x
        self._velocity.y=y
    def getVelocity(self):
        return self._velocity
    
    def onUpdate(self):
        self._pos.x+=self._velocity.x
        self._pos.y+=self._velocity.y

class GameEntity:
    def __init__(self,game = None):
        self.transform=Transform()
        self.visual=Visual()
        self._game=game
    def setup(self,imageFile = "", x = 0, y = 0):
        self.transform.setPosXY(x,y)
        self.visual.setBaseSurface(imageFile)
       #$ self.colRect=colRect
        #self.colRect=[] #localspace
    def getColRect(self): #worldspace
        return GameRect(self.x+self.colRect.x,self.y+self.colRect.y,self.colRect.w,self.colRect.h)
    def onUpdate(self):
        self.transform.onUpdate()
        pass

class BubbleMaker:
    def __init__(self,game,period,bubbleSrcFunc):
        self._time=random.randrange(0,period)
        self._period=period
        self._game=game
        self._bubbleSrcFunc=bubbleSrcFunc
    def onUpdate(self):
        self._time+=1
        if self._time>self._period:
            self._time=0
            bubble = Bubble(self._game)
            bubble.transform.setPos(self._bubbleSrcFunc())
            self._game.addToScene(bubble)
            
class Fish(GameEntity):
    def __init__(self,game):
        GameEntity.__init__(self,game)
        self.__speed=1
        self.__foodSpeed=2
        fishImage='fish1.png'
        self.setup(fishImage)
        self._curBehavior=None
        self._facingRight=True
        self._bubbleMaker=BubbleMaker(game,280,self._getBubbleSrcPos)
        self._targetFood=None
    def _getMouthPos(self):
        myPos=self.transform.getPos()
        xOffset=10
        yOffset=40
        if self._facingRight:
            xOffset=90
        return Vector2(myPos.x+xOffset,myPos.y+yOffset)
    def _getBubbleSrcPos(self):
        return self._getMouthPos()
    def _faceVelocity(self):
        velX=self.transform.getVelocity().x
        if(velX<0):
            self.visual.setXFlip(True)
            self._facingRight=False
        elif(velX>0):
            self.visual.setXFlip(False)
            self._facingRight=True
    def getSize(self):
        return 100,100
    def onUpdate(self):
        fishSize=self.getSize()
        if (self._curBehavior == None) or (self._curBehavior.isDone()):
            if self._targetFood != None:
                self._targetFood.eat()
                self._targetFood = None
            newB=random.randrange(0,2)
            if newB==0:
                waitTime=30+random.randrange(30)
                self._curBehavior=BehaviorWait(waitTime)
            elif newB==1:
                newTargetPos=getRandomPoint(self._game.aquariumSize[0]-fishSize[0],self._game.aquariumSize[1]-fishSize[1])
                self._curBehavior=BehaviorMoveToPoint(startPointFunc=self.transform.getPos,targetPoint=newTargetPos,speed=self.__speed)
                
        foodList=self._game.getAllFood(self._getMouthPos(),200)
        if (len(foodList)>0) & (self._targetFood==None):
            self._targetFood = foodList[random.randrange(0,len(foodList))]
            self._curBehavior=BehaviorMoveToPoint(startPointFunc=self._getMouthPos,targetPointFunc=self._targetFood.transform.getPos,speed=self.__foodSpeed,stopFunc=self._targetFood.isDead)
  
        self._curBehavior.onUpdate()
        newVel=self._curBehavior.getVelocity()
        
        dontTurn=False
        if (self._targetFood!=None):
            foodX=self._targetFood.transform.getPos().x
            if (foodX > self.transform.getPos().x) & (foodX <= self.transform.getPos().x + fishSize[0]):
                dontTurn=True
        if not dontTurn:
            self._faceVelocity()
        self.transform.setVelocity(newVel)

        self._bubbleMaker.onUpdate()
        GameEntity.onUpdate(self)
        
class Bubble(GameEntity):
    def __init__(self,game):
        GameEntity.__init__(self,game)
        self.setup("bubble.png")
    def onUpdate(self):
        GameEntity.onUpdate(self)
        self.transform.setVelocityXY(0,-1)
        if self.transform.getPos().y<-20:
            self._game.removeFromScene(self)

class Food(GameEntity):
    def __init__(self,game):
        GameEntity.__init__(self,game)
        self.setup("food.png")
        self.isFood=True
        self.transform.setVelocityXY(0,0.4)
        self._isDead=False
        if random.randrange(0,2)==1:
            self.visual.setXFlip(True)
        if random.randrange(0,2)==1:
            self.visual.setYFlip(True)
    def onUpdate(self):
        if self.transform.getPos().y>380:
            self.transform.setVelocityXY(0,0)
        GameEntity.onUpdate(self)
    def isDead(self):
        return self._isDead
    def eat(self):
        self._isDead=True
        self._game.removeFromScene(self)

class Button(GameEntity):
    def __init__(self):
        GameEntity.__init__(self)
        self.color_light = (170,170,170)
        self.color_dark = (150,150,150)
        self.color_border = (20,20,20)
        self._isClickable=True
    def setup(self,rect,text,callback):
        self._rect=rect
        self._text=text
        self._callback=callback
    def onClick(self):
        mouse = pygame.mouse.get_pos()
        if self._rect.pointInside(mouse[0],mouse[1]):
            self._callback()
    def onDraw(self,displaySurf,font):
        mouse = pygame.mouse.get_pos()
        colorToUse=self.color_dark
        if self._rect.pointInside(mouse[0],mouse[1]):
            colorToUse=self.color_light
        pygame.draw.rect(displaySurf,self.color_border,[self._rect.x,self._rect.y,self._rect.w,self._rect.h])
        bW=5
        pygame.draw.rect(displaySurf,colorToUse,[self._rect.x+bW,self._rect.y+bW,self._rect.w-2*bW,self._rect.h-2*bW])
        text_surface = font.render(self._text,True,(0,0,0))
        textX=self._rect.x+(self._rect.w/2)-(text_surface.get_width()/2)
        textY=self._rect.y+(self._rect.h/2)-(text_surface.get_height()/2)
        displaySurf.blit(text_surface, (textX,textY))
        
class Game:
    def __init__(self):
        pygame.init()
        self._running = True
        self._display_surf = None
        self._windowSize = self._windowWidth, self._windowHeight = 840, 400
        self._entityList=[]
        self._pyGameClock = pygame.time.Clock()
    def setup(self,gameTitle,iconFile):
        self._display_surf = pygame.display.set_mode(self._windowSize, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption(gameTitle)
        icon = loadImage(iconFile)
        pygame.display.set_icon(icon)
        self.appFont = pygame.font.Font("assets/OpenSansBold.ttf", 20)
    def _onEvent(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            for entity in self._entityList:
                if hasattr(entity,"onClick"):
                    entity.onClick()
    def _onLoop(self):
        for entity in self._entityList:   
            entity.onUpdate()
    def _onPreDraw(self):
        self._display_surf.fill((255,255,255))
        pass
    def _onDraw(self):
        pass
    def _onCleanup(self):
        pygame.quit()
    def runGame(self):
        while( self._running ):
            self._pyGameClock.tick(60)
            for event in pygame.event.get():
                self._onEvent(event)
            self._onLoop()
            self._onPreDraw()
            self._drawSceneEntities()
            self._onDraw()
            pygame.display.flip()
        self._onCleanup()
    def addToScene(self,entity):
        self._entityList.append(entity)
    def removeFromScene(self,entityToRem):
        for entity in self._entityList:   
            if entity==entityToRem:
                self._entityList.pop(self._entityList.index(entity))
    def _drawSceneEntities(self):
        for entity in self._entityList:
            entityPos=entity.transform.getPos()
            surface=entity.visual.getSurface()
            if surface != None:
                self._display_surf.blit(surface,(entityPos.x,entityPos.y))
            if hasattr(entity,"onDraw"):
                entity.onDraw(self._display_surf,self.appFont)
    def isCollision(self,entityA,entityB):
        rect1=entityA.getColRect()
        rect2=entityB.getColRect()
        return self.isRectCollision(rect1,rect2)
    def isRectCollision(self,rect1,rect2):
        return ((rect1.x < rect2.x + rect2.w) &
           (rect1.x + rect1.w > rect2.x) &
           (rect1.y < rect2.y + rect2.h) &
           (rect1.y + rect1.h > rect2.y))
    def drawText(self,text,x,y):  
        text_surface = self.appFont.render(text,True,(0,0,0))
        self._display_surf.blit(text_surface, (x,y))
        
class Aquarium(Game):
    def __init__(self):
        Game.__init__(self)
        self.setup("AquariumV2",'fish1.png')
        tankBG = GameEntity()
        tankBG.setup('tankBG.png',0,-80)
        self.addToScene(tankBG)
        self.aquariumSize = self._windowWidth-200, self._windowHeight
        self.createFish()
        self.createFish()
        
        self._addButton(GameRect(640,0,200,100),"Add Fish",self.createFish)
        self._addButton(GameRect(640,95,200,100),"Feed Fish",self.createFood)
        
        gurgleSound = loadSound("aquarium_gurgle.wav")
        pygame.mixer.Sound.play(gurgleSound,-1)        
    def _addButton(self,rect,text,callback):
        button1=Button()
        button1.setup(rect,text,callback)
        self.addToScene(button1)
    def getAllFood(self,fromPoint,rangeAmount):
        foodList=[]
        for entity in self._entityList:   
            if hasattr(entity,"isFood"):
                if fromPoint.distanceTo(entity.transform.getPos()) < rangeAmount:
                    foodList.append(entity)
        return foodList
        
    def createFish(self):
        fish1 = Fish(self)
        fish1.transform.setPos(getRandomPoint(540,300))
        self.addToScene(fish1)
    def createFood(self):
        food = Food(self)
        food.transform.setPosXY(random.randrange(0,540),0)
        self.addToScene(food)
        splash = loadSound("splash.wav")
        pygame.mixer.Sound.play(splash)
    def _onPreDraw(self):
        Game._onPreDraw(self)
        borderColor=(20,20,20)
        colorToUse = (150,150,150)
        rect=GameRect(self.aquariumSize[0],0,200,self._windowHeight)
        pygame.draw.rect(self._display_surf,borderColor,[rect.x,rect.y,rect.w,rect.h])
        bW=4
        pygame.draw.rect(self._display_surf,colorToUse,[rect.x+bW,rect.y+bW,rect.w-2*bW,rect.h-2*bW])
        
if __name__ == "__main__" :
    game = Aquarium()
    game.runGame()
