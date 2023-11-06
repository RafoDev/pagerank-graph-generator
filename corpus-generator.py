import requests
import json
import PyPDF2
from downloader import download_papers_pdf
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO

max_depth = 1
max_references = 3

papers = []


class Paper:
    global papers

    def __init__(self, pid):
        self.pid = pid
        self.references = []
        self.referenced_papers = []
        self.error = False

        self.get_references()

        if (not self.has_error()):
            papers.append(pid)

    def add_referenced_paper(self, paper):
        self.referenced_papers.append(paper)

    def get_references(self):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{self.pid}/references"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()
            tmp_references = results.get("data",[])

            tmp_pids = [ref["citedPaper"]["paperId"] for ref in tmp_references if "citedPaper" in ref]

            if tmp_pids:

                r = requests.post(
                    'https://api.semanticscholar.org/graph/v1/paper/batch',
                    params={'fields': 'isOpenAccess'},
                    json={
                        "ids": tmp_pids}
                )
                if (r.status_code == 200):
                    results = r.json()
                    for ref in results:
                        if isinstance(ref, dict) and ref.get("isOpenAccess") is True:
                            self.references.append(ref["paperId"])

                else:
                    self.error = True
                    return

            n_references = len(self.references)
            n_papers = max_references if n_references > max_references else n_references

            self.references = self.references[:n_papers]

        else:
            self.error = True

    def to_dict(self):
        return {"pid": self.pid, "references": []}

    def has_error(self):
        return self.error


def traverse_references(paper, curr_depth):
    if (curr_depth == max_depth):
        return
    for pid in paper.references:
        new_paper = Paper(pid)
        if not new_paper.has_error():
            traverse_references(new_paper, curr_depth+1)
            paper.add_referenced_paper(new_paper)


def traverse_tree_util(paper, tree_dict):
    if len(paper.references) == 0:
        tree_dict["references"].append(paper.to_dict())
        return

    for paper in paper.referenced_papers:
        tmp_dict = paper.to_dict()
        traverse_tree_util(paper, tmp_dict)
        tree_dict["references"].append(tmp_dict)


def tree_to_json(paper):
    tree_dict = paper.to_dict()
    traverse_tree_util(paper, tree_dict)

    json_data_bytes =  json.dumps(tree_dict, indent=4).encode('utf-8')
   
    s3_client = boto3.client('s3')

    json_buffer = BytesIO(json_data_bytes)

    s3_client.upload_fileobj(json_buffer,'search-engine-bd', 'data/corpus.json')

    json_buffer.close()



def download_papers():
    global papers
    s3_client = boto3.client('s3')

    download_papers_pdf(papers)

    for paper in papers:
        content = ""
        
        pdf_object = s3_client.get_object(Bucket='search-engine-bd',Key=f"corpus/pdf/{paper}.pdf")
        pdf_data = BytesIO(pdf_object['Body'].read())

        pdf_reader = PyPDF2.PdfReader(pdf_data)
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            content += page_text

        text_data = BytesIO(content.encode('utf-8'))
        s3_client.upload_fileobj(text_data, 'search-engine-bd', f'corpus/txt/{paper}.txt'.format(paper))

        pdf_data.close()
        text_data.close()

if __name__ == "__main__":
    root = Paper("649def34f8be52c8b66281af98ae884c09aef38b")
    traverse_references(root, 0)
    tree_to_json(root)
    download_papers()
