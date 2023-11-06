import argparse
import os

import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO

from requests import Session
from typing import Generator, Union, List, Tuple

import urllib3
urllib3.disable_warnings()


def get_paper(session: Session, paper_id: str, fields: str = 'paperId,title', **kwargs) -> dict:
    params = {
        'fields': fields,
        **kwargs,
    }

    with session.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', params=params) as response:
        response.raise_for_status()
        return response.json()


def download_pdf(session: Session, url: str, path: str, user_agent: str = 'requests/2.0.0'):
    # send a user-agent to avoid server error
    s3_client = boto3.client('s3')
    
    headers = {
        'user-agent': user_agent,
    }

    # stream the response to avoid downloading the entire file into memory
    with session.get(url, headers=headers, stream=True, verify=False) as response:
        # check if the request was successful
        response.raise_for_status()

        if response.headers['content-type'] != 'application/pdf':
            raise Exception('The response is not a pdf')
        
        pdf_data = BytesIO()

        for chunk in response.iter_content(chunk_size=8192):
            pdf_data.write(chunk)
        
        pdf_data.seek(0)

        s3_client.upload_fileobj(pdf_data, 'search-engine-bd', path)

        pdf_data.close()

def download_paper(session: Session, paper_id: str, directory: str = 'papers', user_agent: str = 'requests/2.0.0') -> Union[str, None]:
    paper = get_paper(session, paper_id, fields='paperId,isOpenAccess,openAccessPdf')

    if not paper['isOpenAccess']:
        return None

    if paper['openAccessPdf'] is None:
        return None

    paperId: str = paper['paperId']
    pdf_url: str = paper['openAccessPdf']['url']
    pdf_path = os.path.join(directory, f'{paperId}.pdf')

    os.makedirs(directory, exist_ok=True)

    download_pdf(session, pdf_url, pdf_path, user_agent=user_agent)

    return pdf_path


def download_papers_util(paper_ids: List[str], directory: str = 'papers', user_agent: str = 'requests/2.0.0') -> Generator[Tuple[str, Union[str, None, Exception]], None, None]:
    # use a session to reuse the same TCP connection
    with Session() as session:
        for paper_id in paper_ids:
            try:
                yield paper_id, download_paper(session, paper_id, directory=directory, user_agent=user_agent)
            except Exception as e:
                yield paper_id, e


def download_papers_pdf(paper_ids):
    for paper_id, result in download_papers_util(paper_ids, directory="corpus/pdf", user_agent="requests/2.0.0"):
        if isinstance(result, Exception):
            print(f"Failed to download '{paper_id}': {type(result).__name__}: {result}")
        elif result is None:
            print(f"'{paper_id}' is not open access")
        # else:
            # print(f"Downloaded '{paper_id}' to '{result}'")