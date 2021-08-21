import random

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import glClearColor

from mod import easy_shaders as es, basic_shapes as bs, scene_graph as sg, transformations as tr


def grid(N):
    """
    Defines the coordinates of the map
    """
    axis = np.linspace(-(N//2), N//2, N)
    return axis

def length(posTail, posLead, vertices):
    n = len(vertices)
    if n>0:
        locs = np.array(vertices)
        locs = np.array([posTail, *locs[:, 0], posLead])
    else:
        locs = np.array([posTail, posLead])
    n = len(locs)
    l = 0
    for i in range(n-1):
        l += np.linalg.norm(locs[i+1]-locs[i])
    return l

def normalize(v1):
    return v1/np.linalg.norm(v1)

def angle(v1, v2):
    return np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

def reach(pos1, pos2, mod):
    # Returns False if pos2 is not reached
    if np.linalg.norm(pos2-pos1)>mod:
        return False
    else:
        return True

def posInPath(pos0, angAct, path, delta):
    dirAct = normalize(path[0][0] - pos0)
    totalPath = [[pos0, dirAct, angAct]] + path
    suma = 0
    n = len(totalPath)
    for i in range(n-1):
        l = np.linalg.norm(totalPath[i+1][0]-totalPath[i][0])
        if delta<suma+l:
            newPos = totalPath[i][0]+totalPath[i][1]*(delta - suma)
            return newPos, i, totalPath[i][1], totalPath[i][2]
        else:
            suma += l
    newPos = totalPath[n-1][0]+totalPath[n-1][1]*(delta - suma)
    return newPos, n-1, totalPath[n-1][1], totalPath[n-1][2]

class Axis(object):

    def __init__(self, N):
        self.model = es.toGPUShape(bs.createAxis(N-1))

    def draw(self, pipeline, projection, view):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(self.model, GL_LINES)

class Soil:
    def __init__(self, image):
        gpuSquare = es.toGPUShape(bs.createTextureNormalsQuad(image), GL_REPEAT, GL_LINEAR)

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(40)
        body.childs += [gpuSquare]
        self.model = body

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 235/255,208/255,200/255)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.03, 0.03, 0.03)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.0001, 0.0001, 0.0001)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 1)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Dunes:
    def __init__(self):

        desert = sg.SceneGraphNode('roca')
        desert.transform = tr.matmul([tr.uniformScale(1), tr.rotationX(np.pi/2)])
        desert.childs += [ObjectModel().objectColor('resources/fig/fondoDunasTextura.obj',
                                                    (200 / 255, 150 / 255, 105 / 255))]

        self.model = desert

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"),  lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.09, 0.07, 0.04)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.002, 0.001, 0.0008)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.009)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.0018)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Pyramid:
    def __init__(self):

        pyramid1 = sg.SceneGraphNode('roca')
        pyramid1.transform = tr.matmul([tr.translate(0,40,0),
                                        tr.rotationZ(np.pi/4),
                                        tr.scale(28.5,28.5,10),
                                        tr.rotationX(np.pi/2)])
        pyramid1.childs += [ObjectModel().objectTexture('resources/fig/piramide.obj',
                                                        'resources/texture/piramideTextura.jpg')]

        pyramid2 = sg.SceneGraphNode('roca')
        pyramid2.transform = tr.matmul([tr.translate(-40, 40, 0), tr.scale(1, 1, 1.5)])
        pyramid2.childs += [pyramid1]

        pyramid3 = sg.SceneGraphNode('roca')
        pyramid3.transform = tr.matmul([tr.translate(7, 40, 0), tr.scale(1.5,1.5,2)])
        pyramid3.childs += [pyramid1]

        pyramid4 = sg.SceneGraphNode('roca')
        pyramid4.transform = tr.matmul([tr.translate(40, 0, -5), tr.rotationZ(-np.pi/4)])
        pyramid4.childs += [pyramid1]

        triplePyramid = sg.SceneGraphNode('borde')
        triplePyramid.childs += [pyramid1, pyramid2, pyramid3]

        self.model = triplePyramid

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"),lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.05, 0.05, 0.05)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.001, 0.001, 0.0001)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.002)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Horizon:
    def __init__(self):

        horizon1 = sg.SceneGraphNode('roca')
        horizon1.transform = tr.matmul([tr.translate(0,0,10), tr.scale(100,100,15),tr.rotationX(np.pi/2)])
        horizon1.childs += [ObjectModel().objectTexture('resources/fig/fondoJourney.obj',
                                                        'resources/texture/journey.jpg')]

        horizon2 = sg.SceneGraphNode('roca')
        horizon2.transform = tr.scale(-1,1,1)
        horizon2.childs += [horizon1]

        horizon3 = sg.SceneGraphNode('roca')
        horizon3.transform = tr.scale(1,-1,1)
        horizon3.childs += [horizon1,horizon2]

        horizon = sg.SceneGraphNode('rocas')
        horizon.childs += [horizon1, horizon2,horizon3]
        horizon.transform = tr.matmul([tr.translate(0,0,3), tr.scale(1,1,1.7)])
        self.model = horizon

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.01, 0.01, 0.01)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0, 0, 0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Limit:
    def __init__(self,N):
        rock1 = sg.SceneGraphNode('roca')
        rock1.transform = tr.matmul([tr.translate(N/2+4.5,-2,0),
                                     tr.uniformScale(2),
                                     tr.rotationZ(np.pi),
                                     tr.rotationX(np.pi/2)])
        rock1.childs += [ObjectModel().objectTexture('resources/fig/roca1.obj',
                                                     'resources/texture/Rock_1_Base_Color.png')]

        rock2 = sg.SceneGraphNode('roca')
        rock2.transform = tr.matmul([tr.translate(N / 2 + 3.2, 6, 0),
                                     tr.uniformScale(2),
                                     tr.rotationX(np.pi / 2)])
        rock2.childs += [ObjectModel().objectTexture('resources/fig/roca2.obj',
                                                     'resources/texture/Rock_2_Base_Color.png')]

        rock12 = sg.SceneGraphNode('roca')
        rock12.transform = tr.matmul([tr.translate(0.5,0,-5),tr.scale(1,1.5,1),tr.rotationZ(np.pi)])
        rock12.childs += [rock1, rock2]

        rock4 = sg.SceneGraphNode('roca')
        rock4.transform = tr.matmul([tr.translate(N / 2+0.4, 10, 0),
                                     tr.uniformScale(1),
                                     tr.rotationZ(np.pi),
                                     tr.rotationX(np.pi / 2)])
        rock4.childs += [ObjectModel().objectTexture('resources/fig/roca4.obj',
                                                     'resources/texture/Rock_4_Base_Color.png')]

        rock8 = sg.SceneGraphNode('roca')
        rock8.transform = tr.matmul([tr.translate(N / 2+1.4, 18, 3),
                                     tr.scale(3, 7,6),
                                     tr.rotationZ(np.pi*3/2),
                                     tr.rotationX(np.pi / 2)])
        rock8.childs += [ObjectModel().objectTexture('resources/fig/roca8.obj',
                                                     'resources/texture/Rock_8_Base_Color.png')]

        rock11 = sg.SceneGraphNode('roca')
        rock11.transform = tr.matmul([tr.translate(-18, -25, 0),
                                      tr.scale(3,2,2),
                                      tr.rotationZ(np.pi/2),
                                      tr.rotationX(np.pi / 2)])
        rock11.childs += [ObjectModel().objectTexture('resources/fig/roca1.obj',
                                                      'resources/texture/Rock_1_Base_Color.png')]

        rock111 = sg.SceneGraphNode('roca')
        rock111.transform = tr.translate(13, 0, -2)
        rock111.childs += [rock11]

        rock100 = sg.SceneGraphNode('roca')
        rock100.transform = tr.translate(30, 0, -4)
        rock100.childs += [rock11]

        smallRocks = sg.SceneGraphNode('roca')
        smallRocks.transform = tr.matmul([tr.rotationY(np.pi)])
        smallRocks.childs += [rock4, rock8]

        rock22 = sg.SceneGraphNode('roca')
        rock22.transform = tr.matmul([tr.translate(0,-12,-4),
                                      tr.rotationY(np.pi),
                                      tr.rotationX(np.pi)])
        rock22.childs += [rock2]

        rock10 = sg.SceneGraphNode('roca')
        rock10.transform = tr.matmul([tr.translate(N / 2+1.4, -10, 3),
                                      tr.scale(3, 7,6),
                                      tr.rotationZ(np.pi*3/2),
                                      tr.rotationX(np.pi / 2)])
        rock10.childs += [ObjectModel().objectTexture('resources/fig/roca8.obj',
                                                      'resources/texture/Rock_8_Base_Color.png')]

        rocks = sg.SceneGraphNode('rocas')
        rocks.childs += [rock1, rock2, rock4, rock8, rock11, smallRocks, rock22,rock10, rock111, rock100, rock12]
        self.model = rocks

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.75, 0.7, 0.75)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.25, 0.2, 0.25)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.09, 0.09, 0.09)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.02)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class ObjectModel:

    def __init__(self):
        self.model = None

    def objectTexture(self, fig, image):
        modelo = es.toGPUShape(bs.readOBJ(fig, image), GL_REPEAT, GL_LINEAR)
        self.model = modelo
        return self.model

    def objectColor(self, fig, color):
        modelo = es.toGPUShape(bs.createOBJColor(fig, color))
        self.model = modelo
        return self.model

class Obstacle:
    def __init__(self,N, n):
        self.grilla = grid(N)
        self.N = N
        self.n = n+2
        paresSnake = []
        for i in range(self.n):
            par = [-i, 0]
            paresSnake.append(par)
        while True:
            a = random.choice(self.grilla[2:N-2])
            b = random.choice(self.grilla[2:N-2])
            pos = [a, b]
            if pos not in paresSnake: # If the position is not occupied by the snake
                self.pos = np.array(pos)
                break
        cacto = sg.SceneGraphNode('fruit')
        cacto.childs += [ObjectModel().objectTexture('resources/fig/cactusSolo2.obj',
                                                     'resources/texture/cactusSolo2Textura.png')]
        self.model = cacto

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0),
                                          tr.rotationX(np.pi/2),
                                          tr.uniformScale(2)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class AppleCreator:

    def __init__(self, N, n, fig, color, obstacle):
        self.grilla = grid(N)
        self.N = N
        self.n = n+2
        paresSnake = []
        for i in range(self.n):
            par = [-i, 0]
            paresSnake.append(par)
        while True:
            a = random.choice(self.grilla[1:N-1])
            b = random.choice(self.grilla[1:N-1])
            pos = [a, b]
            if pos not in paresSnake:
                self.pos = pos
                break
        self.posSnake = None
        fruit = sg.SceneGraphNode('fruit')
        fruit.childs += [ObjectModel().objectTexture(fig, color)]
        self.model = fruit
        self.posObstacle = obstacle.pos + np.zeros(2)


    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.5),
                                          tr.rotationX(np.pi/2),
                                          tr.uniformScale(1/100)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

    def createNew(self, head):
        while True:
            a = random.choice(self.grilla[1:self.N-1])
            b = random.choice(self.grilla[1:self.N-1])
            pos = np.array([a,b])
            if not np.any(np.all(pos == head.cellsSnake, axis = 1)) and np.any(pos != self.posObstacle):
                self.pos = pos
                return

class Ghost:
    def __init__(self, head):

        ghost = sg.SceneGraphNode('roca')
        ghost.childs += [ObjectModel().objectColor('resources/fig/ghost.obj', (1, 1, 1))]

        self.head = head
        self.model = ghost
        self.escala = 0.5
        self.height = 0

    def update(self,dt):
        self.height += dt/2
        self.escala = self.escala+dt/2 if self.escala+dt<=2 else 2

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"),  lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.09, 0.07, 0.04)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.002, 0.001, 0.0008)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.009)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.0018)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform= tr.matmul([tr.translate(self.head.pos[0], self.head.pos[1], self.height),
                                         tr.rotationZ(self.head.angDir+np.pi/2),
                                         tr.rotationY(0),
                                         tr.rotationX(np.pi/2),
                                         tr.uniformScale(self.escala)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')


class GameOver:

    def __init__(self):
        gpuSquare = es.toGPUShape(bs.createTextureQuad('resources/texture/goBlack.png'), GL_REPEAT, GL_LINEAR)

        body = sg.SceneGraphNode('body')
        body.transform = tr.matmul([tr.translate(0,0,1),tr.uniformScale(15)])
        body.childs += [gpuSquare]
        self.model = body

    def draw(self, pipeline, projection, view):
        glUseProgram(pipeline.shaderProgram)
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                           projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Head:

    def __init__(self, N, n0, fig, image, obstacle):
        self.N = N

        headMoving = sg.SceneGraphNode('headMoving')
        headMoving.childs += [ObjectModel().objectTexture(fig, image)]

        self.pos = np.zeros(2)
        self.model = headMoving
        self.angDir = 0
        self.direct = np.array([1, 0])
        self.ownTurn = []
        self.cellsSnake = np.zeros((n0, 2))
        self.state = True
        self.limit = np.array([N // 2, N // 2])
        self.posObstacle = obstacle.pos +np.zeros(2)
        self.dif = 1
        self.factor = 1
        self.turnX = np.pi / 2
        self.turnY = np.pi / 2
        self.escala = 3
        self.d = 0

    def direction(self, turn, dt):
        if self.state:
            self.angDir += (np.pi*dt/5)*turn*self.dif
            self.direct = np.array([np.cos(self.angDir), np.sin(self.angDir)])
            pos = self.pos + np.zeros(2)
            direc = self.direct + np.zeros(2)
            ang = self.angDir
            self.ownTurn.append([pos, direc, ang])

    def update(self, dt):
        if self.state:
            self.pos += self.direct * dt
            self.cellsSnake[0] = self.pos
        else:
            self.turnX = self.turnX - dt / 2 if (self.turnX - dt) > 0 else 0
            self.turnY = self.turnY + dt * 4 if self.turnX != 0 else 0
            self.d = np.pi/2
            self.escala = 1

    def eat(self, apple, bod, N, fig, image):
        if np.all(np.around(self.pos) == apple.pos):
            apple.createNew(self)
            self.cellsSnake = np.array([*self.cellsSnake, bod[-1].pos])
            bod[-1].followed()
            lbody = len(bod)
            bod.append(TailGrow(N, bod[-1], lbody + 1, fig, image))
            return bod
        else:
            return bod

    def collide(self):
        if np.any(np.abs(self.pos)>self.limit)\
                or np.any(np.all(np.around(self.pos)==np.around(self.cellsSnake[2:]), axis=1)):
            self.state = False
            glClearColor(1, 0.2, 0.4, 1.0)
        elif np.all(np.around(self.pos)==self.posObstacle):
            self.dif = -1
            self.factor = 2.5

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.5),
                                          tr.rotationZ(self.angDir+self.d),
                                          tr.rotationX(self.turnX),
                                          tr.rotationY(self.turnY),
                                          tr.scale(1, 1, self.escala)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class BodyPart(object):

    def __init__(self, N, posIni, lead, locS, fig, image):
        self.N = N
        self.lead = lead
        headMoving = sg.SceneGraphNode('headMoving')
        headMoving.childs += [ObjectModel().objectTexture(fig, image)]
        self.direct = np.array([1, 0])
        self.angDir = 0
        self.turn = self.lead.ownTurn
        self.ownTurn = []
        self.pos = posIni
        self.model = headMoving
        self.theta = 0
        self.state = self.lead.state
        self.loc = locS

    def update(self, dt, head):
        if not self.lead.state:
            self.state = False
            return
        if self.state:
            n = len(self.turn)
            if n == 0:
                self.pos = self.pos + self.direct * dt
                head.cellsSnake[self.loc] = self.pos
            else:
                self.pos, indice, self.direct, self.angDir = posInPath(self.pos, self.angDir, self.turn, dt)
                self.ownTurn += self.turn[0:indice]
                del self.turn[0:indice]
                head.cellsSnake[self.loc] = self.pos

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.5),
                                          tr.rotationZ(self.angDir),
                                          tr.rotationX(np.pi/2),
                                          tr.rotationY(np.pi/2),
                                          tr.scale(1,1,3)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class Tail(BodyPart):

    def __init__(self, N, posIni, lead, locS, fig, image):
        super().__init__(N, posIni, lead, locS, fig, image)
        self.follower = False

    def followed(self):
        self.follower = True

    def update(self, dt, head):
        if not self.lead.state:
            self.state = False
            return
        if self.state:
            n = len(self.turn)
            if n == 0:
                self.pos = self.pos + self.direct * dt
                head.cellsSnake[self.loc] = self.pos
            else:
                self.pos, index, self.direct, self.angDir = posInPath(self.pos, self.angDir, self.turn, dt)
                if self.follower:
                    self.ownTurn += self.turn[0:index]
                del self.turn[0:index]
                head.cellsSnake[self.loc] = self.pos

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.5),
                                          tr.rotationZ(self.angDir),
                                          tr.rotationX(np.pi/2),
                                          tr.rotationY(np.pi/2),
                                          tr.scale(1,1,3)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')

class TailGrow(Tail):

    def __init__(self, N, lead, locS, fig, image):
        super().__init__(N, lead.pos + np.zeros(2), lead, locS, fig, image)
        self.direct = lead.direct
        self.angDir = lead.angDir
        self.moving = False

    def followed(self):
        self.follower = True

    def update(self, dt, head):
        if not self.lead.state:
            self.state = False
            return
        if not self.moving:
            self.moving = length(self.pos, self.lead.pos, self.turn) >= 1
        if self.state and self.moving:
            n = len(self.turn)
            if n == 0:
                self.pos = self.pos + self.direct * dt
                head.cellsSnake[self.loc] = self.pos
            else:
                self.pos, index, self.direct, self.angDir = posInPath(self.pos, self.angDir, self.turn, dt)
                if self.follower:
                    self.ownTurn += self.turn[0:index]
                del self.turn[0:index]
                head.cellsSnake[self.loc] = self.pos

    def draw(self, pipeline, projection, view, cameraPos, lightPos, lightColor):
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), lightColor[0], lightColor[1], lightColor[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), lightColor[0], lightColor[1], lightColor[2])

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.1, 0.1, 0.1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"),  lightPos[0], lightPos[1],
                    lightPos[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), cameraPos[0], cameraPos[1],
                    cameraPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.5),
                                          tr.rotationZ(self.angDir),
                                          tr.rotationX(np.pi/2),
                                          tr.rotationY(np.pi/2),
                                          tr.scale(1,1,3)])
        sg.drawSceneGraphNode(self.model, pipeline, 'model')
