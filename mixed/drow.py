# global variable
value = 1
  
# function to setup size of
# output window
def setup():
  
    # to set background color of window
    # to white color
    background(255)
  
    # to set width and height of window
    # to 1500px and 1200px respectively
    size(1500, 1200)
  
# function to draw on the window
def draw():
  
    # referring to the global value
    global value
  
    # if mouse is dragged then
    # the value will be set to 0
    # so here by checking if value equal to 0,
    # we are confirming that the mouse is being
    # dragged
    if value == 0:
  
        # width of circle
        r = 10
  
        # to fill the color of circle to black
        fill(0)
  
        # to create a circle at the position of
        # mouse clicked mouseX and mouseY coordinates
        # represents x and y coordinates of mouse
        # respectively when it is being dragged.
        ellipse(mouseX, mouseY, r, r)
  
        # setting value to 1, which means a circle
        # is drawn at current position and waiting
        # for the mouse to be dragged.
        value = 1
  
# this function is called when
# mouse is being dragged (mouse click+ hold + move)
def mouseDragged():
  
    # referring to global value
    global value
  
    # setting value to 0
    value = 0