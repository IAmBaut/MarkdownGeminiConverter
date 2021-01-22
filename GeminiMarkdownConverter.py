import re
import argparse
import os
import shutil

def md2gmni(string):
    #Any `code` or multiline code is being taken out to be added later, because we do not want the modifications to be done to that content.
    #In their place string delimiters are being added.
    #First a few delimiters are tested to make sure they don't appear natively in the text.
    counter=5000                    #Index of the string delimiter in a list of all existing unicode characters. We start at 5000 because the characters are far less likely to exist in the string.
    escapedCode=[[],[],[]]          #[[``double backticks``],[`single backticks`],[code blocks with spaces/tabs]]
    delimiters=[]                   #holds the string delimiters. Same order as escapedCode.
    while len(delimiters)<3:
        if not (chr(counter) in string):
            delimiters+=[chr(counter)]
        counter+=1
    #Delimiters are chosen at this point.
    code=""
    isCode=False
    intermediateString=""
    regex="(?:[\t]|[ ]{4})(.*)" #This regex matches strings with either 4 tabs or 4 whitespaces at the beginning. If you wanted to accept a mixing of tabs and spaces "(?:[\t ]{4})(.*)" would do that.
    for line in string.splitlines():
        result=re.search(regex,line)
        if bool(result) and not isCode: #bool(results) is true if the regex has a match.
            isCode=True
            code+=result.group()+"\n"
            intermediateString+=delimiters[2]
        elif bool(result) and isCode:
            code+=result.group()+"\n"
        elif not bool(result) and isCode:
            isCode=False
            escapedCode[2]+=[code]
            code=""
            intermediateString+=line+"\n"
        else:
            intermediateString+=line+"\n"
    if isCode==True:
        escapedCode[2]+=[code]
    #At this point the code with tabs or spaces in the beginning is removed and saved in "escapedCode"
    string=intermediateString
    position=0
    while string.find("``",position)!=-1 and string.find("``",position+2)!=-1:  #This while loop finds anything inbetween double backticks
        position=string.find("``",position)
        if string.find("``",position+2)!=-1:
            escapedCode[0]+=[string[position+2:string.find("``",position+2)]]
            string=string[:position]+delimiters[0]+string[string.find("``",position+2)+2:]
    position=0
    while string.find("`",position)!=-1 and string.find("`",position+1)!=-1:  #This while loop finds anything inbetween single backticks
        position=string.find("`",position)
        if string.find("`",position+1)!=-1:
            escapedCode[1]+=[string[position+1:string.find("`",position+1)]]
            string=string[:position]+delimiters[1]+string[string.find("`",position+1)+1:]
    content=string.splitlines()
    #All code is now removed from the string and saved in "escapedCode".
    paragraphbuffer=""      #Holds the data of a paragraph inside.
    returnstring=""         #The string that gets returned at the end.
    currentline=""          #The line that is currently being processed.
    previousline=""         #The line that was previously being processed. Needed for titles.
    isQuote=False           #Boolean that remembers if currently a quote paragraph is being processed.
    #First pass for structural stuff - paragraphs & titles are being generated.
    for i in content:
        #removing spaces at the beginning and end of lines
        if len(i)>0:
            while i[len(i)-1]==" ":
                 i=i[:len(i)-1]
            while i[0]==" ":
                 i=i[1:]
        previousline=currentline
        currentline=i
        if not isQuote:
            if len(i)>0:
                if i[0]=="#":           #Checks for a "traditional" title
                    returnstring+=i+"\n"
                elif len(i)>=2 and (i[0:2] in ["* ","+ ","- "]):    #Checks for unordered lists
                    returnstring+="* "+i[2:]+"\n"
                elif bool(re.search(r"^(\d+\.\s.*)",i)):            #Checks for ordered lists
                    returnstring+="* "+i[re.search(r"^(\d+\.\s)",i).span()[1]:]+"\n"
                elif i[0] == ">":                                   #Checks for quotes
                    while i[0]==">":
                        i=i[1:]
                    isQuote=True        #Boolean to keep track of if we are currently processing a quote.
                    if len(paragraphbuffer)>0:
                        returnstring+=paragraphbuffer+"\n"
                        paragraphbuffer=""
                    if i[len(i)-1]!=" ":
                        paragraphbuffer+=i+" "
                    else:
                        paragraphbuffer+=i
                elif (i==(len(i)*"=")): #Checks for two-line titles
                    title="#"+previousline
                    if (len(paragraphbuffer)>len(title)):
                        paragraphbuffer=paragraphbuffer[:len(paragraphbuffer)-len(title)+1]#The +1 comes from the # we added to the title before.
                        returnstring+=paragraphbuffer+"\n"
                        returnstring+=title+"\n"
                        paragraphbuffer=""
                    else:
                        returnstring+=title+"\n"
                        paragraphbuffer=""
                elif previousline!="" and (i==(len(i)*"-")):
                    title="##"+previousline
                    if (len(paragraphbuffer)>len(title)):
                        paragraphbuffer=paragraphbuffer[:len(paragraphbuffer)-len(title)+1]
                        returnstring+=paragraphbuffer+"\n"
                        returnstring+=title+"\n"
                        paragraphbuffer=""
                    else:
                        returnstring+=title+"\n"
                        paragraphbuffer=""
                elif previousline=="" and (i==(len(i)*"-")):
                    currentline=""
                elif not (previousline=="" and len(i)>=3 and (i==(len(i)*"-"))): #Writes line to paragraphbuffer UNLESS it is a horizontal rule
                    if i[len(i)-1]!=" ":
                        paragraphbuffer+=i+" "
                    else:
                        paragraphbuffer+=i
            else:
                if len(paragraphbuffer)>0:
                    returnstring+=paragraphbuffer+"\n"
                paragraphbuffer=""
        else: # isQuote==True
            if len(i)==0:
                returnstring+=">"+paragraphbuffer+"\n"
                paragraphbuffer=""
                isQuote=False
            else:
                if i[0]==">":
                    while len(i)>0 and i[0]==">":
                        i=i[1:]
                    if len(i)>0 and i[len(i)-1]!=" ":
                        paragraphbuffer+=i+" "
                    else:
                        paragraphbuffer+=i
                elif len(i)>=2 and (i[0:2] in ["* ","+ ","- "]): #Unordered list.
                    returnstring+=">"+paragraphbuffer+"\n"
                    paragraphbuffer=""
                    isQuote=False
                    returnstring+="* "+i[2:]+"\n"
                elif bool(re.search(r"^(\d+\.\s.*)",i)): #Ordered list.
                    returnstring+=">"+paragraphbuffer+"\n"
                    paragraphbuffer=""
                    isQuote=False
                    returnstring+="* "+i[re.search(r"^(\d+\.\s)",i).span()[1]:]
                elif i==(len(i)*"-"):   #Horizontal lines do not get added.
                    returnstring+=">"+paragraphbuffer
                    paragraphbuffer=""
                    isQuote=False
                else:
                    if i[len(i)-1]!=" ":
                        paragraphbuffer+=i+" "
                    else:
                        paragraphbuffer+=i
    returnstring+=paragraphbuffer
    #At this point returnstring has correct paragraphs, quotes, titles and any horizontal lines are removed but any inline markdown is still there.
    #In markdown you can link images by using "[![name](image location)](link adress)". This code doesn't handle these nested structures well, so the link is removed and the image is left for further processing.
    regex="\[(\!\[.+?\]\(.+?\))\]\(.+?\)"
    while bool(re.search(regex,returnstring)):
        position=re.search(regex,returnstring).span()
        content=re.search(regex,returnstring).groups()[0]
        returnstring=returnstring[:position[0]]+content+returnstring[position[1]:]
    #Nested imagelinks are turned into images at this point.
    content=returnstring.splitlines()
    if content[0]=="":
        content=content[1:]
    newReturnString=""
    currentLine=""
    for i in content:
        currentLine=i
        regex="\[(.+)\]\(\s*([^ ]+)\s*(?:\s\"(.+)\")?\s*\)" #This regex matches markdown links. It also matches images, because the syntax is almost the same. #\!??\[([^\[\]]*?)\]\(\s*([^ ]+)\s*(?:\s\"(.+)\")?\s*\)
        if bool(re.search(regex,currentLine)):
            position=re.search(regex,currentLine).span()#returns (startOfMatch,endOfMatch).
            content=re.search(regex,currentLine).groups()#returns the groups of the link (link,name,title). If no title is found the third entry is None.
            if currentLine[position[0]-1]=="!":
                currentLine=currentLine[:position[0]-1]+currentLine[position[0]:]#Cuts off the ! at the beggining of a image, since images are handled like links.
            if position[0]==0 and position[1]==len(i):#In the case that there is only a link in the paragraph, we just replace the link with correct syntax.
                currentLine="ä=> "+content[1]+" "+content[0]+"\n"
            else: #if there is more than the link in the line, we need to add newlines for the link.
                while bool(re.search(regex,currentLine)): #matches markdown links.
                    position=re.search(regex,currentLine).span()
                    content=re.search(regex,currentLine).groups()
                    if currentLine[position[0]-1]=="!":
                        currentLine=currentLine[:position[0]-1]+currentLine[position[0]:]#Removes ! at beginning of images.
                    if len(currentLine[position[1]:])>1 and currentLine[position[1]:][0]==" ":
                        currentLine=currentLine[:position[0]]+"\n"+"=> "+content[1]+" "+content[0]+"\n"+currentLine[position[1]+1:] #Cuts off space at beginning of line after the link if there is one.
                    else:
                        currentLine=currentLine[:position[0]]+"\n"+"=> "+content[1]+" "+content[0]+"\n"+currentLine[position[1]:]
        #At this point all links and images are replaced.
        regex="\*{x}(.+)\*{x}"#This regex matches any content that is emphasized (x can be 3,2 or 1).
        for j in range(3,0,-1):
            regex="\*{"+str(j)+"}(.+)\*{"+str(j)+"}"
            if bool(re.search(regex,currentLine)):
                while bool(re.search(regex,currentLine)):
                    position=re.search(regex,currentLine).span()
                    content=re.search(regex,currentLine).groups()
                    currentLine=currentLine[:position[0]]+content[0]+currentLine[position[1]:]
            regex="\_{"+str(j)+"}(.+)\_{"+str(j)+"}"
            if bool(re.search(regex,currentLine)):
                while bool(re.search(regex,currentLine)):
                    position=re.search(regex,currentLine).span()
                    content=re.search(regex,currentLine).groups()
                    currentLine=currentLine[:position[0]]+content[0]+currentLine[position[1]:]
        #At this point all forms of Emphasis are removed.
        newReturnString+=currentLine+"\n"
    string=""
    #Putting back escaped code.
    for i in newReturnString:
        isDelimiter=False
        for j in range(3):
            if i==delimiters[j]:
                isDelimiter=True
                string+="\n```\n"+escapedCode[j][0]+"\n```\n"
                escapedCode[j]=escapedCode[j][1:]
        if not isDelimiter:
            string+=i

    """
    This is somewhat of a workaround, and wouldn't be needed if there weren't some bugs in this function.
    Some lines with empty spaces or empty lines remain in the code and can't easily be fixed
    without restructuring the code substantially due to how I handled the insertion of code.
    """
    finalString=""
    for line in string.splitlines():
        if line!="" and line!=" ":
            if line[len(line)-1]==" ":
                finalString+=line[:len(line)-1]+"\n"
            else:
                finalString+=line+"\n"
    if finalString[len(finalString)-1]=="\n":
        return finalString[:len(finalString)-1]
    else:
        return finalString


def gmni2md(string):
    isCode=False
    code=""
    returnString=""
    regex="" #Regex to match links
    inList=False
    unorderedList=""
    for line in string.splitlines():
        if len(line)>0:
            if line[:3]=="```" and not isCode:
                isCode=True
            elif line[:3]=="```" and isCode:
                returnString+=code+"\n"*2
                code=""
                isCode=False
            elif line[:3]!="```" and isCode:
                code+="\t"+line+"\n"
            else:
                #This is for all lines that are not code.
                regex="\=\>\s*?(\S+)(?:[\t\ ])(.+)?"
                result=re.search(regex,line)
                if result!=None:
                    if (result.span()[0]==0) and (result.groups()[1]==None):
                        returnString+="<"+result.groups()[0]+">"+"\n"*2
                    elif (result.span()[0]==0) and (result.groups()[1]!=None):
                        if result.groups()[1][0]==" ":
                            returnString+="["+result.groups()[1][1:]+"]"+"("+result.groups()[0]+")"+"\n"*2
                        else:
                            returnString+="["+result.groups()[1]+"]"+"("+result.groups()[0]+")"+"\n"*2
                    #Links are replaced now
                else:
                    regex="(\#+)(\ )?(.*)"#Matches headings
                    if bool(re.search(regex,line)):
                        result=re.search(regex,line)
                        if result.groups()[1]==None:
                            returnString+=result.groups()[0]+" "+result.groups()[2]+"\n"*2
                        else:
                            returnString+=result.groups()[0]+result.groups()[2]+"\n"*2
                        #Headings are replaced now
                    else:
                        if line[0]=="*" and not inList:
                            inList=True
                            if len(line)>1 and line[1]==" ":
                                unorderedList+=line+"\n"
                            elif len(line)>1 and line[1]!=" ":
                                unorderedList+="* "+line[1:]+"\n"
                            else:
                                unorderedList+="* \n"
                        elif line[0]=="*" and inList:
                            if len(line)>1 and line[1]==" ":
                                unorderedList+=line+"\n"
                            elif len(line)>1 and line[1]!=" ":
                                unorderedList+="* "+line[1:]+"\n"
                            else:
                                unorderedList+="* \n"
                        elif line[0]!="*" and inList:
                            inList=False
                            returnString+=unorderedList+"\n\n"
                            unorderedList=""
                        elif line[0]!="*" and not inList:
                            returnString+=line+"\n\n"
    return returnString

# Get all files in a folder and its subfolders as one list.
def getListOfFiles(pathstr):
    files=[]
    for entry in os.listdir(pathstr):
        completePath = os.path.join(pathstr, entry)
        if os.path.isdir(completePath):
            files+=getListOfFiles(completePath)
        else:
            files.append(completePath)
    return files

# Handle the CLI
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert files or entire folders between gemini and markdown.")
    parser.add_argument("-m",nargs=1,help="Specify a markdown file or folder.",dest="markdown")
    parser.add_argument("-g",nargs=1,help="Specify a gemini file or folder.",dest="gemini")
    parser.add_argument("-o",nargs=1,help="(Optional) Specify a output file or folder.",dest="output")
    args=parser.parse_args()

    if args.markdown and args.gemini:
        print("Error. Please use *either* gemini or markdown mode.")
    else:
        if args.markdown:
            if (len(args.markdown[0])>3 and args.markdown[0][-3:]==".md"):
                with open(args.markdown[0],"r") as inf:
                    if args.output:
                        with open(args.output[0],"w") as outf:
                            outf.write(md2gmni(inf.read()))
                    else:
                        with open("output.md","w") as outf:
                            outf.write(md2gmni(inf.read()))
            else:
                try:
                    if args.output:
                        newpath=os.path.join(args.output[0],args.markdown[0])
                        shutil.copytree(args.markdown[0],newpath)
                    else:
                        newpath=args.markdown[0]
                    for i in getListOfFiles(newpath):
                        if len(i)>3 and i[-3:]==".md":
                            with open(i,"r+") as infile:
                                inf=infile.read()
                                infile.seek(0)
                                infile.write(md2gmni(inf))
                                infile.truncate()
                except FileExistsError:
                    print("Error. The Folder already Exists. Choose another folder or delete the old folder.")
        elif args.gemini:
            if (len(args.gemini[0])>5 and args.gemini[0][-5:]==".gmni"):
                with open(args.gemini[0],"r") as inf:
                    if args.output:
                        with open(args.output[0],"w") as outf:
                            outf.write(gmni2md(inf.read()))
                    else:
                        with open("output.gmni","w") as outf:
                            outf.write(gmni2md(inf.read()))
            else:
                try:
                    if args.output:
                        newpath=os.path.join(args.output[0],args.gemini[0])
                        shutil.copytree(args.gemini[0],newpath)
                    else:
                        newpath=args.gemini[0]
                    for i in getListOfFiles(newpath):
                        if len(i)>5 and i[-5:]==".gmni":
                            with open(i,"r+") as infile:
                                inf=infile.read()
                                infile.seek(0)
                                infile.write(gmni2md(inf))
                                infile.truncate()
                except FileExistsError:
                    print("Error. The Folder already Exists. Choose another folder or delete the old folder.")
