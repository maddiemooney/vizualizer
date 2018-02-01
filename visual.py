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

    def __init__(self):

        self.chunk = 2048
        self.channels = 1
        self.rate = 44100

        # open stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        output=True,
                        stream_callback=self.callback)
        self.stream.start_stream()

    def callback(self, in_data):

        # read some data
        data = np.fromstring(in_data, dtype=np.float32)
        # play stream and find the frequency of each chunk
        while len(data) == self.chunk * self.swidth:
            # write data out to the audio stream
            self.stream.write(data)
            # unpack the data and times by the hamming window
            indata = np.array(wave.struct.unpack("%dh" % (len(data) / self.swidth), data)) * self.window
            # Take the fft and square each value
            fftData = abs(np.fft.rfft(indata)) ** 2
            # find the maximum
            which = fftData[1:].argmax() + 1
            # use quadratic interpolation around the max
            if which != len(fftData) - 1:
                y0, y1, y2 = np.log(fftData[which - 1:which + 2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                # find the frequency and output it
                thefreq = (which + x1) * self.rate / self.chunk
                print("The freq is %f Hz." % thefreq)
            else:
                thefreq = which * self.RATE / self.chunk
                print("The freq is %f Hz." % thefreq)
            # read some more data
            data = self.wf.readframes(self.chunk)
        if data:
            self.stream.write(data)
        self.stream.close()
        p.terminate()






def main():
    #Visual().visualmain()
    Audio().getfreq()

main()

