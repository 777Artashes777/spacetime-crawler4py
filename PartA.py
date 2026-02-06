import sys
import re
from pathlib import Path

# def tokenize(textFilePath: str)->list[str]:
#     regex = r"[a-zA-Z0-9]+"
#     text = []
#             #Check if the file exists and is a text file
#     if(Path(textFilePath).is_file() and Path(textFilePath).suffix == '.txt'):
#                 #Read
#         with open(textFilePath, 'r', encoding='utf-8', errors="ignore") as file:
#             while True:
#                 char = file.read(1)
#                 if(char != ''): 
#                     if(char >='A' and char <='Z'): # to handle uppercase letters only
#                         char = char.lower()
#                     else: 
#                         pass
                    
#                     text.append(char)
#                 else:
#                     break
                
#                         #split into tokens
#         token = ''.join(text)
#         return re.findall(regex, token)

#     elif(Path(textFilePath).suffix != '.txt'):
#         print(f"'{textFilePath}' is not a text file.")
#         return []
#     else:
#         print(f"'{textFilePath}' is not a valid file.")
#         return []
    
def tokenize(textFilePath: str)->list[str]: #Overall, O(N), where N is the numver of characters in the file
    regex = r"[a-zA-Z0-9]+"
    tokens = []
    #Check if the file exists
    if(Path(textFilePath).is_file()): #O(1)
        #Ignore any exception it throws in the middle of process
        with open(textFilePath, 'r', encoding='utf-8', errors="ignore") as file:  #O(N), where N is the number of characters
             #Instead of storing everything, just read the file and store only tokens
             for line in file: #In total O(N), where N is the number of characters
                filtered = re.findall(regex, line.lower()) #O(R), number of characters on each line
                tokens += filtered
        return tokens
    
    else:
        print(f"'{textFilePath}' is not a valid file.")
        return []
        
def computeWordFrequencies(words: list[str])->dict[str, int]: #Overall, O(M), where M is the number tokens
    tokenFreq = {}
    #If word is not in a dict, add it as a key and initialize its value
    #If it is in a dict, just increase the frequency
    for word in words: #O(M), where M is the number tokens
        if(word in tokenFreq):
            tokenFreq[word] += 1
        else:
            tokenFreq[word] = 1
    return tokenFreq #O(1)
    
    
def printNew(tokenFrequencies: dict[str, int]): #Overall, O(UlogU), where U is the number of unique tokens
    
    #Sort in decreasing order based on values (frequencies)
    sortedDict = sorted(tokenFrequencies.items(), key = lambda item: item[1], reverse=True) #O(UlogU), where U is the number of unique tokens
    for token, freq in sortedDict: #O(U), where U is the number of unique tokens
        print(f"{token} {freq}")


def main(): #Overall O(M+N+UlogU)
        #Check if file is provided as command line argument
    if(len(sys.argv) == 1): #O(1) 
        print("No file path provided.") #O(1)
        #Ensure that only one file is provided
    elif(len(sys.argv) > 2): #O(1)
        print("Too many arguments provided.") #O(1)
    else:
   
        tokens = tokenize(sys.argv[1]) #O(N), where N is the number of characters in the file.
        map = computeWordFrequencies(tokens) #O(M), where M is the number of tokens
        printNew(map) #O(UlogU), where U is the number of unique tokens

if __name__ == "__main__":
    main()