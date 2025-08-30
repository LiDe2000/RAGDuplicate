# coding=utf-8

import json
import requests

from typing import Union, Generator, Dict, Any


class DifyAPIClient:
    """Dify API Client Implementation
    
    Concrete implementation of the BaseAPIClient for the Dify platform.
    Handles both blocking and streaming responses from Dify workflows.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the API client with connection parameters and validate configuration.
    
        Initializes the API client using the provided configuration dictionary, extracts
        necessary connection parameters, and validates that all required fields are present.
        Upon successful initialization, request headers will be automatically generated.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary containing required API connection
                parameters. Must include the following fields:
                - base_url (str): Base URL for the API service
                - api_key (str): Authentication key for API access
                - user (str): User identifier for the API requests
        
        Raises:
            ValueError: If any required field is missing in the configuration, with an error
                message specifying which field is missing
        
        Note:
            After initialization, the following instance attributes will be available:
            - base_url: API base URL extracted from configuration
            - api_key: API key extracted from configuration
            - user: User identifier extracted from configuration
            - headers: Auto-generated request headers
        """
        # Extract required parameters from config
        self.base_url: str = config.get("base_url", "")
        self.api_key: str = config.get("api_key", "")
        self.user: str = config.get("user", "")
        
        # Validate required parameters
        required_fields = {
            "base_url": self.base_url,
            "api_key": self.api_key,
            "user": self.user
        }

        for field_name, value in required_fields.items():
            if not value:
                raise ValueError(f"{field_name} is required in config but not provided")
            
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for Dify API
        
        Creates the required HTTP headers for authenticating with the Dify API.
        
        Returns:
            Dict[str, str]: Dictionary containing Authorization and Content-Type headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def run_workflow(self, inputs: Dict[str, Any], stream: bool = False):
        """Execute a Dify workflow
        
        Executes a Dify workflow with the provided inputs (Key/value pairs), supporting both blocking and streaming response modes.
        
        Args:
            inputs (Dict[str, Any]): A dictionary containing the input parameters required to execute the workflow
            stream (bool, optional): Whether to use streaming mode. Defaults to False.
            
        Returns:
            Union[str, Generator[str, None, None]]: 
            - When stream=False: Returns a JSON string containing the complete response data
            - When stream=True: Returns a generator that yields JSON strings of response data chunks
            
        Example:
            >>> dify_client = DifyAPIClient(config=config)
            >>> result = dify_client.run_workflow({"content": "image"}, stream=False)
            >>> for chunk in result:
            ...     print(chunk, end='\n', flush=True)
            
        NOTE: 
            For detailed API documentation, visit: 
            https://docs.dify.ai/api-reference/workflow-execution/execute-workflow
        """
        url = f"{self.base_url}/v1/workflows/run"
        payload = {
            "inputs": inputs, # NOTE: inputs is a dictionary of key/value pairs
            "response_mode": "streaming" if stream else "blocking",
            "user": self.user
        }
        
        # workflow response
        response = requests.request("POST", url, json=payload, headers=self.headers)
        if response.status_code == 200:
            # NOTE: streaming response, return text/event-stream format with ChunkWorkflowEvent stream.
            if stream:
                return self._workflow_streaming_process(response)
            # NOTE: blocking response, return application/json format with WorkflowCompletionResponse.
            else:
                return self._workflow_blocking_process(response)
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def _workflow_blocking_process(self, response: requests.Response) -> Union[Dict[str, Any], str]:
        """Process blocking workflow response from Dify API.
        
        Parses the JSON response from a Dify workflow execution in blocking mode
        and returns the parsed data. This method handles the WorkflowCompletionResponse 
        format from the Dify API.
        
        Args:
            response (requests.Response): The raw HTTP response object from the 
                Dify API workflow execution endpoint.
                
        Returns:
            Union[Dict[str, Any], str]: A dictionary containing the parsed JSON
                response data if parsing is successful.
                
        Raises:
            Exception: If JSON parsing fails, raises an exception with details
                about the parsing error and the response text.
                
        Example:
            >>> response = requests.Response()
            >>> result = self._workflow_blocking_process(response)
        """
        try:
            response_full = json.loads(response.text)  # decode JSON response
            
            return response_full  # NOTE: return full outputs
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)} - Response text: {response.text}")
    
    def _workflow_streaming_process(self, response: requests.Response) -> Generator[str, None, None]:
        """Process streaming workflow response from Dify API.
        
        Processes the Server-Sent Events (SSE) stream from a Dify workflow execution 
        in streaming mode. Each event is parsed and yielded as a JSON string.
        
        Args:
            response (requests.Response): The raw HTTP response object containing
                the SSE stream from the Dify API.
                
        Yields:
            str: JSON strings containing the parsed event data or error information.
            
        Note:
            - Each SSE event starts with 'data: ' prefix and ends with '\n\n'
            - Successfully parsed events are returned as JSON strings
            - Parsing errors are caught and returned as error objects in JSON format
        """
        for line in response.iter_lines():
            # Skip empty lines
            if not line:
                continue
                
            try:
                # NOTE: SSE (Server-Sent Events) stream. Each event starts with 'data: ' and ends with '\n\n'.
                # Check if line starts with 'data: ' prefix (SSE format)
                if not line.startswith(b'data: '):
                    continue
                    
                # Extract JSON string by removing 'data: ' prefix
                json_str = line.decode('utf-8')[6:]  # Remove "data: " prefix
                data = json.loads(json_str)  # decode JSON string
                
                # Yield structured data as JSON string
                yield json.dumps(data, ensure_ascii=False)
                
            except json.JSONDecodeError as e:
                # Handle JSON parsing errors
                error_data = {
                    'error': f"Failed to parse JSON: {str(e)}",
                    'raw_line': line.decode('utf-8') if line else None
                }
                yield json.dumps(error_data, ensure_ascii=False)
            except Exception as e:
                # Handle any other unexpected errors
                error_data = {
                    'error': f"Unexpected error processing stream: {str(e)}",
                    'raw_line': line.decode('utf-8') if line else None
                }
                yield json.dumps(error_data, ensure_ascii=False)
