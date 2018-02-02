from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math

import pyaudio
import wave
import numpy as np


class Visual:

    def __init__(self):
        self.name = "Vizualizer Test"

    def initbg(self):
        glutInit(sys.argv)

        #initializes double buffered window, RGBA mode, depth buffer
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(400, 400)
        glutCreateWindow(self.name)

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
        x1 = x/5
        #print(x1)
        if x1==0:
            glTranslatef(x, math.sin(y)*10, z)

        else:
            glTranslatef(x, math.sin(.166*y)*10, z)
        glutSolidSphere(2, 10, 10)

    def display(self):
        for j in range(100):
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


    def visualmain(self):

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

    def audiomain(self):

        CHUNK = 4096  # number of data points to read at a time
        RATE = 44100  # time resolution of the recording device (Hz)
        TARGET = 440  # show only this one frequency

        p = pyaudio.PyAudio()  # start the PyAudio class
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                        frames_per_buffer=CHUNK)  # uses default input device

        # create a numpy array holding a single read of audio data
        for i in range(30):  # to it a few times just to see
            data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
            fft = abs(np.fft.fft(data).real)
            fft = fft[:int(len(fft) / 2)]  # keep only first half
            freq = np.fft.fftfreq(CHUNK, 1.0 / RATE)
            freq = freq[:int(len(freq) / 2)]  # keep only first half
            assert freq[-1] > TARGET, "ERROR: increase chunk size"
            val = fft[np.where(freq >= TARGET)[0][0]]
            print(val)

        # close the stream gracefully
        stream.stop_stream()
        stream.close()
        p.terminate()



def main():
    #Visual().visualmain()
    Audio().audiomain()

main()

