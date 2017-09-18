import requests, json, csv, secrets

#This is the final step in a process to update agent records with remediated contact information. 
#This script authenticates, opens a csv, and posts agent records back to ArchvesSpace based on the contents of that CSV.

# import secrets
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

# authenticate
auth = requests.post(baseURL + "/users/"+user+"/login?password="+password).json()
session = auth["session"]
headers = {"X-ArchivesSpace-Session":session}

# Field names
agent_contacts = "agent_contacts"
names = "names"

# test for successful connection
def test_connection():
    try:
        requests.get(baseURL)
        print "Connected!"
        return True

    except requests.exceptions.ConnectionError:
        print "Connection error. Please confirm ArchivesSpace is running.  Trying again in 10 seconds."

is_connected = test_connection()

while not is_connected:
    time.sleep(10)
    is_connected = test_connection()

updated_agents = "infilepost.csv"

#opens and iterates through spreadsheet
with open(updated_agents,"rb") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
    #define variables to go into json record

        # Get agent id from CSV
        agent_uri = row[0]
        #print(agent_uri)
        # Get authority ID from CSV
        authority_id = row[1]
        # Get contact name from csv, account for presence of class year
        lastname = row[2]
        firstname = row[3]
        classyear = row[4]
        if not classyear:
            contactname = firstname + " " + lastname
        else:
            contactname = firstname + " " + lastname + " '" + classyear
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

        # Get the agent"s ASpace URI
        #agent_uri = baseURL + agent_uri

        #names = requests.get(agent_uri,headers=headers).json()

        # Update Agent Names
        names = {
            "source": "local_inmagic-people",
            "authority_id": ("people_%s" % authority_id),
            "primary_name": lastname,
            "rest_of_name": firstname,
            'name_order':'inverted',
            'sort_name_auto_generate':True
        }

        # Update Agent Contacts 
        agent_contacts = {
         "name": contactname,
         "address_1": organization, 
         "address_2": address1, 
         "address_3": address2, 
         "city": city, 
         "region": state, 
         "post_code": postcode, 
         "email": email,
         "note": notes,
         "telephones": []
        }

        if homephone: 
            agent_contacts["telephones"].append({"number_type": "home","number": homephone})
        if workphone: 
            agent_contacts["telephones"].append({"number_type": "business","number": workphone})
        if cellphone: 
            agent_contacts["telephones"].append({"number_type": "cell","number": cellphone})

        post_data = {"names": [names], "agent_contacts": [agent_contacts]}
        # Wrapping the POST in a try so a failed POST request does not kill the entire update 
        try:    
            print(baseURL + agent_uri)
            print(headers)
            print(json.dumps(post_data))
            agent_post = requests.post(baseURL + agent_uri ,headers=headers,data=json.dumps(post_data))
            print(agent_post)

        except Exception as e:
            print("ERROR: Failed to POST updated names for agent: %s" % agent_post)
            print(e)
            if response.status_code != 200:
                print('Failed to get data:', agent_post.status_code)
        
