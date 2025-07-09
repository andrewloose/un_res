"""
jsonformatter.py
Formats the original DGC-SCRES.json file, from the dataset titled
"Resolutions and Decisions of the Security Council" from the United Nations Peace and Security data hub.
https://psdata.un.org/dataset/DGC-SCRES

Goal: clean up votes and tie together relevant sections of votes, add an easy-to-understand Year Integer
instead of UNIX Timestamp, and fix null subject fields
"""
import json
from datetime import datetime

# Load the JSON file
with open('DGC-SCRES.json', 'r') as file:
    data = json.load(file)

# Iterate through each document in the json file and add the year field
for document in data:
    if 'date' in document:
        # take the timestamp and divide by 1000 to get rid of miliseconds
        timestamp = document['date'] / 1000
        # only want year
        year = datetime.utcfromtimestamp(timestamp).year
        # append year to the item
        document['year'] = year

# Iterate through each document and update the subject field
for document in data:
    # if a subject line doesnt exist, make it the top topic
    if 'topics' in document and 'subjects' not in document:
        main_topic = document['topics'][0] if document['topics'] else None
        document['subjects'] = main_topic

# Iterate through each document and modify the structure
for document in data:
    if 'voting_yes' in document:
        voting = {
            'yes': document['voting_yes'],
            'no': document['voting_no'],
            'abstain': document['voting_abstain']
        }

        document['voting'] = voting

        # Remove the original 'voting_yes', 'voting_no', 'voting_abstain' fields if needed
        del document['voting_yes']
        del document['voting_no']
        del document['voting_abstain']

# Iterate through each document and add the voting_yes_percentage field
for document in data:
    if 'voting' in document:
        voting_yes = document['voting'].get('yes', 0)
        voting_no = document['voting'].get('no', 0)
        voting_abstain = document['voting'].get('abstain', 0)

        if voting_yes is not None:
            if voting_yes.lower() == 'adopted unanimously':
                voting_yes_percentage = 100
            else:
                total_votes = int(voting_yes) + float(voting_no) + float(voting_abstain)
                voting_yes_percentage = int((int(voting_yes) / total_votes) * 100)
        else:
            # Handle the case when 'voting_yes' is None
            voting_yes_percentage = 0

        document['voting']['voting_yes_percentage'] = voting_yes_percentage

# Save the modified JSON back to a file
with open('un_res.json', 'w') as modified_file:
    json.dump(data, modified_file, indent=2)
