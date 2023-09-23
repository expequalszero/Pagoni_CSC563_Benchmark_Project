#Creator: Brian Pagoni, SCSU CSC-563-01 
#This project is desined to allow user to obtain a benchmark for this system and display the results using a gui.   

#importing the different modules that will be used to assist 



import time

import tkinter as tk
from tkinter import ttk
import concurrent.futures
import math

gui = tk.Tk()
gui.config(bg="skyblue",pady=20)   

    
def getDeviation(data):          #ran into issue with statistics given off the wall returns for standard deviation. using a custom deviation function for time being
    
    average  = sum(data)/len(data) #getting the avergae from the data set 
    
    squDif = [(count - average)**2 for count in data] #getting the square difference 
    
    avgSqu = sum(squDif)/len(squDif) #getting the average of the squared differences
    
    deviation = round(math.sqrt(avgSqu),6) #calculating the deviation based on above code.
   
    return deviation,average  #returning result 

def getCounts(testType, operation,threadCount):         #function for getting require results, broken into two options. 
     
    setOpsCount =100_000                         #varible to test for the number of operations, current value is so testing can be done quickly
    opsCount = []                                       #varible to hold number of operations complated in a 1 second
    durationCount = []                                  #varible to hold how long it takes each iteration of the operation test
    
    
    for _ in range(3):                               #running the test three times
            if(testType == "setNumTime"):                   #checking testType varible, either setNumTime or setNumOps - 
                numOps = 0                                  #initial value of number of operations completed
                startTime = time.perf_counter()             #getting the start time using performance counter for ms 
        
                while time.perf_counter()-startTime <1:     #running a loop for 1 second and getting the number of operatiosn completed.
                    eval(operation)                         #the provided operation needs to be evaluated 
                    numOps+=1                               #tracking number of operations complated
        
                opsCount.append(numOps)                     #adding the number of operations to list to use for later calculations 
                
            else:                                           #if the testType is other thant setNumTime 
                startTime = time.perf_counter()             #recording start time 
                for _ in range(setOpsCount):                #running loop based on the set number of operations
                    eval(operation)                         #evaluating the operation
                endTime =  time.perf_counter()              #recording the time after all operations are completed
                duration = endTime-startTime                #getting the total duration of time 
                opsPerSec = setOpsCount/duration            #divide the total number of operations by the total time to get the time it takes to complete operations per second  
                durationCount.append(opsPerSec)             #add the results to the list 
            
    if(testType == "setNumTime"):                       #based on the test type: send the appropriate list to the function to return the deviation and average 
        deviation,average = getDeviation(opsCount) 
    else:   
        deviation,average = getDeviation(durationCount) 

   
    return threadCount,average, deviation               #returning thread count, average and deviation 


def threadCountUsed(benchType):                         #function to use a particular number of threads
    
    resetGUI()                                       #result the GUI 
    loadingScreen()                                     #load loading screen
    gui.update()
    
    results= []                                         #list to hold results 
    numThreads = [1,2,4,8]                              #list to hold thread count
    
   
    results.extend([("float",) + getCounts(benchType,"2.0+1.0","default")])  #getting base for whatever the computer will do on its own.
    results.extend([("int",) + getCounts(benchType,"2+1","default")])        
    
    with concurrent.futures.ThreadPoolExecutor() as executor:                                                        #getting results based on the number of threads used, using thread pool executor . 
        futuresF = [executor.submit(getCounts,benchType,"2.0+1.0",threadCount) for threadCount in numThreads]        #using a loop to send elements of numThread to executor module to run function based on thread count 
        results.extend((("float",) + future.result()) for future in futuresF)                                        #adding results to the list 
        futuresI = [executor.submit(getCounts,benchType,"2+1",threadCount) for threadCount in numThreads]
        results.extend((("int",) + future.result()) for future in futuresI)
    print( "Completed tasks for set time, results returned to user")                                                 #advise the user on terminal that the operations were completed
    
    createGUI(benchType,results)                                                                                                 #return the results to user

    
def createGUI(type, cpuSpeeds):                                                                                      #function to create a GUI 
                                                                                                                    #creating the gui 
    resetGUI()  
    
    resizeGUI(10,4)
    gui.update()
    #gui.grid_rowconfigure(0,weight=1)
    #gui.grid_columnconfigure(0,weight=1)
    if type =="setNumTime":
        typeHeader = "Using a Set Duration of Time"
    else:
        typeHeader = "Using a Set Amount of Operations"
    gui.title(f"Benchmark Program: CPU Speeds {typeHeader}")                                                       #creating a nested list to hold frames for gui
    frames = [[None for _ in range(4)] for _ in range(len(cpuSpeeds))]
    headerStyle = ttk.Style()                                                                                       #setting the style up for the gui header and body
    headerStyleName = "headerStyle.TLabel"
    headerStyle.configure(headerStyleName, font=("Times New Roman",14,"bold"), background = "lightgrey")
    bodyStyle = ttk.Style()
    bodyStyleName = "body.TLabel"
    bodyStyle.configure(bodyStyleName, font =("Times New Roman", 12))
   
    guiHeaders = [ "Operation Type: ","Number of Threads: ", "Average of Operations per second: ", "Standard Deviation: "] #list of header titles
    for head, headers in enumerate(guiHeaders):                                                         #filling in the header on gui 
        headerFrame = tk.Frame(gui, relief="solid", borderwidth=1, bg="lightgrey")
        headerFrame.grid(row=0,column=head,padx =10, pady=10,sticky ="w")
        label = ttk.Label(headerFrame, text = headers, anchor ='w', style= headerStyleName)
        label.grid(row=0,column= head, padx = 10, pady =10, sticky ='w')
        
    for row, result in enumerate (cpuSpeeds):                                                       #running through the results and filling in the GUI - using enumerate to run through the results list 
        for col, data in enumerate(result):
            dataFrame = tk.Frame(gui,relief="solid",borderwidth = 1)                         #using frames and configuration frames design 
            dataFrame.grid(row= row+1, column = col, padx =10, pady=10)
            frames[row][col] = dataFrame                                                            #adding frames to the list based on location 
             
            if col == 0 and data == "float":                                                        #seeing what type of operations were conducted and filling in the labels accordingly
                labelText = "Float Operations Per Second (FLOPS): "
            elif col == 0 and data == "int":
                labelText = "Integer Operations Per Second (IOPS): "
            else:
                labelText = str(data)
         
            label = ttk.Label(dataFrame,text = labelText, anchor = "w", style = bodyStyleName)      #filling in the labels 
            label.grid(row=row,column = col,sticky ="w")

    ttk.Button(gui,text= "Do Another Test", command = lambda: (resetGUI(), welcomeGUI())).grid(row=len(cpuSpeeds)+1,column = 4, padx =10,pady=10,sticky ="se" )

                                                                              #displaying the GUI

def welcomeGUI():                                                                                 #display welcome GUI - ran into overcomplex coding with other route i was goign to take
    
    gui.title(f"Benchmark Program: Welcome Page ")  
    

    frames = []
    textList = ["Please select the type of test you would like to run to test you CPU: ","Use a set number of operations:","Use a set amount of time:","Close Benchmark Application"]
    welcomeFont = ("Times New Roman",14,"bold")
    
    for i in range(4):
        frame = tk.Frame(gui,relief="solid",borderwidth=2,bg="lightgrey")                       #making the frames for the GUI
        
        frame.grid(row=i,column=0,padx = 0, pady = 20)
        frame.grid_rowconfigure(i,weight=1)
        
        frames.append( frame)

    labelStyle = ttk.Style()
    labelStyle.configure("Welcome.TLabel", background ="lightgrey")

    buttonStyle = ttk.Style()
    buttonStyle.configure("ButtonStyle.TButton",                                                      #ran into an issue with the style for the buttons, still cant figure out why background wont cahnge color 
                          background = "lightgrey", 
                          focuscolor = "blue", 
                          bordercolor= "black",
                          borderwidth = 2)

    buttonStyle.map("ButtonStyle.TButton",                                                          #mapping for change - however it isnt taking effect, need to do more research for better understanding 
                    background = [("pressed","green"),
                                  ("active","green")])
                    
    resizeGUI(4,0)

    ttk.Label(frames[0],text= textList[0],style = "Welcome.TLabel",font = welcomeFont).grid(row=0, column = 0, sticky="ew")
    ttk.Button(frames[1],text = textList[1], style = "ButtonStyle.TButton", command = lambda:threadCountUsed("setNumOps")).grid(row=1,column = 0,  sticky = "ew")
    ttk.Button(frames[2],text = textList[2], style ="ButtonStyle.TButton", command = lambda:threadCountUsed("setNumTime")).grid(row=2,column = 0,  sticky = "ew")
    ttk.Button(frames[3],text = textList[3], style ="ButtonStyle.TButton", command = lambda:gui.destroy()).grid(row=3,column = 0, sticky = "ew")
    
  
def loadingScreen():                                                                                    ##added a loading screen 
    
   
    gui.title("Conducting Test Please Wait")
    loadingText = "The system is currently conducting the test you have requested please wait until the test is completed."
    loadingLabel = ttk.Label(gui, text= loadingText, background="lightgrey")
    loadingLabel.grid(row=0,column=0,sticky="nsew")
    
    
     
def resizeGUI(row,col):
    for i in range(row):
        gui.grid_rowconfigure(row,weight=1)
        
    for j in range(col):
        gui.grid_columnconfigure(col,weight=1)

def resetGUI():
    for items in gui.winfo_children():
        
        items.destroy()
    
if __name__== "__main__":
    
    welcomeGUI()
    gui.mainloop() 

    ##spent most of day messing with different ways to improve the code, trying to add major improvements, did alright, but ran out of time. 


   