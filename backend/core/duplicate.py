# coding=utf-8

import re
import os
import datetime
from typing import Optional
from tqdm import tqdm

from backend.utils import doc_handler
from backend.config import CONFIG
from backend.dify_wrapper import DifyAPIClient


def duplicate(file_path: str, output_path: Optional[str] = None):
    '''
    Check for duplicate content in a document by comparing sentences against a Dify workflow API
    
    Example:
        >>> duplicate('path/to/file.txt')
        >>> duplicate('path/to/file.txt', 'path/to/output.txt')
    '''
    
    # 1. Read file content
    content = doc_handler.read(file_path)  # return str
    
    # 2. Split the document by commas or periods to create a list of sentences
    sentences = re.split(r'[，。]', str(content))  # Split text by commas or periods using regular expression
    sentences: list = [sentence.strip() for sentence in sentences if sentence.strip()]  # Filter out empty strings
    
    
    record: dict = {}
    # 3. Loop through calling the dify API
    for i in tqdm(range(0, len(sentences)), desc="Processing progress"):
        result = DifyAPIClient(CONFIG.DIFY_CONFIG).run_workflow(inputs={"content": sentences[i]})
        # 4. When the result contains recalled content
        assert isinstance(result, dict)
        data = result.get("data")
        assert isinstance(data, dict)
        result = data.get("outputs", {}).get("result")
        if result and len(result) > 0:
            record[sentences[i]] = []
            for j in range(len(result)):
                # Save the sentence, duplicate content, and score to the dictionary
                record[sentences[i]].append((result[j]["content"], result[j]['metadata']['score']))
    
    # 5. Convert results to markdown format and save to md file
    markdown_content = "# 重复内容检测结果\n\n"
    
    for sentence, duplicates in record.items():
        markdown_content += f"## 原句\n\n{sentence}\n\n"
        markdown_content += "### 重复内容\n\n"
        
        for i, (duplicate_content, score) in enumerate(duplicates):
            markdown_content += f"**重复项 {i+1}** (Similarity: {score})\n\n"
            markdown_content += f"{duplicate_content}\n\n"
        markdown_content += "---\n\n"
    
    # Determine output path - either use provided path or default to input file path with .md extension
    if output_path is None:
        # Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        # Get the directory of the input file
        input_dir = os.path.dirname(file_path)
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Construct new output path: directory + base_name + timestamp + .md
        output_path = os.path.join(input_dir, f"{base_name}_{timestamp}.md")
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    doc_handler.write(markdown_content, output_path)