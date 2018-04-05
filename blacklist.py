import json

class blacklist():

    blacklist = 'blacklist.json'

    def add(self,ip):
        jsonFile = open(self.blacklist, "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        ## Working with buffered content
        data["blacklist"].append(ip)

        ## Save our changes to JSON file
        jsonFile = open(self.blacklist, "w+")
        jsonFile.write(json.dumps(data,indent=4))
        jsonFile.close()

    def remove(self,ip):
        jsonFile = open(self.blacklist, "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        ## Working with buffered content
        try:
            data["blacklist"].remove(ip)
        except:
            print 'IP does not exist on the blacklist'

        ## Save our changes to JSON file
        jsonFile = open(self.blacklist, "w+")
        jsonFile.write(json.dumps(data,indent=4))
        jsonFile.close()
