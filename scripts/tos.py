import os
import sys
import copy
from enum import Enum
import queue
import random
import shutil

from PIL import Image, ImageDraw
import imageio
from pydantic import Field, BaseModel


class Move(Enum):
    UP = [-1, 0]
    DOWN = [1, 0]
    LEFT = [0, -1]
    RIGHT = [0, 1]


class StoneType(Enum):
    DARK = "dark"
    LIGHT = "light"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"
    HEALTH = "health"


class ToSConfig(BaseModel):
    input_filename: str = Field(
        ...,
        title="Input filename",
        description="This file can be either a txt file or a screenshot.",
        frozen=False,
        deprecated=False,
    )
    output_dir: str = Field(
        ...,
        title="Output directory",
        description="The directory to store the output images and txt file.",
        frozen=False,
        deprecated=False,
    )
    hand: str = Field(
        default="./imgs/start.png",
        title="Hand image",
        description="The image for the starting point.",
        frozen=True,
        deprecated=False,
    )
    flag: str = Field(
        default="./imgs/destination.png",
        title="Flag image",
        description="The image for the destination point.",
        frozen=True,
        deprecated=False,
    )
    dark: str = Field(
        default="./imgs/dark.png",
        title="Dark image",
        description="The image for the dark stone.",
        frozen=True,
        deprecated=False,
    )
    light: str = Field(
        default="./imgs/light.png",
        title="Light image",
        description="The image for the light stone.",
        frozen=True,
        deprecated=False,
    )
    water: str = Field(
        default="./imgs/water.png",
        title="Water image",
        description="The image for the water stone.",
        frozen=True,
        deprecated=False,
    )
    fire: str = Field(
        default="./imgs/fire.png",
        title="Fire image",
        description="The image for the fire stone.",
        frozen=True,
        deprecated=False,
    )
    earth: str = Field(
        default="./imgs/earth.png",
        title="Earth image",
        description="The image for the earth stone.",
        frozen=True,
        deprecated=False,
    )
    health: str = Field(
        default="./imgs/health.png",
        title="Health image",
        description="The image for the health stone.",
        frozen=True,
        deprecated=False,
    )
    background: str = Field(
        default="./imgs/background.png",
        title="Background image",
        description="The image for the background.",
        frozen=True,
        deprecated=False,
    )
    pixels: int = Field(
        default=60,
        title="Pixels",
        description="The size of each stone in pixels.",
        frozen=True,
        deprecated=False,
    )
    line_width: int = Field(
        default=4,
        title="Line width",
        description="The width of the line.",
        frozen=True,
        deprecated=False,
    )
    line_color: tuple = Field(
        default=(150, 150, 150),
        title="Line color",
        description="The color of the line.",
        frozen=True,
        deprecated=False,
    )


config = ToSConfig(input_filename="./logs/test.jpg", output_dir="./outputs/")


class Runestone:
    def __init__(self, _type: str, _status: str = " "):
        self.type = _type
        self.status = _status

    def __repr__(self):
        if self.type == StoneType.DARK:
            return f"\x1b[0;35;40m D[{self.status}] \x1b[0m"
        if self.type == StoneType.LIGHT:
            return f"\x1b[0;33;40m L[{self.status}] \x1b[0m"
        if self.type == StoneType.WATER:
            return f"\x1b[0;34;40m W[{self.status}] \x1b[0m"
        if self.type == StoneType.FIRE:
            return f"\x1b[0;31;40m F[{self.status}] \x1b[0m"
        if self.type == StoneType.EARTH:
            return f"\x1b[0;32;40m E[{self.status}] \x1b[0m"
        if self.type == StoneType.HEALTH:
            return f"\x1b[0;37;40m H[{self.status}] \x1b[0m"
        return None


class TosBoard:
    def __init__(self):
        self.numOfRows = 5
        self.numOfCols = 6
        self.runestones = [[None] * self.numOfCols for row in range(self.numOfRows)]
        self.currentPosition = [0, 0]
        self.previousPosition = self.currentPosition

    def __repr__(self):
        output = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                output = output + str(stone)
            output = output + "\n"
        return output

    def _swap(self, _pos1, _pos2) -> None:
        swapTmp = self.runestones[_pos1[0]][_pos1[1]]
        self.runestones[_pos1[0]][_pos1[1]] = self.runestones[_pos2[0]][_pos2[1]]
        self.runestones[_pos2[0]][_pos2[1]] = swapTmp

    def randomInitialized(self) -> None:
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                stone = Runestone(random.choice(list(StoneType)))
                self.runestones[rowIdx][colIdx] = stone
        self.currentPosition = [random.randrange(self.numOfRows), random.randrange(self.numOfCols)]
        self.previousPosition = self.currentPosition
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"

    def initFromFile(self, _filePath) -> None:
        with open(_filePath) as fin:
            for lineIdx, line in enumerate(fin):
                tokenList = line.strip().split()
                if len(tokenList) != 6:
                    continue
                for tokenIdx, token in enumerate(tokenList):
                    stone = None
                    if token == "D":
                        stone = Runestone(StoneType.DARK)
                    if token == "L":
                        stone = Runestone(StoneType.LIGHT)
                    if token == "W":
                        stone = Runestone(StoneType.WATER)
                    if token == "F":
                        stone = Runestone(StoneType.FIRE)
                    if token == "E":
                        stone = Runestone(StoneType.EARTH)
                    if token == "H":
                        stone = Runestone(StoneType.HEALTH)
                    self.runestones[lineIdx][tokenIdx] = stone

    def initFromScreenshot(self, _filePath) -> None:
        types = screenshotToTypes(_filePath, self.numOfRows, self.numOfCols)
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                self.runestones[rowIdx][colIdx] = Runestone(types[rowIdx][colIdx])

    def setCurrentPosition(self, _pos) -> None:
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = " "
        self.currentPosition = _pos
        self.previousPosition = self.currentPosition
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"

    def getSuccessorList(self):
        successorList = []
        for move in list(Move):
            newPosition = [sum(z) for z in zip(list(move.value), self.currentPosition)]
            if newPosition == self.previousPosition:
                continue
            if 0 <= newPosition[0] < self.numOfRows and 0 <= newPosition[1] < self.numOfCols:
                newBoard = TosBoard()
                newBoard.runestones = [copy.copy(row) for row in self.runestones]
                newBoard.currentPosition = newPosition
                newBoard.previousPosition = self.currentPosition
                newBoard._swap(newPosition, self.currentPosition)
                successorList.append((newBoard, move))
        return successorList

    def evaluate(self):
        # determine if the stone would be removed
        removed = [[None] * self.numOfCols for row in range(self.numOfRows)]
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols - 2):
                stone1 = self.runestones[rowIdx][colIdx]
                stone2 = self.runestones[rowIdx][colIdx + 1]
                stone3 = self.runestones[rowIdx][colIdx + 2]
                if stone1.type == stone2.type and stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx][colIdx + delta] = stone1.type
        for colIdx in range(self.numOfCols):
            for rowIdx in range(self.numOfRows - 2):
                stone1 = self.runestones[rowIdx][colIdx]
                stone2 = self.runestones[rowIdx + 1][colIdx]
                stone3 = self.runestones[rowIdx + 2][colIdx]
                if stone1.type == stone2.type and stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx + delta][colIdx] = stone1.type
        # check if the stone you take at first will be removed or not
        end = False
        if removed[self.currentPosition[0]][self.currentPosition[1]]:
            end = True
        # calculate the number of stones removed and change their status for printing
        stones = 0
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                self.runestones[rowIdx][colIdx].status = " "
                if removed[rowIdx][colIdx] is not None:
                    stones = stones + 1
                    self.runestones[rowIdx][colIdx].status = "+"
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"
        # check if four boundaries are removed or not
        boundary = 0
        if removed[0][0] is not None:
            boundary = boundary + 1
        if removed[0][-1] is not None:
            boundary = boundary + 1
        if removed[-1][0] is not None:
            boundary = boundary + 1
        if removed[-1][-1] is not None:
            boundary = boundary + 1
        # calculate combo
        combo = 0
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
                if removed[rowIdx][colIdx] is not None:
                    combo = combo + 1
                    t = removed[rowIdx][colIdx]
                    q = queue.Queue()
                    q.put((rowIdx, colIdx))
                    while not q.empty():
                        (r, c) = q.get()
                        removed[r][c] = None
                        if r + 1 < self.numOfRows and removed[r + 1][c] == t:
                            q.put((r + 1, c))
                        if c + 1 < self.numOfCols and removed[r][c + 1] == t:
                            q.put((r, c + 1))
                        if r - 1 >= 0 and removed[r - 1][c] == t:
                            q.put((r - 1, c))
                        if c - 1 >= 0 and removed[r][c - 1] == t:
                            q.put((r, c - 1))
        # return results
        return stones, boundary, combo, end


def analyze(_initBoard: TosBoard):
    # determine where to start
    q = queue.PriorityQueue()
    minCost, bestRowIdx, bestColIdx = 10e9, 0, 0
    # try every possible stone
    for rowIdx in range(_initBoard.numOfRows):
        for colIdx in range(_initBoard.numOfCols):
            _initBoard.setCurrentPosition([rowIdx, colIdx])
            cost, count, moveList = 10e9, 0, []
            q.put((cost, count, moveList, _initBoard))
            while not q.empty():
                (cost, _, moveList, board) = q.get()
                if cost < minCost:
                    minCost, bestRowIdx, bestColIdx = (cost, rowIdx, colIdx)
                if len(moveList) >= 5:
                    continue
                for _successorIdx, successor in enumerate(board.getSuccessorList()):
                    count = count + 1
                    (newBoard, move) = successor
                    stones, boundary, combo, end = newBoard.evaluate()
                    newCost = -(combo * 100 + boundary * 50 + stones) + len(moveList) * 0.001
                    newCost = newCost + 100 if end else newCost
                    newMoveList = copy.copy(moveList)
                    newMoveList.append(move)
                    q.put((newCost, count, newMoveList, newBoard))
    # search end - set current position to the best position
    _initBoard.setCurrentPosition([bestRowIdx, bestColIdx])
    stones, boundary, combo, end = _initBoard.evaluate()
    sys.stderr.write(str(_initBoard) + "\n")
    # search best result
    q = queue.PriorityQueue()
    cost, count, moveList = 10e9, 0, []
    minCost, bestMoveList, bestBoard = (cost, moveList, _initBoard)
    numOfPhases, finalMoveList = 5, []
    # break the search mechanism into several phases
    for it in range(1, numOfPhases + 1):
        q.put((minCost, count, bestMoveList, bestBoard))
        # bfs with evaluation as reward
        while not q.empty():
            (cost, _, moveList, board) = q.get()
            if cost < minCost:
                minCost, bestMoveList, bestBoard = (cost, moveList, board)
            if len(moveList) >= 10:
                continue
            for _successorIdx, successor in enumerate(board.getSuccessorList()):
                count = count + 1
                (newBoard, move) = successor
                stones, boundary, combo, end = newBoard.evaluate()
                newCost = (
                    -(combo * 100 + boundary * 10 * (numOfPhases - it) + stones)
                    + len(moveList) * 0.001
                )
                newCost = newCost + 100 if end and it != numOfPhases else newCost
                newMoveList = copy.copy(moveList)
                newMoveList.append(move)
                q.put((newCost, count, newMoveList, newBoard))
        # end search - concatenate the move list and evaluate again
        stones, boundary, combo, end = bestBoard.evaluate()
        minCost = -(combo * 100 + boundary * 10 * (numOfPhases - 1 - it) + stones)
        minCost = minCost + 100 if end and it != (numOfPhases - 1) else minCost
        finalMoveList = finalMoveList + bestMoveList
        bestMoveList = []
        sys.stderr.write(f"phase {it}/{numOfPhases}\n")
        sys.stderr.write(
            f"stones={stones}, boundary={boundary}, combo={combo}, end={end}, steps={len(finalMoveList)}, count={count}\n"
        )
        sys.stderr.write(str(bestBoard) + "\n")
    # return final result
    return bestBoard, finalMoveList


def drawBoard(_board: TosBoard):
    type2Foreground = {
        StoneType.DARK: Image.open(config.dark).convert("RGBA"),
        StoneType.LIGHT: Image.open(config.light).convert("RGBA"),
        StoneType.WATER: Image.open(config.water).convert("RGBA"),
        StoneType.FIRE: Image.open(config.fire).convert("RGBA"),
        StoneType.EARTH: Image.open(config.earth).convert("RGBA"),
        StoneType.HEALTH: Image.open(config.health).convert("RGBA"),
    }
    background: Image.Image = Image.open(config.background).convert("RGBA")
    for rowIdx in range(_board.numOfRows):
        for colIdx in range(_board.numOfCols):
            stone = _board.runestones[rowIdx][colIdx]
            foreground = type2Foreground[stone.type]
            location = (colIdx * config.pixels, rowIdx * config.pixels)
            background.paste(foreground, location, foreground)
    return background


def visualizePath(_initBoard: TosBoard, _bestBoard, _finalMoveList) -> None:
    # create directory
    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)
    os.makedirs(config.output_dir)
    # setup image objects
    hand = Image.open(config.hand).convert("RGBA")
    flag = Image.open(config.flag).convert("RGBA")
    drawBoard(_initBoard).save(os.path.join(config.output_dir, "initBoard.png"))
    drawBoard(_bestBoard).save(os.path.join(config.output_dir, "bestBoard.png"))
    # draw path images
    board = _initBoard
    path = drawBoard(_initBoard)
    d = ImageDraw.Draw(path)
    delta, pathIdx, visited = config.pixels // 2, 1, [board.previousPosition]
    for _finalMoveIdx, finalMove in enumerate(_finalMoveList):
        oldBoard = board
        for _successorIdx, successor in enumerate(oldBoard.getSuccessorList()):
            (newBoard, move) = successor
            board = newBoard if finalMove == move else board
        if board.currentPosition in visited:
            # draw start and end before saving
            path.paste(hand, (visited[0][1] * config.pixels, visited[0][0] * config.pixels), hand)
            path.paste(
                flag,
                (
                    board.previousPosition[1] * config.pixels,
                    board.previousPosition[0] * config.pixels,
                ),
                flag,
            )
            path.save(os.path.join(config.output_dir, f"path{pathIdx:0>2d}.png"))
            # create new path image
            path = drawBoard(oldBoard)
            d = ImageDraw.Draw(path)
            pathIdx, visited = pathIdx + 1, [board.previousPosition]
        src = (
            board.previousPosition[1] * config.pixels + delta,
            board.previousPosition[0] * config.pixels + delta,
        )
        des = (
            board.currentPosition[1] * config.pixels + delta,
            board.currentPosition[0] * config.pixels + delta,
        )
        d.line([src, des], fill=config.line_color, width=config.line_width)
        visited.append(board.currentPosition)
    path.paste(hand, (visited[0][1] * config.pixels, visited[0][0] * config.pixels), hand)
    path.paste(
        flag,
        (board.currentPosition[1] * config.pixels, board.currentPosition[0] * config.pixels),
        flag,
    )
    path.save(os.path.join(config.output_dir, f"path{pathIdx:0>2d}.png"))
    # gif
    images = [imageio.v3.imread(os.path.join(config.output_dir, "initBoard.png"))]
    for idx in range(1, pathIdx + 1):
        images.append(imageio.v3.imread(os.path.join(config.output_dir, f"path{idx:0>2d}.png")))
    images.append(imageio.v3.imread(os.path.join(config.output_dir, "bestBoard.png")))
    imageio.mimsave(os.path.join(config.output_dir, "path.gif"), images, duration=1.5)


def screenshotToTypes(_filePath, _numOfRows, _numOfCols):
    # load image and config
    screen: Image.Image = Image.open(_filePath).convert("RGB")
    width = screen.size[0]
    height = int(width * 1.5)
    delta = (screen.size[1] - height) // 2
    box = (
        0,
        screen.size[1] - delta - width // _numOfCols * _numOfRows,
        width,
        screen.size[1] - delta,
    )
    screen = screen.crop(box).resize(
        (config.pixels * _numOfCols, config.pixels * _numOfRows), Image.BILINEAR
    )
    # init
    types = []
    type2Value = {
        StoneType.DARK: (118, 28, 138),
        StoneType.LIGHT: (120, 89, 11),
        StoneType.WATER: (44, 90, 136),
        StoneType.FIRE: (153, 28, 15),
        StoneType.EARTH: (27, 117, 31),
        StoneType.HEALTH: (172, 74, 128),
    }
    type2Weight = {
        StoneType.DARK: 1.0,
        StoneType.LIGHT: 1.0,
        StoneType.WATER: 1.0,
        StoneType.FIRE: 1.0,
        StoneType.EARTH: 1.0,
        StoneType.HEALTH: 1.7,
    }
    # parse
    for rowIdx in range(_numOfRows):
        types.append([])
        for colIdx in range(_numOfCols):
            types[rowIdx].append(None)
            box = (
                colIdx * config.pixels,
                rowIdx * config.pixels,
                (colIdx + 1) * config.pixels,
                (rowIdx + 1) * config.pixels,
            )
            value = screen.crop(box).resize((1, 1), Image.Resampling.LANCZOS).getpixel((0, 0))
            minDist = 10e9
            for t in type2Value:
                v = type2Value[t]
                dist = abs(value[0] - v[0]) + abs(value[1] - v[1]) + abs(value[2] - v[2])
                dist = dist * type2Weight[t]
                if dist >= minDist:
                    continue
                minDist = dist
                types[rowIdx][colIdx] = t
    # return types
    return types


# get board object
initBoard = TosBoard()
# init
initBoard.randomInitialized()
if config.input_filename is not None:
    if config.input_filename.endswith("txt"):
        initBoard.initFromFile(config.input_filename)
    else:
        initBoard.initFromScreenshot(config.input_filename)
# test evaluation
stones, boundary, combo, end = initBoard.evaluate()
# start searching
bestBoard, finalMoveList = analyze(initBoard)
# evaluate and visualization
stones, boundary, combo, end = bestBoard.evaluate()
visualizePath(initBoard, bestBoard, finalMoveList)
# dump result to txt file
with open(os.path.join(config.output_dir, "output.txt"), "w") as fout:
    fout.write(f"startRowIdx={initBoard.currentPosition[0]}\n")
    fout.write(f"startColIdx={initBoard.currentPosition[1]}\n")
    for move in finalMoveList:
        fout.write(f"{move} ")
    fout.write(f"\nstones={stones}\ncombo={combo}\nsteps={len(finalMoveList)}\n")
