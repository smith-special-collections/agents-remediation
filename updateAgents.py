import requests, json, csv, secrets

#This is the final step in a process to update agent records with remediated contact information. 
#This script authenticates, opens a csv, and posts agent records back to ArchvesSpace based on the contents of that CSV.

# import secrets
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

# authenticate
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Field names
agent_contacts = 'agent_contacts'
names = 'names'

# test for successful connection
def test_connection():
    try:
        requests.get(baseURL)
        print 'Connected!'
        return True

    except requests.exceptions.ConnectionError:
        print 'Connection error. Please confirm ArchivesSpace is running.  Trying again in 10 seconds.'

is_connected = test_connection()

while not is_connected:
    time.sleep(10)
    is_connected = test_connection()

updated_agents = 'infileupdate.csv'

#opens and iterates through spreadsheet
with open(updated_agents,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)
    #define variables to go into json record

        # Get agent id from CSV
        agent_uri = row[0]
        print(agent_uri)
        # Get authority ID from CSV
        authority_id = row[1]
        # Get contact name from csv, account for presence of class year
        lastname = row[2]
        firstname = row[3]
        classyear = row[4]
        if not classyear:
            contactname = firstname + ' ' + lastname
        else:
            contactname = firstname + ' ' + lastname + " '" + classyear
        # Get contact information
        organization = row[5]
        address1 = row[6]
        address2 = row[7]
        city = row[8]
        state = row[9]
        postcode = row[10]
        email = row[11]
        homephone = row[12]
        workphone = row[13]
        cellphone = row[14]
        notes = row[15]

        # Get the agent's ASpace URI
        agent_uri = baseURL + agent_uri

        agent_json = requests.get(agent_uri,headers=headers).json()


        # Update Notes
        updatedNote = {
            
        }

        # Update Agent Names
        updatedName = {
            'source': 'local_inmagic-people',
            'authority_id': ('people_%s' % authority_id)
        }
        if 'names' in agent_json: 
            if (len(agent_json[names]) > 1):
                print("%s name entries in agent record (%s), can't do anything with that shit." % (len(agent_json[names]), agent_uri))
            # Take the only name entry for this record and update values in Source and Authority ID
            else: 
                agent_json[names][0].update(updatedName)
        else: 
            # Throw and error 
            print("No name entry in agent record (%s), can't do anything with it" % agent_uri)

        # Update Agent Contacts 
        updateContact = {
         'name': contactname,
         'address_1': organization, 
         'address_2': address1, 
         'address_3': address2, 
         'city': city, 
         'region': state, 
         'post_code': postcode, 
         'email': email,
         'note': notes,
         'telephones': []
        }

        if homephone: 
            updateContact['telephones'].append({'number_type': 'home',"number": homephone})
        if workphone: 
            updateContact['telephones'].append({'number_type': 'business',"number": workphone})
        if cellphone: 
            updateContact['telephones'].append({'number_type': 'cell',"number": cellphone})

        if (agent_contacts in agent_json and len(agent_json[agent_contacts]) == 1):
            # If there is only one then grab it and update the values
            existingContact = agent_json[agent_contacts][0]
            existingContact.update(updateContact)
            agent_json[agent_contacts] = [existingContact]
        elif((agent_contacts in agent_json and len(agent_json[agent_contacts]) == 0) or (agent_contacts not in agent_json)):
            agent_json[agent_contacts] = [updateContact]
        else: 
            print("%s agent contacts in agent record (%s), don't know what to do" % (len(agent_json[agent_contacts]), agent_uri))


        # Wrapping the POST in a try so a failed POST request does not kill the entire update 
        try:    
            agent_post = requests.post(agent_uri,headers=headers,data=json.dumps(agent_json))
            print("Successfully updated %s" % agent_uri)
        except Exception as e:
            print("ERROR: Failed to POST updated agent_json for agent: %s" % agent_uri)
            print(e)
        
