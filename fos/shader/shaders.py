#
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#
# Modified by Stephan Gerhard, 2010

from ctypes import (
    byref, c_char, c_char_p, c_int, cast, create_string_buffer, pointer, c_float,
    POINTER
)

from pyglet.gl import *

class Shader:
    # vert, frag and geom take arrays of source strings
    # the arrays will be concattenated into one string by OpenGL
    def __init__(self, vert = [], frag = [], geom = []):
        # create the program handle
        self.handle = glCreateProgram()
        # we are not linked yet
        self.linked = False

        # create the vertex shader
        self.createShader(vert, GL_VERTEX_SHADER)
        # create the fragment shader
        self.createShader(frag, GL_FRAGMENT_SHADER)

        if not len(geom) == 0:
            # the geometry shader will be the same, once pyglet supports the extension
            self.createGeometryShader( [geom[0]] , GL_GEOMETRY_SHADER_EXT, geom[1], geom[2], geom[3])

        # attempt to link the program
        self.link()

    def retrieveAttribLocation(self, name):
        """ Call only after linking
        """
        return glGetAttribLocation(self.handle, name)

    def createShader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (c_char_p * count)(*strings)
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        # compile the shader
        glCompileShader(shader)

        temp = c_int(0)
        # retrieve the compile status
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))

        # retrieve the log length
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
        # create a buffer for the log
        buffer = create_string_buffer(temp.value)
        # retrieve the log text
        glGetShaderInfoLog(shader, temp, None, buffer)
        
        # print the log to the console
        print buffer.value

        # all is well, so attach the shader to the program
        glAttachShader(self.handle, shader)

    def createGeometryShader(self, strings, type, input_type, output_type, vertices_out):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (c_char_p * count)(*strings)
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        # compile the shader
        glCompileShader(shader)

        temp = c_int(0)
        # retrieve the compile status
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))

        # if compilation failed, print the log
        # retrieve the log length
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
        # create a buffer for the log
        buffer = create_string_buffer(temp.value)
        # retrieve the log text
        glGetShaderInfoLog(shader, temp, None, buffer)
        # print the log to the console

        print("Geometry shader compiled.")

        # And define the input and output of the geometry shader, point and triangle strip in this case. Four is how many the vertices the shader will create.

        #glProgramParameteriEXT(self.handle, GL_GEOMETRY_INPUT_TYPE_EXT, input_type)
        #glProgramParameteriEXT(self.handle, GL_GEOMETRY_OUTPUT_TYPE_EXT, output_type)
        #glProgramParameteriEXT(self.handle, GL_GEOMETRY_VERTICES_OUT_EXT, vertices_out)

        print buffer.value

        # all is well, so attach the shader to the program
        glAttachShader(self.handle, shader);


    def link(self):
        # link the program
        glLinkProgram(self.handle)

        temp = c_int(0)
        # retrieve the link status
        glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))

        #    retrieve the log length
        glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
        # create a buffer for the log
        buffer = create_string_buffer(temp.value)
        # retrieve the log text
        glGetProgramInfoLog(self.handle, temp, None, buffer)
        # print the log to the console
        print buffer.value

        # print the log
        if temp:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        # bind the program
        glUseProgram(self.handle)

        #glEnableVertexAttribArray(0)
        #glEnableVertexAttribArray(1)
#        glEnable(GL_TEXTURE_1D)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        glUseProgram(0)

#        glDisableVertexAttribArray(0)
#        glDisableVertexAttribArray(1)
#        glDisable(GL_TEXTURE_1D)

    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1f,
                2 : glUniform2f,
                3 : glUniform3f,
                4 : glUniform4f
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1i,
                2 : glUniform2i,
                3 : glUniform3i,
                4 : glUniform4i
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)

    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
        # obtian the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # uplaod the 4x4 floating point matrix
        glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))
