För att lägga till ett bash script :

1, Tryck windows + r
2, Skriv in : shell:startup
3, Kopiera in ditt script in i mappen.

// används inte i detta projekt för de kräver att man loggar in för att starta.

Vi kör scheduled tasks i windows-

Så här lägger man till en ny task:

1. Scheduled Task in Windows
Open Task Scheduler:

2. Search for Task Scheduler in the Start Menu and open it.
Create a New Task:

3. Click Create Task in the right panel.
General Tab:

4. Give the task a name (e.g., "Start Uvicorn at Startup").
Select Run whether user is logged on or not.
Check the box for Run with highest privileges.
Triggers Tab:

5. Click New....
Choose At startup as the trigger.
Click OK.
Actions Tab:

6. Click New....
Under Action, choose Start a program.
Under Program/script, type the path to cmd.exe (typically C:\Windows\System32\cmd.exe).
In the Add arguments (optional) field, enter the command:
/k uvicorn apiwebb:app --host 0.0.0.0 --port 8001   - byt till den .py fil du vill köra.
Conditions Tab (Optional):

If you want the task to only run when certain conditions are met (like when the computer is on AC power), you can configure these here.
Settings Tab:

Ensure that Allow task to be run on demand is checked.
Save the Task:

Click OK to save the task. You will likely be prompted to enter your user password to confirm.
This setup will ensure that your uvicorn command starts automatically when the computer boots, without requiring a user to log in.


TIPS:
expempel på sökväg.
/k "D: && cd IoTermometer && uvicorn apiwebb:app --host 0.0.0.0 --port 8001"

Location : Är där scriptsen lagras, behövs inte. Finns standard biblotek för det i windows.


