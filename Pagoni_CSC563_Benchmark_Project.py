#Creator: Brian Pagoni, SCSU CSC-563-01 
#This project is desined to allow user to obtain a benchmark for this system and display the results using a gui.   

#importing the different modules that will be used to assist 



import enum
import time
import tkinter as tk
from tkinter import ttk
import concurrent.futures
import math

                                                                 #some global varibles that are used and some styles that should effect all GUIS
gui = tk.Tk()
gui.config(bg="skyblue",pady=20)   
buttonStyle = ttk.Style()
buttonStyle.configure("ButtonStyle.TButton",                        #ran into an issue with the style for the buttons, still cant figure out why background wont cahnge color 
                        background = "lightgrey",
                        focuscolor = "blue",
                        bordercolor= "black",
                        borderwidth = 2)

buttonStyle.map("ButtonStyle.TButton",                             #Mapping out user interactions for buttons,  
                background = [("pressed","green"),
                                ("active","green"),
                                ("!active","white")])
headerStyle = ttk.Style()                                           #setting the style up for the gui header and body
headerStyleName = "headerStyle.TLabel"
headerStyle.configure(headerStyleName,
    font=("Times New Roman",14,"bold"), background = "lightgrey")

bodyStyle = ttk.Style()
bodyStyleName = "body.TLabel"
bodyStyle.configure(bodyStyleName, font =("Times New Roman", 12))

    
def getDeviation(data):                                                 #ran into issue with statistics given off the wall returns for standard deviation. using a custom deviation function for time being
    
    average  = sum(data)/len(data)                                      #getting the avergae from the data set 
    
    squDif = [(count - average)**2 
              for count in data]                                        #getting the square difference 
    
    avgSqu = sum(squDif)/len(squDif)                                    #getting the average of the squared differences
    deviation = round(math.sqrt(avgSqu),6)                              #calculating the deviation based on above code.
   
    return deviation,average                                            #returning result 

def getCounts( benchType,threadCount, operation):                         #function for getting require results, broken into two options. 
     
    setOpsCount = 100                                              #varible to test for the number of operations, current value is so testing can be done quickly
    opsCount = []                                                       #varible to hold number of operations complated in a 1 second
    durationCount = []                                                  #varible to hold how long it takes each iteration of the operation test
    
    
    for _ in range(3):                                                  #running the test three times
            if(benchType == "setNumTime"):                               #checking testType varible, either setNumTime or setNumOps - 
                numOps = 0                                              #initial value of number of operations completed
                startTime = time.perf_counter()                         #getting the start time using performance counter for ms 
        
                while time.perf_counter()-startTime <1:                 #running a loop for 1 second and getting the number of operatiosn completed.
                    eval(operation)                                     #the provided operation needs to be evaluated 
                    numOps+=1                                           #tracking number of operations complated
        
                opsCount.append(numOps)                                 #adding the number of operations to list to use for later calculations 
                
            else:                                                       #if the testType is other thant setNumTime 
                startTime = time.perf_counter()                         #recording start time 
                for _ in range(setOpsCount):                            #running loop based on the set number of operations
                    eval(operation)                                     #evaluating the operation
                endTime =  time.perf_counter()                          #recording the time after all operations are completed
                duration = endTime-startTime                            #getting the total duration of time 
                opsPerSec = setOpsCount/duration                        #divide the total number of operations by the total time to get the time it takes to complete operations per second  
                durationCount.append(opsPerSec)                         #add the results to the list 
            
    if(benchType == "setNumTime"):                                       #based on the test type: send the appropriate list to the function to return the deviation and average 
        deviation,average = getDeviation(opsCount) 
    else:   
        deviation,average = getDeviation(durationCount) 
    if operation == "2.0+1.0":
        return ["FLOPS", threadCount,average, deviation  ]
    else:
        return ["IOPS", threadCount,average, deviation  ]
                          #returning thread count, average and deviation 


def threadCountUsed(benchType):                                         #function to use a particular number of threads
    
    resetGUI()                                                          #result the GUI 
    loadingScreen()                                                     #load loading screen
    gui.update()
                                                       #list to hold results 
    threadsUsed  = [1,2,4,8]                                              #list to hold thread count
    
    
    defaultFloat= getCounts(benchType,"default","2.0+1.0")       #getting base for whatever the computer will do on its own.
    defaultInt= getCounts(benchType,"default","2+1") 
    
    resultsData = useThreads(benchType,threadsUsed)

    frameData = combinLists(defaultFloat, defaultInt, resultsData)
    
    print( "Completed tasks for set time, results returned to user")    #advise the user on terminal that the operations were completed
    
    resultsGUI(benchType,frameData) 
    

def combinLists(defaultFloat, defaultInt, resultsData):

    frameData = [ ["Operation Type: ","Number of Threads: ",
                    "Average of Operations per second: ",
                   "Standard Deviation: "]]                                               #making the framedata useable in this function and adding in the default tests 
    frameData.append(defaultFloat)
    frameData.append(defaultInt)

    headers = frameData[0]                                                #seperating out the data 
    defaultF = frameData[1]
    defaultI = frameData[2]
    
    for row in resultsData:                                             #adding the results from the calculations 
        frameData.append(row)
        
    data=frameData[3:]                                                    #getting the results seperate for sorting 

    floatOperations = [row for row in data if row[0]=="FLOPS"]          #getting all the operations into their own list          
    intOperations = [row for row in data if row[0]=="IOPS"]
    
    sortedFloatOps = sorted(floatOperations, key=lambda data: (data[0],data[1]))    #sort the results based on the first and second columns 
    sortedIntOps = sorted(intOperations, key=lambda data: (data[0],data[1]))
    
    
    results = [headers]+[defaultF]+sortedFloatOps+[defaultI] + sortedIntOps #combining all the lists together to return

    return results                                                          #returning the results 

def useThreads(benchType,threadCount):

    results= []

    with concurrent.futures.ThreadPoolExecutor() as executor: 
        futuresF = [executor.submit(getCounts,benchType,threadNum,"2.0+1.0") for threadNum in threadCount]
        futuresI = [executor.submit(getCounts,benchType,threadNum,"2+1") for threadNum in threadCount]
        for future in concurrent.futures.as_completed(futuresF):
            results.extend([future.result()])
        for future in concurrent.futures.as_completed(futuresI):
            results.extend([future.result()])
    return results

def resultsGUI(benchType,data):                                         #function to create a GUI 
                                                                      
    resetGUI()                                                          #resetting the GUI 
    resizeGUI(10,4)                                                     #resizing the GUI to fit results
                                                           #forcing GUI to update
    if benchType =="setNumTime":                                             #taking the type of operation and changing the title of GUI 
        typeHeader = "Using a Set Duration of Time"
    else:
        typeHeader = "Using a Set Amount of Operations"
   
    gui.title(f"Benchmark Program: CPU Speeds {typeHeader}")                                                      
    
    setFrames(data)                                                                       #adding a button to run a new test by returning to welcome page 
    ttk.Button(gui,text= "Do Another Test", command = lambda: (resetGUI(), welcomeGUI())).grid(row=len(data),column = 4, padx =10,pady=10,sticky ="se" )

def setFrames(data):
    
    dataGrid = [col for col in data]
    
    
    for rowIndex, rowData in enumerate(data):
       
        for colIndex,colData in enumerate(rowData):
           
           frame = tk.Frame(gui, relief="solid", borderwidth=1, bg="lightgrey")
           frame.grid(row=rowIndex,column=colIndex,padx =10, pady=10,sticky ="w")

           label = ttk.Label(frame, text = colData, anchor ='w', style= headerStyleName)
           label.grid(row=rowIndex,column= colIndex, padx = 10, pady =10, sticky ='w')
          
            
   

def welcomeGUI():                                                       #display welcome GUI - ran into overcomplex coding with other route i was goign to take
    
    gui.title(f"Benchmark Program: Welcome Page ")  
    

    frames = []                                                         #list to hold frames 
                                                                        #list to hold text 
    textList = [
        "Please select the type of test you would like to run to test you CPU: ",
        "Use a set number of operations:","Use a set amount of time:",
        "Close Benchmark Application"]

    welcomeFont = ("Times New Roman",14,"bold")                         #varible to aadjust font for title 
                                                                        #making the frames for the GUI
    for i in range(4):
        frame = tk.Frame(gui,relief="solid",borderwidth=2,bg="lightgrey")

        frame.grid(row=i,column=0,padx = 0, pady = 20)
        frame.grid_rowconfigure(i,weight=1)

        frames.append( frame)

    labelStyle = ttk.Style()
    labelStyle.configure("Welcome.TLabel", background ="lightgrey")

    
                    
    resizeGUI(4,0)                                                      #resize GUI to fit frames for welcome page
                                                                        #adding in label and buttons 
    ttk.Label(frames[0],text= textList[0],style = "Welcome.TLabel",font = welcomeFont)\
        .grid(row=0, column = 0, sticky="ew") 
    ttk.Button(frames[1],text = textList[1], style = "ButtonStyle.TButton",\
       command = lambda:threadCountUsed("setNumOps")).grid(row=1,column = 0,  sticky = "ew")
    ttk.Button(frames[2],text = textList[2], style ="ButtonStyle.TButton", \
        command = lambda:threadCountUsed("setNumTime")).grid(row=2,column = 0,  sticky = "ew")
    ttk.Button(frames[3],text = textList[3], style ="ButtonStyle.TButton",\
       command = lambda:gui.destroy()).grid(row=3,column = 0, sticky = "ew")
    
  
def loadingScreen():                                                    #added a loading screen to advise user that the program is running 
                                                                        #working on adding more functionality to this 
    
    gui.title("Conducting Test Please Wait")
    loadingText = "The system is currently conducting the test you have requested please wait until the test is completed."
    loadingLabel = ttk.Label(gui, text= loadingText, background="lightgrey")
    loadingLabel.grid(row=0,column=0,sticky="nsew")
    
    
     
def resizeGUI(rows,cols):                                                 #function to resize GUI to ensure the frames all fit 
    for i in range(rows):
        gui.grid_rowconfigure(rows,weight=1)
        
    for j in range(cols):
        gui.grid_columnconfigure(cols,weight=1)

def resetGUI():                                                         #function to remove all frames from GUI - Testing purposes and attempts to resolve some issues. 
    for items in gui.winfo_children():
        
        items.destroy()




    
if __name__== "__main__":
    
    welcomeGUI()
    gui.mainloop() 

   


   