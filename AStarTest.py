#!/usr/bin/python
# -*- coding: UTF-8 -*-

BLOCK = "B"
START = "S"
END = "E"
PATH = "#"
VISITED = "*"
SPACE = "."
#直线单格移动代价
LINE_PARAM = 10
#斜线单格移动代价
OBLIQUE_PARAM = 14
class PointVo():
	def __init__(self):
		self.parent = [0,0]
		self.pos = []
		self.tag = ""
		#从起点S移动到指定方格的移动代价
		self.G = 0
		#从指定的方格移动到终点E的估算成本
		self.H = 0
		#F=G+H
		self.F = 0

class AStar():
	def __init__(self):
		self.mapData = []
		self.startPos = []
		self.endPos = []
		self.map = [". . . . . . . . . . . . . . . . . . . . . . . .",
					". . . . . . . . . . . . . . . . . . . . . . . .",
					". . . . . B . . . . . . . . . . . . . . . . . .",
					". . . . . B . . . B . . . . . . . . . . . . . .",
					". . . . . B . S . B . . . . . . . . . . . . . .",
					". B B . . B . . . B . . . . . . . . . . . . . .",
					". B B B B B B B B B . . . . . . . . . . . . . .",
					". . . . . . . . . . . . . . . . . . . . . . . .",
					". . . . . . . . . . . . . . . . . . . . . . . .",
					". . . E . . . . . . . . . . . . . . . . . . . .",
					". . . . . . . . . . . . . . . . . . . . . . . ."]

	#读取地图数据
	def initMapData(self):
		lineIndex = 0
		for line in self.map:
			self.mapData.append([])
			pointIndex = 0
			for point in line.split(" "):
				pointVo = PointVo()
				pointVo.tag = point
				pointVo.pos = [lineIndex,pointIndex]
				self.mapData[lineIndex].append(pointVo)
				if point == "S":
					self.startPos = [lineIndex,pointIndex]
				if point == "E":
					self.endPos = [lineIndex,pointIndex]
					print(self.endPos)
				pointIndex = pointIndex + 1
			lineIndex = lineIndex + 1
		self.MAX_X = lineIndex
		self.MAX_Y = pointIndex

	#取四周8个点
	def addPoint2OpenList(self,posX,posY):
		self.closeList.append(self.mapData[posX][posY])
		if self.mapData[posX][posY] in self.openList:
			self.openList.remove(self.mapData[posX][posY])
		print(posX,posY)
		#取上下左右4点
		if posX > 0:
			self.addOpenList(posX-1,posY,[posX,posY],False)
		if posX < self.MAX_X - 1:
			self.addOpenList(posX,posY-1,[posX,posY],False)
		if posY > 0:
			self.addOpenList(posX+1,posY,[posX,posY],False)
		if posY < self.MAX_Y - 1:
			self.addOpenList(posX,posY+1,[posX,posY],False)
		#取斜角4点
		if posX > 0 and posY > 0:
			self.addOpenList(posX-1,posY-1,[posX,posY],True)
		if posX > 0 and posY < self.MAX_Y - 1:
			self.addOpenList(posX-1,posY+1,[posX,posY],True)
		if posX < self.MAX_X - 1 and posY > 0:
			self.addOpenList(posX+1,posY-1,[posX,posY],True)
		if posX < self.MAX_X - 1 and posY < self.MAX_Y - 1:
			self.addOpenList(posX+1,posY+1,[posX,posY],True)

	#计算估值
	def addOpenList(self,posX,posY,parent,isOblique):
		if self.mapData[posX][posY] in self.closeList:
			return
		if self.mapData[posX][posY].tag == "B":
			return

		tempG = 0
		if isOblique:
			tempG = OBLIQUE_PARAM
		else:
			tempG = LINE_PARAM
		if not self.mapData[posX][posY] in self.openList:
			self.mapData[posX][posY].parent = parent
			self.mapData[posX][posY].G = self.mapData[parent[0]][parent[1]].G + tempG
			self.mapData[posX][posY].H = (abs(self.endPos[0]-posX) + abs(self.endPos[1]-posY))*10
			self.mapData[posX][posY].F = self.mapData[posX][posY].H + self.mapData[posX][posY].G
			self.openList.append(self.mapData[posX][posY])
		else:
			if self.mapData[posX][posY].G < self.mapData[parent[0]][parent[1]].G + tempG:
				self.closeList.append(self.mapData[parent[0]][parent[1]])
				if self.mapData[parent[0]][parent[1]] in self.openList:
					self.openList.remove(self.mapData[parent[0]][parent[1]])


	#获取openList中F值最小的点
	def getMinFPoint(self):
		minVo = self.openList[0]
		for vo in self.openList:
			if vo.F < minVo.F:
				minVo = vo
		return minVo

	def startSearch(self):
		self.initMapData()
		
		#待检测队列
		self.openList = []
		self.closeList = []
		self.addPoint2OpenList(self.startPos[0],self.startPos[1])
		minVo = self.getMinFPoint()
		while not (minVo.pos[0] == self.endPos[0] and minVo.pos[1] == self.endPos[1]):
			self.addPoint2OpenList(minVo.pos[0],minVo.pos[1])
			minVo = self.getMinFPoint()

		pathVo = self.mapData[self.endPos[0]][self.endPos[1]]
		while not (pathVo.pos[0] == self.startPos[0] and pathVo.pos[1] == self.startPos[1]):
			pathVo = self.mapData[pathVo.parent[0]][pathVo.parent[1]]
			if not (pathVo.pos[0] == self.startPos[0] and pathVo.pos[1] == self.startPos[1]):
				pathVo.tag = "#"

		for line in self.mapData:
			lineStr = ""
			for point in line:
				lineStr = lineStr + point.tag + " "
			print(lineStr)
				
		
astar = AStar()
astar.startSearch()