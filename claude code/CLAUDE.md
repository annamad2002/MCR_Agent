## This is a repo for agentic design of molecules that inhibit MCR. Important files are: 
- code/MCR_Tools.py contains the functions required to test the compounds properties. 
- prompts.md lists the prompts used during the iterative workflow.
- The folders with a number as the name contain the relevant outputs for each prompt with the same number. This contains the chat logs, and the docking files returned. 
 * the chat logs named e.g. '13 - gemma' means that the file is from prompt 13, and that gemma was the model used. the same order is used for the docking results.  

## Next steps for you to take:
- Create and excecute code that goes through every chat log to collate every SMILES, binding affinity, model used, prompt used, and any other properties listed into a master file. Ensure there are no duplicate SMILES. Make this as a CSV that can be read in as a dataframe.