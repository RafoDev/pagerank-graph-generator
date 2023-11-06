import requests
import json
import PyPDF2
from downloader import download_papers_pdf
# from pdfminer.high_level import extract_text
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
        url = f"https://api.semanticscholar.org/graph/v1/paper/{self.pid}/references".format(
            self.pid)
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()
            tmp_references = results["data"]

            tmp_pids = []
            for ref in tmp_references:
                tmp_pids.append(ref["citedPaper"]["paperId"])

            r = requests.post(
                'https://api.semanticscholar.org/graph/v1/paper/batch',
                params={'fields': 'isOpenAccess'},
                json={
                    "ids": tmp_pids}
            )
            if (response.status_code == 200):
                results = r.json()
                for ref in results:
                    if ref and ref["isOpenAccess"] is True:
                        self.references.append(ref["paperId"])

            else:
                self.error = True
                return

            n_references = len(self.references)
            n_papers = max_references if n_references > max_references else n_references

            self.references = self.references[0:n_papers]

            print(self.references)

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

    with open('s3://hive-practice/data/corpus.json', 'w') as json_file:
        json.dump(tree_dict, json_file, indent=4)


def download_papers():
    global papers

    download_papers_pdf(papers)

    for paper in papers:
        content = ""
        with open(f"s3://hive-practice/corpus/pdf/{paper}.pdf".format(paper), 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            n_pages = len(pdf_reader.pages)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                content += page_text

            with open(f's3://hive-practice/corpus/txt/{paper}.txt'.format(paper), 'w') as txt_file:
                txt_file.write(content)


if __name__ == "__main__":
    root = Paper("649def34f8be52c8b66281af98ae884c09aef38b")
    traverse_references(root, 0)
    tree_to_json(root)
    download_papers()
