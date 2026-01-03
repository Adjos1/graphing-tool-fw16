import math
import time
from tqdm import tqdm
import serial
import sympy
import numpy as np

width = 9
height = 34
Auto = 0
Minx = "I am a placeholder"
Maxx = "I am a placeholder"
Miny = "I am a placeholder"
Maxy = "I am a placeholder"
howlong = "I am a placeholder"
CalculationsPerPixel = "i am a placeholder"
Minxsmallerthen0 = ")"
Maxandminy = "I am a placeholder"
Helpstring = "I am a placeholder"
phi = 1.618033988749894848204586834365638117720309
psi = -0.618033988749894848204586834365638117720309
g = 9.81035
gamma = 0.57721566490153286060651209008240243104215933593992 #makeing some constants available
Display10th = 0
Port_right = serial.Serial(port="/dev/ttyACM1", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE) #right LED Matrix
Port_left = serial.Serial(port="/dev/ttyACM0", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE) #left LED Matrix
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
def iscomplex(string):
    try:
        np.complex128(string)
        return True
    except ValueError:
        return False
def isavaluatable(string):
    try:
        sympy.sympify(string)
        if  str(sympy.sympify(string)) != "zoo":
            string = str(sympy.sympify(string).evalf())
            string = string.replace("*I", "j")
            string = string.replace(" ", "")
            return iscomplex(string)
        else:
            return True
    except:
        return False
def makeavaluatable(string): # makes some constants accessible
    string = string.replace("sin(", "cos(-0.5*pi+") # sin has i in it, wich we later replace with root -1
    string = string.replace("e",str(math.e))
    string = string.replace("tau","pi*2")
    string = string.replace("pi",str(math.pi))
    string = string.replace("phi",str(phi))
    string = string.replace("psi","(" + str(psi) + ")")
    string = string.replace("i","(-1)**(1/2)").replace("j","(-1)**(1/2)")
    string = string.replace("gamma",str(gamma))
    string = string.replace("g",str(g))
    return string
def devidearraywithNaN(array,number):
    for i in range(len(array)):
        if array[i] != "NaN":
            array[i] = array[i] / number
    return array
def subarraywithNaN(array,number):
    for i in range(len(array)):
        if array[i] != "NaN":
            array[i] -= number
    return array
def minwithNaNandcomplex(array):
    helparray = [0 for x in range(len(array))]
    for i in range(len(array)):
        helparray[i] = array[i] # when I used the original array, it would always remove all "NaN"s, I don't know if array.copy would work.
    while helparray.count("NaN") != 0:
        helparray.remove("NaN")
    for i in range(len(helparray)):
        helparray[i] = float(helparray[i].real)
    if len(helparray) > 0:
        return min(helparray)
    else:
        return 0
def maxwithNaNandcomplex(array):
    helparray = [0 for x in range(len(array))]
    for i in range(len(array)):
        helparray[i] = array[i]  # when I used the original array, it would always remove all "NaN"s, I don't know if array.copy would work.
    while helparray.count("NaN") != 0:
        helparray.remove("NaN")
    for i in range(len(helparray)):
        helparray[i] = float(helparray[i].real)
    if len(helparray) > 0:
        return max(helparray)
    else:
        return 0        # for the array to be able to hold values that it doesn't display, while being able to display all values, there needs to be functions that are able to work with NaN
def seperate_reel_imag(array):
    for i in range(len(array)):
        if array[i] != "NaN":
            reelarray[i] = array[i].real
            imagarray[i] = array[i].imag
            if imagarray[i] != 0:
                array[i] = "NaN"

        else:
            reelarray[i] = 0
            imagarray[i] = 0
    #print(array)
def functiontoarray(function,maxx,minx,maxy,miny,displayimaginaray,display10th,calculationsPerPixel):
    global reelarray
    global imagarray
    height_per_calculation = ((maxx - minx) / (height - 1)) / calculationsPerPixel
    #print(function)
    function = makeavaluatable(function)
    function = function.replace("x", "((x*" + str(height_per_calculation) + ")+" + str(minx) + ")")#.replace("j","(-1)**(1/2)")  # scales the available pixels between minx and maxx
    print("calculating the values")
    outputarray = [1 for x in range(height * calculationsPerPixel - calculationsPerPixel + 1)]
    for y in tqdm(range(height * calculationsPerPixel - calculationsPerPixel + 1)): #  the sides still only calculate to the user - given max value. that means they need less pixels. the formula for how many less is (calc.perpixel - 1 ) / 2. multiplied by 2 and distributing the minus, the term equates to -calc.perpixel + 1
        #print(y)
        helpstring = function.replace("x",str(y))
        #print(helpstring)
        if isavaluatable(helpstring): #this is mostly for the gamma-function. sympy just gives an error if we take (-5)! for example.
            if not "zoo" in str(sympy.sympify(helpstring)): # we don't like dealing with zoo, nor can we display it , zoo is the result of x/0
                outputarray[y] = str(sympy.sympify(helpstring).evalf()) #I had problems with square-roots without the evalf function
                outputarray[y] = outputarray[y].replace("*I","j")
                outputarray[y] = outputarray[y].replace(" ","")
                #print(outputarray[y])
                #print(95)
                outputarray[y] = np.complex128(outputarray[y])
            else:
                outputarray[y] = "NaN"
        else:
            outputarray[y] = "NaN"
    #print(outputarray)
    seperate_reel_imag(outputarray)
    if Auto > 0:
        if displayimaginaray == 1:
            miny = minwithNaNandcomplex(outputarray) #sets maxy to the highest value if auto is true
        else:
            miny = minwithNaNandcomplex(reelarray)
    miny = float(miny)
    if Auto > 0:
        if displayimaginaray == 1:
            if maxwithNaNandcomplex(outputarray) - miny != 0: # if it where 0 we would devide by 0 later on.
                maxy = maxwithNaNandcomplex(outputarray) #sets maxy to the highest value if auto is true
            else:
                maxy = miny + 1
        elif maxwithNaNandcomplex(reelarray) - miny != 0:
            maxy = maxwithNaNandcomplex(reelarray)
        else:
            maxy = miny + 1
    maxy = float(maxy)
    lenght_per_pixel = (maxy - miny) / (width * 2 * imaginary - 1  + display10th)
    outputarray = subarraywithNaN(outputarray, miny) #reorients the graph to let miny be the lowest displayed point (0)
    outputarray = devidearraywithNaN(outputarray,lenght_per_pixel) # adjusts the scale of the graph so that maxy is the highest displayed point
    reelarray = subarraywithNaN(reelarray,miny)
    reelarray = devidearraywithNaN(reelarray,lenght_per_pixel) #same as above, only important if the imag. part is being displayed
    if Auto == 1:
        miny = minwithNaNandcomplex(imagarray)
        miny = float(miny)
        if maxwithNaNandcomplex(imagarray) - miny != 0:
            maxy = maxwithNaNandcomplex(imagarray)
        else:
            maxy = miny + 1
    maxy = float(maxy)
    lenght_per_pixel = (maxy - miny) / (width * 2 * imaginary - 1 + display10th)
    print("calculating the pixels")
    imagarray = subarraywithNaN(imagarray, miny)
    imagarray = devidearraywithNaN(imagarray, lenght_per_pixel)
    #print(outputarray)
     # calculates the y position of each pixel (in this case x is the height and y the width of the LED matrix)
    #print(imagarray)
    #print(lenght_per_pixel)
    #print(miny)
    #print(maxy)
    displayarray = [[0 for x in range(width * 2 + display10th)] for y in range(height)]
    if imaginary == 1: #imaginarry is 1 if the imaginary part isnt displayed since the display stays the same size.
        for x in tqdm(range(height * calculationsPerPixel - calculationsPerPixel + 1)):
            if not "NaN" in str(outputarray[x]) and not "nan" in str(outputarray[x]) and (width * 2 - 1) + display10th >= round(outputarray[x].real) >= 0:
                #print(outputarray[x])
                displayarray[round(x / calculationsPerPixel)][round(outputarray[x].real)] = 1
    else:
        for x in tqdm(range(height * calculationsPerPixel - calculationsPerPixel + 1)):
            if not "NaN" in str(reelarray[x]) and not "nan" in str(reelarray[x]) and (width * 2 - 1) + display10th >= round(reelarray[x].real) >= 0:
                displayarray[round(x / calculationsPerPixel)][round(reelarray[x])] = 1
            if not "NaN" in str(imagarray[x]) and not "nan" in str(imagarray[x]) and (width * 2 - 1) + display10th >= round(imagarray[x].real) >= 0:
                displayarray[round(x / calculationsPerPixel)][round(imagarray[x]) + 9] = 1
                #print(outputarray[x])
    return displayarray
def display(rightorleft, array):
    displayArray = [0 for x in range(42)]
    expo = 0
    byteValue = 0
    i = 3
    displayArray[0] = 0x32
    displayArray[1] = 0xAC
    displayArray[2] = 0x06
    for y in range(height):
        for x in range(width):
            byteValue = byteValue + (2 ** expo) * array[x][y]
            expo = expo + 1
            if (expo == 8):
                displayArray[i]=byteValue
                i = i + 1
                expo=0
                byteValue=0
    displayArray[i]=byteValue
    if(rightorleft != 0):
        Port_right.write(displayArray)
    else:
        Port_left.write(displayArray)

def display2displays(array, display10th):
    arraytodisplayleft = [[0 for x in range(height)] for y in range(width)]
    arraytodisplayright = [[0 for x in range(height)] for y in range(width)]
    for i in range(height):
        for j in range(width):
          arraytodisplayleft[j][i] = array[i][j]
          arraytodisplayright[j][i] = (array[i][j + width + display10th])
    display(0,arraytodisplayleft)
    display(1,arraytodisplayright)
while not isavaluatable(Helpstring): #start of dialogue with user
    print("please enter your function, remember to use * (this means e.g. 5*x instead of 5x)")
    Function = str(input())
    Helpstring =Function
    Helpstring = Helpstring.replace("x", "tau") # testing an arbitrary value.
    Helpstring = makeavaluatable(Helpstring)
while not iscomplex(Minx):
    print("where should it start?(complex)")
    Minx = input()
    Minx = makeavaluatable(Minx)
    if isavaluatable(Minx):
        Minx = str(sympy.sympify(Minx).evalf())
        Minx = Minx.replace("*I", "j")
        Minx = Minx.replace(" ", "")
Minx = np.complex128(Minx)
if Minx != 0:
    Minxsmallerthen0 = " (or a for -the smallest value))"
while not( (iscomplex(Maxx) and np.complex128(Maxx) - np.complex128(Minx)) != 0 or ((Maxx == "a" or Maxx == "A") and Minx != 0)):
    print("where should it end(complex" + Minxsmallerthen0) # bracket is always closed since Minxsmallerteno is ")" by default
    Maxx = input()
    Maxx = makeavaluatable(Maxx)
    if isavaluatable(Maxx):
        Maxx = str(sympy.sympify(Maxx).evalf())
        Maxx = Maxx.replace("*I", "j")
        Maxx = Maxx.replace(" ", "")
if Maxx == "a" or Maxx == "A":
    Maxx = -Minx
Maxx = np.complex128(Maxx)
while not (isfloat(Maxy) and isfloat(Miny) and float(Miny) < float(Maxy) or Maxandminy == "a" or Maxandminy == "A"):
    print("what should the lowest and highest value be? (form: Low;High, a for Auto)")
    Maxandminy = input()
    if not Maxandminy == "a" or Maxandminy == "A":
        if Maxandminy.count(";") == 1:
            Miny = Maxandminy[0:Maxandminy.index(";")]
            Maxy = Maxandminy[Maxandminy.index(";") + 1:]
    else:
        Auto = 1
while not(isint(CalculationsPerPixel) and int(CalculationsPerPixel) > 0):
    print("how many calculations should be made per Pixel?(recommended: odd, must be: int > 0, a for 1)")
    CalculationsPerPixel = input()
    if CalculationsPerPixel == "a" or CalculationsPerPixel == "A":
        CalculationsPerPixel = 1
CalculationsPerPixel = int(CalculationsPerPixel)
reelarray = [0 for x in range(height * CalculationsPerPixel - CalculationsPerPixel + 1)]
imagarray = [0 for x in range(height * CalculationsPerPixel -CalculationsPerPixel + 1)]
print("should the imaginary part be displayed? (1 or yes if yes)")
imaginary = input()
if imaginary == "1" or imaginary == "yes" or imaginary == "Yes":
    imaginary = 1/2 #half the screensize for the reel and half of the screensize for the imag. part
    if Auto == 1:
        print("should the imaginary and real scaling be the same)? (1 or yes if yes)")
        Auto = input()
        if Auto == "1" or Auto == "yes" or Auto == "Yes":
            Auto = 2
        else:
            Auto = 1
else:
    imaginary = 1
    print("should the 10th row be displayed? (1 or yes if yes)")
    Display10th =input() # end of dialogue with user
    if Display10th == "1" or Display10th == "yes" or Display10th == "Yes":
        Display10th = 0
    else:
        Display10th = 1 # there is one extra row if it isn't displayed1
while not (isint(howlong) and int(howlong) >= 0 or howlong == "a" or howlong == "A"):
    print("how long should it be displayed?(int, in minutes, a for inf)")
    howlong = input()
if not howlong == "a" or howlong == "A":
    howlong = int(howlong)

THEHOLYARRAY = functiontoarray(Function,Maxx,Minx,Maxy,Miny,imaginary,Display10th,CalculationsPerPixel)

while howlong =="a" or howlong == "A" or howlong >= 0:
    display2displays(THEHOLYARRAY,Display10th)
    if not howlong == "a" or howlong == "A":
        howlong -= 0
    time.sleep(10)
    display2displays(THEHOLYARRAY,Display10th)
    time.sleep(50)