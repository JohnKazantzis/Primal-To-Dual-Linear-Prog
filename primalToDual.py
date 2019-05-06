#!/usr/bin/env python3
#coding: utf-8
import re
import sys
import copy

def outputtingData(minMax, dualA, w, b, dualEqin,c):
    outFile = open("output.txt","w")

    #Adding signs
    for x in dualA:
        for j in range(len(x)):
            if len(x[j]) == 1:
                x[j] = "+" + x[j]

    for j in range(len(b)):
        if len(b[j]) == 1:
            b[j] = "+" + b[j]

    for j in range(len(c)):
        if len(c[j]) == 1:
            c[j] = "+" + c[j]


    #Writing min/max
    if minMax == 1:
        outFile.write("max ")
    else:
        outFile.write("min ")
    #outFile.write("c = ")

    for x in range(len(w)):
        outFile.write(str(b[x]))
        outFile.write(str(w[x]))
        outFile.write(" ")

    outFile.write("\ns.t\t")

    #Creating the xi vars
    n = len(dualA[0])
    xVar = []
    for x in range(n):
        xVar.append("x" + str(x+1))


    for x in range(len(dualA)):
        for j in range(len(dualA[x])):
            outFile.write(dualA[x][j])
            outFile.write(xVar[j])
            outFile.write(" ")
        outFile.write(dualEqin[x])
        outFile.write(" ")
        outFile.write(c[x])
        outFile.write("\n\t")

    outFile.write("w ≥ 0")

    outFile.close()

def inputtingData(fileLines):
    #Storing Min or max
    minMax = re.findall("max|min",fileLines[0])
    if minMax[0] == "max":
        minMax = 1
    else:
        minMax = -1

    #Storing c
    c = []
    j=0
    fileLines[0] = re.sub("\A\s*min|max","",fileLines[0])
    c = re.findall("\s*[+-]*\s*\d*[a-zA-Z]",fileLines[0])
    for x in c:
        c[j] = re.sub("x","",c[j])
        c[j] = re.sub("\s","",c[j])
        if c[j] == "":
            c[j] = re.sub("","1",c[j])
        elif c[j] == "+":
            c[j] = re.sub("[+]","+1",c[j])
        elif c[j] == "-":
            c[j] = re.sub("[-]","-1",c[j])
        j = j + 1

    #Storing the A
    A = []
    j=0
    for y in range(1,len(fileLines)-1):
        A.append(re.findall("\s*[+-]*\s*\d*[a-zA-Z]",fileLines[y]))
        for x in A[y-1]:
            A[y-1][j] = re.sub("x","",A[y-1][j])
            A[y-1][j] = re.sub("\s","",A[y-1][j])
            if A[y-1][j] == "":
                A[y-1][j] = re.sub("","1",A[y-1][j])
            elif A[y-1][j] == "+":
                A[y-1][j] = re.sub("[+]","+1",A[y-1][j])
            elif A[y-1][j] == "-":
                A[y-1][j] = re.sub("[-]","-1",A[y-1][j])
            j = j + 1
        j = 0

    #Storing Eqin
    Eqin = []
    for x in range(1,len(fileLines)-1):
        if re.search("≥",fileLines[x]) != None:
            Eqin.append(1)
        elif re.search("≤",fileLines[x]) != None:
            Eqin.append(-1)
        else:
            Eqin.append(0)

    #Storing b
    b = []
    for x in range(1,len(fileLines)-1):
        b.append(re.findall("[+-]*\d\d*\s*\Z",fileLines[x]))

    tmpb = []
    for x in b:
        for j in x:
            tmpb.append(j)
    b = tmpb

    return minMax, A, c, b, Eqin

def inputCheck(fileLines):
    numOfVars = 0
    numOfSigns = 0
    invalidInput = False

    #Checking if there is mix or max before z
    minMaxCheck = re.search("(\A(\s)*max\s)|(\A(\s)*min\s)",fileLines[0])

    if(minMaxCheck == None):
        print("Invalid input!")
        invalidInput = True

    #Checking if there is st,s.t. or subject to before the first constrain
    stCheck = re.search("\A(\s)*st\s|\A(\s)*s.t.\s|\A(\s)*subject to\s",fileLines[1])
    if(stCheck == None):
        print("Invalid input!")
        invalidInput = True

    #(z) -> Checking if all the variables have signs
    subLine = re.sub("\A\s*min|max","",fileLines[0])

    zSignCheck = re.findall("([a-zA-Z]\d\d*)",subLine)
    numOfVars = numOfVars + len(zSignCheck)

    zSignCheck = re.findall("[+-]",subLine)
    numOfSigns = numOfSigns + len(zSignCheck)

    zSignCheck = re.search("(\A\s*[+-]\d*[a-zA-Z])",subLine)
    if zSignCheck == None:
        numOfSigns = numOfSigns + 1

    if numOfVars != numOfSigns:
        print("Invalid input!")
        invalidInput = True

    #(Constrains) -> Checking if all the variables have signs
    #Same as the z sign check
    #The z signs could have been checked with the constrain signs
    #inside the for loop
    for x in range(1,len(fileLines)-1):
        constrainSignCheck = re.findall("([a-zA-Z]\d\d*)",fileLines[x])
        numOfVars = numOfVars + len(constrainSignCheck)

        constrainSignCheck = re.findall("[+-]",fileLines[x])
        numOfSigns = numOfSigns + len(constrainSignCheck)

        if x==1:
            fileLines[x] = re.sub("\A\s*st|s.t.|subject\sto","",fileLines[x])

        constrainSignCheck = re.search("(\A\s*[+-]\d*[a-zA-Z])",fileLines[x])
        if constrainSignCheck == None:
            numOfSigns = numOfSigns + 1

    if numOfVars != numOfSigns:
        print("Invalid input!")
        invalidInput = True

    #(Constrains) -> Checking if the (≤, =, ≥) and bi exist
    for x in range(1,len(fileLines)-1):
        compSignCheck = re.search("([≤≥=]\s*\d\s*\Z)|([≤≥=]\s*\d\s*\n)",fileLines[x])
        if compSignCheck == None:
            print("Invalid input!")
            invalidInput = True

def PrimalToDual(minMax, A, c, b, Eqin):
    #Changing:
    #Min -> Max
    #Max -> Min
    if minMax == -1:
        minMax = 1
    else:
        minMax = -1

    #Num of Wi -> Num of technological constrains
    n = len(b)
    w = []
    for x in range(n):
        w.append("w" + str(x+1))

    numOfc = len(c)
    dualA = []
    tmpdualA = []
    for x in range(numOfc):
        for i in A:
            tmpdualA.append(i[x])
        dualA.append(copy.deepcopy(tmpdualA))
        tmpdualA.clear()

    # x>=0 -> ">="
    dualEqin = []
    for x in range(numOfc):
        dualEqin.append("≥")
    return dualA, w, minMax, dualEqin

def main():
    fileLines = []

    if len(sys.argv) != 2:
        print("Use python3 primalToDual.py -h or python3 primalToDual.py --help")
        print("to learn how to run the script")
        exit(0)

    if sys.argv[1]== "-h" or sys.argv[1]== "--help":
        print("Usage: python3 primalToDual.py [Input File Name]")
        exit(0)

    #Opening text file
    input_obj = open(sys.argv[1],"r")
    input = input_obj.read()

    #Splitting the string's lines
    for line in input.splitlines():
        fileLines.append(line)

    #Calling the function responsible for checking the input
    inputCheck(fileLines)
    #Calling the function responsible for storing the data
    minMax, A, c, b, Eqin = inputtingData(fileLines)

    dualA, w, minMax, dualEqin = PrimalToDual(minMax, A, c, b, Eqin)

    outputtingData(minMax, dualA, w, b, dualEqin,c)

    print("The convertion was successful please check the output.txt file")


if __name__ == '__main__':
    main()
