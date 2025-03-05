import itkdb
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import requests
import csv
from io import StringIO

__version__ = "1.3.1"

# Model for the input of parameters
class SpecDataInput(BaseModel):
    accessCode1: str = Field(default=None, examples=["my_access_code1"])
    accessCode2: str = Field(default=None, examples=["my_access_code2"])
    project: str = Field(default=None, examples=["P"])
    componentType: str = Field(default=None, examples=["PCB"])
    testType: str = Field(default=None, examples=["METROLOGY"])
    stage: str = Field(default=None, examples=["PCB_RECEPTION"])
    parameter: Optional[str] = Field(default=None, examples=["BOW1"])

# Model for the output of parameters
class SpecDataOutput(BaseModel):
    project: Optional[str] = None
    componentType: Optional[str] = None
    testType: Optional[str] = None
    stage: Optional[str] = None
    parameter: List[str] = None
    specList: Dict[str, Dict[str, Any]] = None

#################
### FUNCTIONS ###
#################

def help_api():
    return {
        "message": "Welcome to itk-spec",
        "endpoints": {
            "/spec": {
                "method": "GET",
                "description": "Get specification for a single parameter",
                "parameters": {
                    "project": "Project name",
                    "componentType": "Component type",
                    "testType": "Test type",
                    "stage": "Stage",
                    "parameter": "Parameter"
                }
            },
            "/speclist": {
                "method": "GET",
                "description": "Get specifications for multiple parameters",
                "parameters": {
                    "project": "Project name",
                    "componentType": "Component type",
                    "testType": "Test type",
                    "stage": "Stage",
                }
            },
            "/modules": {
                "method": "GET",
                "description": "Get all modules"
            },
            "/modules/{module_id}": {
                "method": "GET",
                "description": "Get a specific module by ID"
            }
        }
    }

def input(kwargs=None):
    if kwargs is None:
        print("No input data provided. please call this function with a dictionary of parameters. Example:")
        print("{'accessCode1':'your_access_code1', 'accessCode2':'your_access_code2', 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'}")
    else:
        input_data = SpecDataInput(
            accessCode1=kwargs["accessCode1"],
            accessCode2=kwargs["accessCode2"],
            project=kwargs["project"],
            componentType=kwargs["componentType"],
            testType=kwargs["testType"],
            stage=kwargs["stage"],
            parameter=kwargs["parameter"]
        )
        return input_data

def read_json(path):
    print("searching json file...")
    with open(path, 'r') as f:
        data = json.load(f)
    print(f"JSON data: {data}")
    return data

def authenticate_user(accessCode1: str, accessCode2: str):
    user = itkdb.core.User(access_code1=accessCode1, access_code2=accessCode2)
    try:
        user.authenticate()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Authentication failed")
    return user
'''
def retrieve_spec(kwargs=None, path=None):
    print("kwargs:" + str(type(kwargs)))
    print("path:" + str(type(path)))
    if type(kwargs) is dict:
        kwargs = input(kwargs)
        kwargs_dict = kwargs.model_dump()
        print(f"kwargs_dict: {kwargs_dict}")
        authenticate_user(kwargs_dict["accessCode1"], kwargs_dict["accessCode2"])
        query = getSpec(**kwargs_dict)
        print(f"Query result: {query}")
        output = SpecDataOutput(
            project=kwargs_dict["project"],
            componentType=kwargs_dict["componentType"],
            testType=kwargs_dict["testType"],
            stage=kwargs_dict["stage"],
            parameter=[query["parameter"]],
            specList={query["parameter"]: query["spec"]}
        )
        print(f"Output: {output}")
        return output
    elif type(path) is str:
        data = read_json(path)
        authenticate_user(data["accessCode1"], data["accessCode2"])
        query = getSpec(**data)
        print(f"Query result: {query}")
        output = SpecDataOutput(
            project=data["project"],
            componentType=data["componentType"],
            testType=data["testType"],
            stage=data["stage"],
            parameter=[query["parameter"]],
            specList={query["parameter"]: query["spec"]}
        )
        print(f"Output: {output}")
        return output

def retrieve_spec_list(kwargs=None, path=None):
    if type(kwargs) is dict:
        kwargs = input(kwargs)
        kwargs_dict = kwargs.model_dump()
        print(f"kwargs_dict: {kwargs_dict}")
        authenticate_user(kwargs_dict["accessCode1"], kwargs_dict["accessCode2"])
        query = getSpecList(**kwargs_dict)
        print(f"Query result: {query}")
        output = SpecDataOutput(
            project=kwargs_dict["project"],
            componentType=kwargs_dict["componentType"],
            testType=kwargs_dict["testType"],
            stage=kwargs_dict["stage"],
            parameter=query["parameter"],
            specList={x: y | {"associatedParam": []} for x, y in zip(query["parameter"], query["spec"])}
        )
        print(f"Output: {output}")
        return output
    elif type(path) is str:
        data = read_json(path)
        authenticate_user(data["accessCode1"], data["accessCode2"])
        query = getSpecList(**data)
        print(f"Query result: {query}")
        output = SpecDataOutput(
            project=data["project"],
            componentType=data["componentType"],
            testType=data["testType"],
            stage=data["stage"],
            parameter=query["parameter"],
            specList={x: y | {"associatedParam": []} for x, y in zip(query["parameter"], query["spec"])}
        )
        print(f"Output: {output}")
        return output
'''

def retrieve_spec(data):
    url = "https://key-version-tester.app.cern.ch/spec"
    response = requests.post(url, json=data)
    print(response.json())

def retrieve_spec_list(data):
    url = "https://key-version-tester.app.cern.ch/speclist"
    response = requests.post(url, json=data)
    print(response.json())

def help_okd():
    url = "https://key-version-tester.app.cern.ch/help"
    response = requests.get(url)
    print(response.text)

def health_check():
    url = "https://key-version-tester.app.cern.ch/health"
    response = requests.get(url)
    print(response.text)

def help():
    help_text = """These are the available Python functions:
    1. retrieve_spec - Get specification for a single parameter
    2. retrieve_spec_list - Get specifications for multiple parameters
    3. help_okd - Understand the available endpoints
    4. health_check - Check if the server is running
    5. Exit
    """
    print(help_text)
    while True:
        choice = input("Enter the number of the function you want to learn more about (or type 'exit' to quit): ").strip().lower()
        if choice in ["5", "exit"]:
            print("Exiting help menu.")
            break
        details = {
            "1": "retrieve_spec: Fetches the specification for a single parameter based on the provided details. \nExample:{'accessCode1':'your_access_code1', 'accessCode2':'your_access_code2', 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'}",
            "2": "retrieve_spec_list: Fetches specifications for multiple parameters at once. \nExample:{'accessCode1':'your_access_code1', 'accessCode2':'your_access_code2', 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION'}",
            "3": "help_okd: Provides information about the available API endpoints in the OKD environment on a dictionary format.",
            "4": "health_check: Checks if the server is running and returns a status response. If the server is connected, the response will be 'ok'.",
        }
        print(details.get(choice, "Invalid selection. Please enter a number from 1 to 4."))

def get_from_EOS(filename):
    url = f'https://eddossan.web.cern.ch/itk-specs/{filename}'
    reqs = requests.get(url)
    if reqs.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return []
    csv_content = reqs.text
    print(f"Fetched content from {url}:\n{csv_content[:500]}...")

    # Parse the CSV content
    data = []
    csv_reader = csv.reader(StringIO(csv_content))
    headers = ["project", "componentType", "testType", "stage", "parameter", "spec"]
    for row in csv_reader:
        if row:
            row_data = {headers[i]: row[i] for i in range(len(headers))}
            if row_data["spec"]:
                try:
                    row_data["spec"] = json.loads(row_data["spec"].replace("'", "\""))  # Convert spec string to dictionary
                except json.JSONDecodeError:
                    print(f"Failed to decode spec: {row_data['spec']}")
                    row_data["spec"] = {}
            else:
                row_data["spec"] = {}
            data.append(row_data)

    print(f"Data: {data}")
    return data

def query_spec_list(data, parameter):
    # Filter the data to find the entry with the specified parameter
    for entry in data:
        if entry["parameter"] == parameter:
            return entry
    
    return None
# Example call to get_from_EOS function
#data_output = get_from_EOS('P_PCB.csv')
#retrieve_spec({'accessCode1':os.environ['ac1'], 'accessCode2':os.environ['ac2'], 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'})
#user = itkdb.core.User(access_code1= os.environ['ac1'], access_code2=os.environ['ac2'])
#user.authenticate()
#help_okd()
#speclist_input_okd({'accessCode1':os.environ['ac1'], 'accessCode2':os.environ['ac2'], 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'})
#spec_input_okd({'accessCode1':os.environ['ac1'], 'accessCode2':os.environ['ac2'], 'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'})