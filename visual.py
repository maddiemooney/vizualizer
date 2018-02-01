from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math

name = "Vizualizer Test"

class Visual:

    def initbg(self):
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


    def lighting(self):

        glEnable(GL_LIGHTING)
        lightZeroPosition = [0., 0., 1., 0.]  # aligned with z axis
        lightZeroColor = [1, 1, 1, 1.0]  # green tinged
        # (light, source, param)
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)



    def draw_ball(self,x,y,z):
        #(radius,slices,stacks)
        if x%2==0:
            glTranslatef(x, math.sin(.25*y)*2, z)
        else:
            glTranslatef(x, math.sin(.38*y)*4, z)
        glutSolidSphere(2, 10, 10)

    def display(self):
        for j in range(50):
            #clear
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            for i in range(-100,100,5):  #(-100,100,5)
                glPushMatrix()
                color = [1.0,0.,0.,1.] #red atm
                #(face, pname, param)
                glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
                self.draw_ball(i,j,0)
                glPopMatrix()

            glFlush()
            glutSwapBuffers()
            glutPostRedisplay()


    def audiomain(self):

        self.initbg()
        self.lighting()
        glutDisplayFunc(self.display)

        #distance
        gluPerspective(100.,1.,1.,400.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(-10,0,50,
                  -10,0,0,
                  0,1,0)
        glutMainLoop()

class Audio:

    def ree(self):
        print("heck")


def main():
    Visual().audiomain()

main()

