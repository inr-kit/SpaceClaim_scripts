# Python Script, API Version = V17
import os,time

######## User guide ##########
# run the script inside a project
# it search each component for bodies,
# if any bodies, it group together and save
# to a file with the file name as component name

######## User Input ##########
# please provide the path to save the model
# for example "D:\\Program\\McCad\\"
PathToSave = "D:\\Projects\\IFMIF_DONES\\40_TC_modeling_2020\\decomposed\\PCP"

##############################

def recursive(comp, count):
    "this function recursively seprate the components and parts"
    #recursively save the bodies for all components
    if len(comp.Components)>0:
        for icomp in comp.Components :
           recursive(icomp,count)
    #if bodies, save to the files
    if len(comp.GetBodies())>0:
        sel = Selection.Create(comp.GetBodies())
        result = Copy.ToClipboard(sel)
         #create a new document to save the solid to STEP file
        DocumentHelper.CreateNewDocument() #;time.sleep(0.2)
        result = Paste.FromClipboard()#;time.sleep(0.2)
        #time.sleep(1.0)
        filename = PathToSave + "\\"  + comp.GetName() + ".stp" #+ String(count) + "_"
        counter =1
        while  os.path.exists(filename):
            filename = filename[:-4] + "-"+str(counter)  + ".stp"
            counter += 1
        print filename
        DocumentSave.Execute(filename,ExportOptions.Create() )#;time.sleep(0.2)
        # delete the solid in this document
        Delete.Execute(Selection.SelectAll())#;time.sleep(0.2)
        CloseWindow()#;time.sleep(0.2)
        #time.sleep(1.0)
        count += 1
        # return count


root = GetRootPart()
count =  1 # file indexes
recursive(root,count)