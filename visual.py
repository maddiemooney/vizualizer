from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys



name = "Vizualizer Test"

def init():
    glutInit(sys.argv)

    #initializes double buffered window, RGBA mode, depth buffer
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400, 400)
    glutCreateWindow(name)

    # background color (red, green, blue, alpha)
    glClearColor(0., 0., 0., 1.)

    # flat or smooth
    glShadeModel(GL_SMOOTH)

    #some graphics stuff about rendering faces
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)

    #projection matrix replaced with identity matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


    glEnable(GL_LIGHTING)
    lightZeroPosition = [0.,0.,1.,0.] #aligned with z axis
    lightZeroColor = [1,1,1,1.0] #green tinged

    #(light, source, param)
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)


def draw_ball():
    #(radius,slices,stacks)
    glutSolidSphere(2, 10, 10)


def display():
    #clear
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    for i in range(-100,100,5):
        glPushMatrix()
        glTranslatef(i,0,0) #translation vector
        color = [1.0,0.,0.,1.] #red atm
        #(face, pname, param)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
        draw_ball()
        glPopMatrix()
    glFlush()
    glutSwapBuffers()
    glutPostRedisplay()


def main():

    init()

    glutDisplayFunc(display)

    #distance
    gluPerspective(100.,1.,1.,400.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(-10,0,50,
              -10,0,0,
              0,1,0)
    glutMainLoop()


if __name__ == '__main__': main()
