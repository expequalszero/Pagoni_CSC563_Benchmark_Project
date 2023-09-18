#Creator: Brian Pagoni, SCSU CSC-563-01 
#This project is desined to allow user to obtain a benchmark for this system and display the results using a gui.   

#importing the different modules that will be used to assist 

from asyncio import futures
import time
import statistics
import tkinter as tk
from tkinter import ttk
import concurrent.futures
import math
from tkinter import font
from turtle import bgcolor


operationsCount = 100_000       # for testing purposes 

def getDeviation(data):          #ran into issue with statistics given off the wall returns for standard deviation. using custom function for time being
    
    average  = sum(data)/len(data) #getting the avergae from the data set 
    
    squDif = [(count - average)**2 for count in data] #getting the square difference 
    
    avgSqu = sum(squDif)/len(squDif) #getting the average of the squared differences
    
    deviation = math.sqrt(avgSqu) #calculating the deviation based on above code.
   
    return deviation  #returning result 




def getOperationCount(typeOp,operation,threadCount): #function for getting the num of operations completed per second
    
    runOps = [] 
    
    for _ in range(3):
        numOps = 0 
        
        startTime = round(time.perf_counter(),6) #getting the start time using performance counter for ms 
        
        while round(time.perf_counter(),6)-startTime <1:   #running a loop for 1 second and getting the number of operatiosn completed.
            eval(operation)
            numOps+=1
        
        runOps.append(numOps) #adding the number of operations to list 
    
    average = sum(runOps)/len(runOps)           #getting average number of operations after completing 3 iterations 
    
    deviation = getDeviation(runOps)             #getting the standard deviation from the data set 
    
    

    return threadCount,typeOp,average, deviation

def threadCountUsed():

    results= []
    numThreads = [1,2,4,8]
    
    #getting base for whatever the computer will do on its own.
    results.append(getOperationCount("float","2.0+1.0","default"))
    results.append(getOperationCount("int","2+1","default"))
    #getting results based on the number of threads used. 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futuresF = [executor.submit(getOperationCount,"float","2.0+1.0",threadCount) for threadCount in numThreads]
        results.extend(future.result() for future in futuresF)
        futuresI = [executor.submit(getOperationCount,"int","2+1",threadCount) for threadCount in numThreads]
        results.extend( future.result() for future in futuresI)
    print( "Completed tasks results returned to user")
    
    return results



def createGUI(data):
    #creating the gui 
    guiDisplay = tk.Tk()
    #set background color
    guiDisplay.config(bg="skyblue")
    guiDisplay.grid_rowconfigure(0,weight=1)
    guiDisplay.grid_columnconfigure(0,weight=1)

    guiDisplay.title("Benchmark Program: CPU Speeds")
    #creating a nested list to hold frames for gui
    frames = [[None for _ in range(4)] for _ in range(10)]
    dataInfo = [[None for _ in range(4)] for _ in range(10)]
    
    headerStyle = ttk.Style() #setting the style up for the gui options
    headerStyle.configure("headerStyle.TLabel", font=("Times New Roman",14,"bold"), background = "lightgrey")
    bodyStyle = ttk.Style()
    bodyStyle.configure("body.TLabel", font =("Times New Roman", 12))


    guiHeaders = ["Number of Threads: ", "Operation Type: ", "Average of Operations per second: ", "Standard Deviation: "]



    for head, headers in enumerate(guiHeaders):
        headerFrame = tk.Frame(guiDisplay, relief="solid", borderwidth=1, bg="lightgrey")
        headerFrame.grid(row=0,column=head,padx =10, pady=10,sticky ="w")
        
        label = ttk.Label(headerFrame, text = headers, anchor ='w', style="headerStyle.TLabel")
        label.grid(row=0,column= head, padx = 10, pady =10, sticky ='w')
        
        

    for row, result in enumerate (cpuSpeeds):
        for col, data in enumerate(result):
               
            dataFrame = tk.Frame(guiDisplay,relief="solid",borderwidth = 1)
            dataFrame.grid(row= row+1, column = col, padx =10, pady=10)
            frames[row][col] = dataFrame
            threadCount = cpuSpeeds[row][0]
            labelText = ""
                
            if col == 1 and data == "float":
                labelText = "Float Operations Per Second: "
            elif col == 1 and data == "int":
                labelText = "Integer Operations Per Second: "
            else:
                labelText = str(data)
         
            label = ttk.Label(dataFrame,text = labelText, anchor = "w", style = "body.TLabel")   
            label.grid(row=row,column = col,sticky ="w")
    guiDisplay.mainloop()

if __name__ == "__main__":
     #creating varibles to get the results 
    cpuSpeeds = threadCountUsed()
    createGUI(cpuSpeeds)
