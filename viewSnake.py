import glfw
import sys
from modelSnake import *
from controllerSnake import Controller
from mod import lighting_shaders as ls

if __name__ == "__main__":

    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Super Snake 3000 3D", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)

    texturePipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    lightPipeline = ls.SimplePhongShaderProgram()
    textureLightPipeline = ls.SimpleTexturePhongShaderProgram()


    glClearColor(0.4, 0.6, 0.8, 1.0)

    glEnable(GL_DEPTH_TEST)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    N = 41 # Size of map
    n = 8 # Number of parts at the beginning
    cactus = Obstacle(N, n)
    snake = Head(N, n, 'resources/fig/spongebob_bind.obj', 'resources/texture/spongebob.png', cactus)
    part1 = BodyPart(N, np.array([-1, 0]), snake, 1, 'resources/fig/spongebob_bind.obj',
                     'resources/texture/spongebob.png')
    parts = [part1]
    apple = AppleCreator(N, n, 'resources/fig/naranja.obj', 'resources/texture/Orange_baseColor.png', cactus)
    surface = Soil('resources/texture/sand3.jpg')
    limit = Limit(N)
    dune = Dunes()
    pyramids = Pyramid()
    horizon = Horizon()
    controller.set_model(snake)
    ghost = Ghost(snake)
    text = GameOver()

    for i in range(n-3):
        part = BodyPart(N, np.array([-(i + 2), 0]), parts[i], i + 2, 'resources/fig/spongebob_bind.obj',
                        'resources/texture/spongebob.png')
        parts.append(part)

    tail = Tail(N, np.array([-(n - 3 + 2), 0]), parts[-1], n - 1, 'resources/fig/spongebob_bind.obj',
                'resources/texture/spongebob.png')
    parts.append(tail)

    t0 = glfw.get_time()
    tIni = t0

    while not glfw.window_should_close(window):

        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Time difference between every execution of the loop
        t1 = glfw.get_time()
        dt = (t1 - t0) * 7
        t0 = t1
        factor = snake.factor
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            snake.direction(1, dt*factor)

        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            snake.direction(-1, dt*factor)

        glClear(GL_COLOR_BUFFER_BIT)

        snake.update(dt*factor)

        for element in parts:
            element.update(dt * factor, snake)

        parts = snake.eat(apple, parts, N, 'resources/fig/spongebob_bind.obj',
                          'resources/texture/spongebob.png')
        snake.collide()

        if controller.camera == 1:
            projection = tr.perspective(80, float(width) / float(height), 0.1, 200)
            sigCamPos = snake.pos - (snake.direct * 10)
            a = sigCamPos[0]
            b = sigCamPos[1]
            c = np.abs(b)
            if a>20 and c<10:
                w = (20-snake.pos[0])/snake.direct[0]
                camPos = snake.pos + (snake.direct * w)
            elif b<-20 and a <10:
                w = (20+snake.pos[1]) / snake.direct[1]
                camPos = snake.pos - (snake.direct * w)
            else:
                camPos = sigCamPos
            camPos = np.array([camPos[0], camPos[1], 4])
            eye = np.array([snake.pos[0], snake.pos[1], 0])
            view = tr.lookAt(
                camPos,
                eye,
                np.array([0, 0, 1])
            )
        elif controller.camera == 3:
            projection = tr.perspective(47, float(width) / float(height), 0.1, 300)
            camPos = np.array([-35, 35, 20])
            eye = np.array([0, 0, 0])
            view = tr.lookAt(
                camPos,
                eye,
                np.array([0, 0, 1])
            )
        else:
            f = 0.52
            projection = tr.ortho(-f*N, f*N, -f*N, f*N, 0.1, 12)
            camPos = np.array([0,0,10])
            view = tr.lookAt(
                camPos,
                np.array([0,0,0]),
                np.array([0, 1, 0])
            )
        radius = 26
        posLight = (radius * np.cos(1.5 * t1 / 2), radius * np.sin(1.5 * t1 / 2), 22)
        if snake.state:
            light1 = np.array([1, 1, 1])
            light2 = np.array([0.2, 0.2, 0.6])
            light = light1 * (np.cos(t1 / 8)) ** 2 + light2 * (np.sin(t1 / 8)) ** 2
        else:
            light = np.array([0.9,0.5,0.5])

        limit.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        snake.draw(textureLightPipeline, projection, view, camPos, posLight, light)

        if snake.state:
            for element in parts:
                element.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        else:
            ghost.update(dt)
            ghost.draw(lightPipeline, projection, view, camPos, posLight, light)

        cactus.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        horizon.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        apple.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        dune.draw(lightPipeline, projection, view, camPos, posLight, light)
        surface.draw(textureLightPipeline, projection, view, camPos, posLight, light)
        pyramids.draw(textureLightPipeline, projection, view, camPos, posLight, light)

        if not snake.state:
            if ghost.height >3:
                projection = tr.ortho(-10, 10, -10, 10, 0.1, 10)
                camPos = np.array([0, 0, 2])
                view = tr.lookAt(
                    camPos,
                    np.array([0, 0, 0]),
                    np.array([0, 1, 0])
                )
                text.draw(texturePipeline, projection, view)

        glfw.swap_buffers(window)

    glfw.terminate()
