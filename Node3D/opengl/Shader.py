from ..vendor.pyqtgraph.opengl.shaders import VertexShader, FragmentShader
from OpenGL.GL import *
from OpenGL.GL import shaders


class Shader(object):
    def __init__(self, name, shaders):
        self.name = name
        self.shaders = shaders
        self.prog = None

    def program(self):
        if self.prog is None:
            try:
                compiled = [s.shader() for s in self.shaders]  # compile all shaders
                self.prog = shaders.compileProgram(*compiled)  # compile program
            except:
                self.prog = -1
                raise
        return self.prog

    def bind(self):
        if len(self.shaders) > 0 and self.program() != -1:
            glUseProgram(self.program())

    def unbind(self):
        if len(self.shaders) > 0:
            glUseProgram(0)

    def __enter__(self):
        self.bind()

    def __exit__(self, *args):
        self.unbind()

    def getUniformLocation(self, name):
        return glGetUniformLocation(self.program(), name.encode('utf_8'))

    def getAttribLocation(self, name):
        return glGetAttribLocation(self.program(), name.encode('utf_8'))

    def setUniform1f(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform1f(loc, value)

    def setUniform1i(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform1i(loc, value)

    def setUniform2f(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform2f(loc, value[0], value[1])

    def setUniform2i(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform2i(loc, value[0], value[1])

    def setUniform3f(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform3f(loc, value[0], value[1], value[2])

    def setUniform3i(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform3i(loc, value[0], value[1], value[2])

    def setUniform4f(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform3f(loc, value[0], value[1], value[2], value[3])

    def setUniform4i(self, name, value):
        loc = self.getUniformLocation(name)
        glUniform3i(loc, value[0], value[1], value[2], value[3])

    def setUniformMatrix3(self, name, value):
        loc = self.getUniformLocation(name)
        glUniformMatrix3fv(loc, 1, False, (ctypes.c_float * 16)(*value))

    def setUniformMatrix4(self, name, value):
        loc = self.getUniformLocation(name)
        glUniformMatrix4fv(loc, 1, False, (ctypes.c_float * 9)(*value))


standShader = Shader('shaded', [
    VertexShader("""
        varying vec3 normal;
        varying vec2 texCoord;
        void main() {
            // compute here for use in fragment shader
            normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
            texCoord = gl_MultiTexCoord0.xy;
        }
    """),
    FragmentShader("""
        varying vec3 normal;
        varying vec2 texCoord;
        uniform int flatColor;
        void main() {
            vec4 color = gl_Color;
            if(flatColor == 0)
            {
                float p = dot(normal, normalize(vec3(1.0, -1.0, -1.0)));
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);
            }
            gl_FragColor = color;
        }
    """)])

IDColorShader = Shader('IDColor', [
    VertexShader("""
        void main() {
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
        }
    """),
    FragmentShader("""
        void main() {
            gl_FragColor = gl_Color;
        }
    """)])

PointShader = Shader('pointSprite', [
    VertexShader("""
        attribute float pscale;
        uniform float unifrom_scale;
        uniform vec3 camPos;
        uniform int pixmode;
        void main() {
            gl_FrontColor=gl_Color;
            gl_Position = ftransform();
            if(unifrom_scale >= 0)
                gl_PointSize = unifrom_scale;
            else
                gl_PointSize = pscale * 0.1;
            if(pixmode == 0)
                gl_PointSize = gl_PointSize * (25 - gl_Position.z);

        } 
    """)])


baseShader = Shader('base', [
    VertexShader("""
#version 130

uniform mat4 u_viewProjectionMatrix;
uniform mat4 u_modelMatrix;
uniform mat3 u_normalMatrix;
uniform vec3 u_lightPos;

uniform vec4 u_materialDiffuse;

in vec3 a_vertex;
in vec3 a_normal;

out vec4 v_color;

void main(void)
{
    // Now the normal is in world space, as we pass the light in world space.
    vec3 normal = u_normalMatrix * a_normal;

    float dist = distance(a_vertex, u_lightPos);

    // att is not used for now
    float att=1.0/(1.0+0.8*dist*dist);

    vec3 surf2light = normalize(u_lightPos - a_vertex);
    vec3 norm = normalize(normal);
    float dcont=max(0.0,dot(norm,surf2light));

    float ambient = 0.3;
    float intensity = dcont + 0.3 + ambient;

    v_color = u_materialDiffuse  * intensity;

    gl_Position = u_viewProjectionMatrix * u_modelMatrix * vec4(a_vertex, 1.0);
}
    """),
    FragmentShader("""
        varying vec3 normal;
        varying vec2 texCoord;
        uniform int flatColor;
        void main() {
            vec4 color = gl_Color;
            if(flatColor == 0)
            {
                float p = dot(normal, normalize(vec3(1.0, -1.0, -1.0)));
                p = p < 0. ? 0. : p * 0.8;
                color.x = color.x * (0.2 + p);
                color.y = color.y * (0.2 + p);
                color.z = color.z * (0.2 + p);
            }
            gl_FragColor = color;
        }
    """)])