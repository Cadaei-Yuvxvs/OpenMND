import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import time

class PubMedService:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return list of PMIDs"""
        url = f"{self.base_url}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        if self.api_key:
            params["api_key"] = self.api_key
            
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    
    def fetch_paper_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed information for given PMIDs"""
        if not pmids:
            return []
            
        # PubMed allows up to 200 IDs per request
        batch_size = 200
        all_papers = []
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            papers = self._fetch_batch(batch_pmids)
            all_papers.extend(papers)
            
            # Rate limiting - be respectful to NCBI servers
            time.sleep(0.5)
            
        return all_papers
    
    def _fetch_batch(self, pmids: List[str]) -> List[Dict]:
        """Fetch a batch of papers"""
        url = f"{self.base_url}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        if self.api_key:
            params["api_key"] = self.api_key
            
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return self._parse_xml_response(response.text)
    
    def _parse_xml_response(self, xml_content: str) -> List[Dict]:
        """Parse XML response and extract paper information"""
        root = ET.fromstring(xml_content)
        papers = []
        
        for article in root.findall(".//PubmedArticle"):
            try:
                paper_data = self._extract_paper_data(article)
                if paper_data:
                    papers.append(paper_data)
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
                
        return papers
    
    def _extract_paper_data(self, article) -> Optional[Dict]:
        """Extract data from a single PubmedArticle XML element"""
        try:
            # Basic information
            medline_citation = article.find(".//MedlineCitation")
            pmid = medline_citation.find(".//PMID").text
            
            article_elem = medline_citation.find(".//Article")
            title_elem = article_elem.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""
            
            # Abstract
            abstract_elem = article_elem.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Authors
            authors = []
            for author in article_elem.findall(".//Author"):
                last_name = author.find("LastName")
                first_name = author.find("ForeName")
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
            
            # Journal
            journal_elem = article_elem.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else ""
            
            # Publication date
            pub_date = self._extract_publication_date(article_elem)
            
            # DOI
            doi_elem = article_elem.find(".//ELocationID[@EIdType='doi']")
            doi = doi_elem.text if doi_elem is not None else ""
            
            # MeSH terms
            mesh_terms = []
            for mesh in medline_citation.findall(".//MeshHeading/DescriptorName"):
                mesh_terms.append(mesh.text)
            
            return {
                "pubmed_id": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
                "doi": doi,
                "mesh_terms": mesh_terms
            }
            
        except Exception as e:
            print(f"Error extracting paper data: {e}")
            return None
    
    def _extract_publication_date(self, article_elem) -> Optional[datetime]:
        """Extract publication date from article element"""
        try:
            pub_date = article_elem.find(".//Journal/JournalIssue/PubDate")
            if pub_date is not None:
                year_elem = pub_date.find("Year")
                month_elem = pub_date.find("Month")
                day_elem = pub_date.find("Day")
                
                year = int(year_elem.text) if year_elem is not None else 2000
                month = self._parse_month(month_elem.text) if month_elem is not None else 1
                day = int(day_elem.text) if day_elem is not None else 1
                
                return datetime(year, month, day)
        except:
            pass
        return None
    
    def _parse_month(self, month_str: str) -> int:
        """Convert month string to number"""
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        try:
            return int(month_str)
        except:
            return month_map.get(month_str.lower()[:3], 1)
