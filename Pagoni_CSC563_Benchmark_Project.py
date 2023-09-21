#Creator: Brian Pagoni, SCSU CSC-563-01 
#This project is desined to allow user to obtain a benchmark for this system and display the results using a gui.   

#importing the different modules that will be used to assist 

from asyncio import futures
import time
import threading
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
    
    deviation = round(math.sqrt(avgSqu),6) #calculating the deviation based on above code.
   
    return deviation,average  #returning result 




def getCounts(testType, operation,threadCount): #function for getting the num of operations completed per second, some arguments are needed for return to track 
    setOpsCount =100_000
    opsCount = [] 
    durationCount = []
    deviation,average = 0,0
    for _ in range(3):
        if(testType == "setNumTime"):
            numOps = 0 
            startTime = round(time.perf_counter(),6) #getting the start time using performance counter for ms 
        
            while round(time.perf_counter(),6)-startTime <1:   #running a loop for 1 second and getting the number of operatiosn completed.
                eval(operation)
                numOps+=1
        
            opsCount.append(numOps) #adding the number of operations to list 
        
        else:
            startTime = round(time.perf_counter(),6)
            for _ in range(setOpsCount):
                eval(operation)
            endTime =  round(time.perf_counter(),6)
            duration = endTime-startTime
            opsPerSec = setOpsCount/duration
            durationCount.append(opsPerSec)
            
    if(testType == "setNumTime"):
       deviation,average = getDeviation(opsCount) 
    else:   
       deviation,average = getDeviation(durationCount) 

    return threadCount,average, deviation #returning thread count, operation type, average and deviation 


def threadCountUsed(benchType):

    results= []
    numThreads = [1,2,4,8]
    
   
    results.extend([("float",) + getCounts(benchType,"2.0+1.0","default")])  #getting base for whatever the computer will do on its own.
    results.extend([("int",) + getCounts(benchType,"2+1","default")])
    
    with concurrent.futures.ThreadPoolExecutor() as executor: #getting results based on the number of threads used, using thread pool executor . 
        futuresF = [executor.submit(getCounts,benchType,"2.0+1.0",threadCount) for threadCount in numThreads]
        results.extend((("float",) + future.result()) for future in futuresF)
        futuresI = [executor.submit(getCounts,benchType,"2+1",threadCount) for threadCount in numThreads]
        results.extend((("int",) + future.result()) for future in futuresI)
    print( "Completed tasks for set time, results returned to user")
    return results






def createGUI(cpuSpeeds,type):
    #creating the gui 
    guiDisplay = tk.Tk()
    #set background color
    guiDisplay.config(bg="skyblue")
    guiDisplay.grid_rowconfigure(0,weight=1)
    guiDisplay.grid_columnconfigure(0,weight=1)

    guiDisplay.title(f"Benchmark Program: CPU Speeds {type}")
    #creating a nested list to hold frames for gui
    frames = [[None for _ in range(4)] for _ in range(len(cpuSpeeds))]
    dataInfo = [[None for _ in range(4)] for _ in range(len(cpuSpeeds))]
    
    headerStyle = ttk.Style() #setting the style up for the gui options
    headerStyle.configure("headerStyle.TLabel", font=("Times New Roman",14,"bold"), background = "lightgrey")
    bodyStyle = ttk.Style()
    bodyStyle.configure("body.TLabel", font =("Times New Roman", 12))


    guiHeaders = [ "Operation Type: ","Number of Threads: ", "Average of Operations per second: ", "Standard Deviation: "]



    for head, headers in enumerate(guiHeaders):
        headerFrame = tk.Frame(guiDisplay, relief="solid", borderwidth=1, bg="lightgrey")
        headerFrame.grid(row=0,column=head,padx =10, pady=10,sticky ="w")
        
        label = ttk.Label(headerFrame, text = headers, anchor ='w', style="headerStyle.TLabel")
        label.grid(row=0,column= head, padx = 10, pady =10, sticky ='w')
        
        

    for row, result in enumerate (cpuSpeeds):
        print("row " ,row, "result: ", result)
        
        
        for col, data in enumerate(result):
            print("col: ", col, "data: ", data)
              
            dataFrame = tk.Frame(guiDisplay,relief="solid",borderwidth = 1)
            dataFrame.grid(row= row+1, column = col, padx =10, pady=10)
            frames[row][col] = dataFrame
            threadCount = cpuSpeeds[row][1]
            labelText = ""
                
            if col == 0 and data == "float":
                labelText = "Float Operations Per Second (FLOPS): "
            elif col == 0 and data == "int":
                labelText = "Integer Operations Per Second (IOPS): "
            else:
                labelText = str(data)
         
            label = ttk.Label(dataFrame,text = labelText, anchor = "w", style = "body.TLabel")   
            label.grid(row=row,column = col,sticky ="w")
    guiDisplay.mainloop()

if __name__ == "__main__":
     #creating varibles to get the results 
    cpuSpeedsTime = threadCountUsed("setNumTime")
    cpuSpeedsOps = threadCountUsed("setNumOps")
    titleTime = "Using a Set Amount of Time."
    titleOps = "Using a Set Amount of Operations."
    threadForTime = threading.Thread(target=createGUI, args=(cpuSpeedsTime,titleTime, ))
    threadForOps = threading.Thread(target=createGUI, args=(cpuSpeedsOps,titleOps, ))

    threadForTime.start()
    threadForOps.start()

    threadForTime.join()
    threadForOps.join()