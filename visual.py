from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys

name = "Vizualizer Test"

def init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400, 400)
    glutCreateWindow(name)

    # background color
    glClearColor(0., 0., 0., 1.)

    # flat or smooth
    glShadeModel(GL_SMOOTH)

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


    glEnable(GL_LIGHTING)
    lightZeroPosition = [10.,4.,10.,100.]
    lightZeroColor = [1,1,1,1.0] #green tinged

    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)


def draw_ball():
    glutSolidSphere(2, 20, 20)


def display():
    global sphereLocations
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    for i in range(-100,100,5):
        glPushMatrix()
        glTranslatef(i,0,1)
        color = [1.0,0.,0.,1.]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
        draw_ball()
        glPopMatrix()
    glFlush()
    glutSwapBuffers()
    glutPostRedisplay()


def main():

    init()

    glutDisplayFunc(display)
    #glMatrixMode(GL_PROJECTION)

    #distance
    gluPerspective(100.,1.,1.,400.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(-10,0,50,
              -10,0,0,
              0,1,0)
    glutMainLoop()

    #return

if __name__ == '__main__': main()
