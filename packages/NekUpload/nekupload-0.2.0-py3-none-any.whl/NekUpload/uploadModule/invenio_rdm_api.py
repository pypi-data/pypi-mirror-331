import logging
from typing import Dict,Any,List
import requests
from .custom_exceptions import APIError,ClientError
import os

"""
This file contains python wrapping of API calls for ease of use.
Not using class here as each method should be atomic and stateless, much like REST API.
All inputs stated in the documentation should be provided.
Always return a response, so clients have flexibility to choose how they want to process things.
For now, lets not worry about other error codes
"""

def create_record(url: str, token: str,metadata: Dict[str,Any]=None,custom_fields:Dict[str,Any] = None) -> requests.Response:
    """Create a record draft in InvenioRDM. Not fully implemented with access, files and custom_fields yet.

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        metadata (Dict[str,Any]): Metadata to be uploaded
        custom_fields (Dict[str,Any]): Custom fields metadata for record (v10 and newer)

    Returns:
        requests.Response: Returns a requests.Response object on success (201 status code) 
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """

    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if not _is_valid_metadata(metadata):
        msg = f"Metadata must be a Dict, currently is a {type(metadata)}"
        logging.error(msg)
        raise ClientError(msg)

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    if url.endswith('/'):
        url = url[:-1]
    records_url = url + "/api/records"

    try:
        response = requests.post(records_url, headers=header, json=metadata)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        if response.status_code == 201:
            _log_debug_response("Record created succesfully",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response) 
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def prepare_file_upload(url: str,token: str,record_id: str,file_name_list: List[str]) -> requests.Response:
    """Creates a location in the Invenio database record to store the files. Capable of batch file preparation.

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of record to be prepared for file upload
        file_name_list (List[str[]): List of names of file to be uploaded

    Returns:
        requests.Response: Response for preparing file upload

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)
    
    for file_name in file_name_list:
        if not _is_valid_file_name(file_name):
            msg = f"{file_name} is a path, not a file name"
            logging.error(msg)
            raise ClientError(msg)

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    #convert to JSON array with []
    body = [{"key": file_name} for file_name in file_name_list]
    
    if url.endswith('/'):
        url = url[:-1]
    record_url = url + f"/api/records/{record_id}/draft/files"

    try:
        response = requests.post(record_url,headers=header, json=body)
        response.raise_for_status()

        if response.status_code == 201:
            _log_debug_response("Files prepared for uploads", response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def upload_file(url: str, token: str, record_id: str, file_path: str) -> requests.Response:
    """Upload the specified file to the records location specified in the url

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): User personal access token
        record_id(str): Id of record to be prepared for file upload
        file_path (str): Path of file to be uploaded

    Returns:
        requests.Response: Upload response object
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """

    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if not os.path.isfile(file_path):
        msg = f"File path: {file_path} does not exist or is not a file."
        logging.error(msg)
        raise ClientError(msg)

    #there is an optional size parameter, but we choose to ignore for now
    header = {
        "Content-Type": "application/octet-stream",
        "Authorization": f"Bearer {token}"
    }

    filename = file_path.split('/')[-1]
    if url.endswith('/'):
        url = url[:-1]
    file_upload_url = url + f"/api/records/{record_id}/draft/files/{filename}/content"

    #open in binary mode, requests behaviour is file is streamed for upload, avoiding memory issues
    with open(file_path, "rb") as f:
        try:
            response = requests.put(file_upload_url, headers=header, data=f)
            response.raise_for_status()
            
            if response.status_code == 200:
                _log_debug_response(f"File {file_path} uploaded successfully", response)
                return response
            else:
                err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
                logging.error(err_msg)
                raise APIError(err_msg,response=response)
        except requests.exceptions.RequestException as e:
            err_msg = f"Request Error: {e}"
            logging.error(err_msg)
            raise APIError(err_msg)

def commit_file_upload(url: str, token: str, record_id: str, filename: str) -> requests.Response:
    """Save uploaded file in the specified url location to the repository

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): User personal access token
        record_id(str): Id of record to be prepared for file upload
        filename (str): Name of file to be uploaded

    Returns:
        requests.Response: Commit response object

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)
    
    if '/' in filename:
        msg = f"filename: {filename} is a path, not file"
        logging.error(msg)
        raise ClientError(msg)

    header = {"Authorization": f"Bearer {token}"}
    
    if url.endswith('/'):
        url = url[:-1]
    file_commit_url = url + f"/api/records/{record_id}/draft/files/{filename}/commit"

    try:
        response = requests.post(file_commit_url, headers=header)
        response.raise_for_status()
        
        if response.status_code == 200:
            _log_debug_response(f"File {filename} committed successfully",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)    
    except requests.exceptions.RequestException as e:
            err_msg = f"Request Error: {e}"
            logging.error(err_msg)
            raise APIError(err_msg)

def publish_draft(url: str, token: str, record_id: str) -> requests.Response:
    """Publish the specified draft on InvenioRDM

    Args:
        url (str): url route to draft to be published base_url/api/records/{record_id}/draft/actions/publish
        token (str): User personal access token
        record_id(str): Id of record to be prepared for file upload

    Returns:
        requests.Response: Publish response object

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)
    
    header = {"Authorization": f"Bearer {token}"}
    
    if url.endswith('/'):
        url = url[:-1]
    publish_url = url + f"/api/records/{record_id}/draft/actions/publish"

    try:
        response = requests.post(publish_url, headers=header)
        response.raise_for_status() #raise exception for bad status codes
        
        if response.status_code == 202:
            _log_debug_response(f"Draft published successfully.",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def delete_draft(url: str, token: str, record_id: str) -> requests.Response:
    """Delete a draft record

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of record to be prepared for file upload

    Returns:
        requests.Response: Delete response object

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """

    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if url.endswith('/'):
        url = url[:-1]
    delete_url = url + f"/api/records/{record_id}/draft"

    header = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(delete_url, headers=header)
        response.raise_for_status() #raise exception for bad status codes

        if response.status_code == 204:
            _log_debug_response(f"Draft deleted successfully.",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def get_community(url:str, token: str,community_slug: str) -> requests.Response:
    """Get community specified by the community slug or id

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        community_slug (str): Community url slug or uuid

    Returns:
        requests.Response: Get community response

    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    header = {"Authorization": f"Bearer {token}"}

    if url.endswith('/'):
        url = url[:-1]
    community_url = url + f"/api/communities/{community_slug}"

    try:
        response = requests.get(community_url,headers=header)
        response.raise_for_status()

        if response.status_code == 200:
            _log_debug_response(f"Successfully found community associated with {url}",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def submit_record_to_community(url: str,token: str,community_uuid:str, record_id:str) -> requests.Request:
    """Submit a record to a specified community

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        community_uuid (str): Community UUID
        record_id(str): Id of record to be prepared for file upload

    Returns:
        requests.Request: Community submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if url.endswith('/'):
        url = url[:-1]
    community_url = url + f"/api/records/{record_id}/draft/review"

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
        }

    body =  {
        "receiver" : {
            "community": f"{community_uuid}"
        },
        "type": "community-submission"
    }

    try:
        response = requests.put(community_url,headers=header,json=body)
        response.raise_for_status()

        if response.status_code == 200:
            _log_debug_response(f"Successfully submitted record {record_id} to community {community_uuid}",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def submit_record_for_review(url: str,token: str,record_id: str,payload: Dict[str,str]) -> requests.Response:
    """Once record is submmitted to community, submit it now for review

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of record to be prepared for file upload
        payload(str): Contains content and format
        
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)
    
    if not _is_valid_comment_payload(payload):
        msg = f"Current payload {payload} is invalid. Should contain 'content': str and 'format': 'html'"
        logging.error(msg)
        raise ClientError(msg)
        
    if url.endswith('/'):
        url = url[:-1]
    submit_review_url = url + f"/api/records/{record_id}/draft/actions/submit-review"

    header = {"Authorization": f"Bearer {token}"}
    body = {"payload": payload}

    try: 
        response = requests.post(submit_review_url,headers=header,json=body)
        response.raise_for_status()

        if response.status_code == 202:
            _log_debug_response(f"Record submitted to community for review",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)

def get_record(url: str, token: str, record_id: str) -> requests.Response:
    """Get record associated with record_id

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of desired record
        
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if url.endswith('/'):
        url = url[:-1]
    draft_url = url + f"/api/records/{record_id}/draft"

    header = {"Authorization": f"Bearer {token}"}
    
    try: 
        response = requests.get(draft_url,headers=header)
        response.raise_for_status()

        if response.status_code == 200:
            _log_debug_response(f"Record {record_id} acquired",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)    

def delete_review_request(url:str,token:str,record_id:str) -> requests.Response:
    """Get community review request associated with record_id

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        record_id(str): Id of desired record
        
    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)

    if url.endswith('/'):
        url = url[:-1]
    review_url = url + f"/api/records/{record_id}/draft/review"

    header = {"Authorization": f"Bearer {token}"}

    try: 
        response = requests.delete(review_url,headers=header)
        response.raise_for_status()

        if response.status_code == 204:
            _log_debug_response(f"Record {record_id} acquired",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)   

def cancel_review_request(url:str,token:str,request_id:str,payload: Dict[str,str]) -> requests.Response:
    """Cancel a user-submitted review request. Only request's creator can cancel it

    Args:
        url (str): Base url route to the invenio database, of form http:// or https://
        token (str): Personal access token
        request_id(str): Id of request
        payload(str): Contains content and format

    Returns:
        requests.Response: Record review submission response
    
    Raises:
        APIError: If an error occurs during the API call. 
        ClientError: If an error occurs due to invalid message parameters
    """
    #sanitise incoming data
    if not _is_valid_base_url(url):
        msg = f"url {url} is invalid. Should be of form http://example or https://example"
        logging.error(msg)
        raise ClientError(msg)
    
    if not _is_valid_comment_payload(payload):
        msg = f"Current payload {payload} is invalid. Should contain 'content': str and 'format': 'html'"
        logging.error(msg)
        raise ClientError(msg)
        
    if url.endswith('/'):
        url = url[:-1]
    cancel_request = url + f"/api/requests/{request_id}/actions/cancel"

    header = {"Authorization": f"Bearer {token}"}
    body = {"payload": payload}

    try: 
        response = requests.post(cancel_request,headers=header,json=body)
        response.raise_for_status()

        if response.status_code == 200:
            _log_debug_response(f"Request {request_id} cancelled.",response)
            return response
        else:
            err_msg = f"Unexpected status code: {response.status_code} - {response.text}"
            logging.error(err_msg)
            raise APIError(err_msg,response=response)     
    except requests.exceptions.RequestException as e:
        err_msg = f"Request Error: {e}"
        logging.error(err_msg)
        raise APIError(err_msg)   
    
def _log_debug_response(msg: str, response: requests.Response) -> None:
    """Log a debug statement to logger, with message and response.
    Will take form msg: response. For long responses, they are shortened when logged. 

    Args:
        msg (str): User defined message
        response (requests.Response): Request response 
    """
    try:
        response_data = response.json()
        if isinstance(response_data, dict) and len(response_data) > 10:
            response_data = {k: response_data[k] for k in list(response_data)[:10]}
            response_data['...'] = '...'
        elif isinstance(response_data, list) and len(response_data) > 10:
            response_data = response_data[:10] + ['...']
    except ValueError:
        response_data = response.text[:1000] + '...' if len(response.text) > 1000 else response.text

    logging.debug(f"{msg}: {response_data}")

def _is_valid_metadata(metadata: Dict[str,Any]) -> bool:
    #might want to introduce other checks
    return isinstance(metadata, dict)

def _is_valid_file_name(file_name:str) -> bool:
    """Check if the file name is valid by ensuring it does not contain any '/' characters.

    Args:
        file_name (str): The file name to check.

    Returns:
        bool: True if the file name is valid, False otherwise.
    """
    return '/' not in file_name

def _is_valid_comment_payload(payload: Dict[str,str]) -> bool:
    """Checks whether comment payload has correct format

    Args:
        payload (Dict[str,str]): Payload

    Returns:
        bool: Is valid
    """
    if len(payload) != 2:
        return False
    
    #must have format as html
    try:
        if payload["format"] != "html":
            return False
    except KeyError:
        return False
    
    #must havwe content as string
    try: 
        if not isinstance(payload["content"],str):
            return False
    except KeyError:
        return False
    
    return True

def _is_valid_base_url(url: str) -> bool:
    """Check if the base URL is valid (starts with http:// or https://).

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    return url.startswith("http://") or url.startswith("https://")