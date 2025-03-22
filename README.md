# Install requirements:
1. Install python and pip
2. `cd` into project directory
3. Run:
```bash 
pip install -r requirements.txt 
```
# To run API Server
Run:
```bash
python main.py
```
# Endpoints
To use endpoints:
1. Install [Postman](https://www.postman.com/downloads/)
2. Import API Testing collection file `plag-checker-api.postman_collection.json`

Descriptions of endpoints:
1. `get-file-list`: Returns list of files stored on server
2. `store-files`: Uploads files to server
   - add `files` parameter to body of request and attach files to upload 
3. `delete-file`: Deletes file from server
   - add `serial_numbers` parameter to body of request, e.g. `[1, 2, 3]` will delete files with serial numbers 1, 2 and 3 when sorted in alphabetical order
4. `calculate`: Compares files in server and returns HTML report with results
