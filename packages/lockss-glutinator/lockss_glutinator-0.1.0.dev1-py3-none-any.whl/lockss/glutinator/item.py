#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Mimicking what datamodel-codegen does, not sure if it's because of --target-python-version=3.9
from __future__ import annotations

from re import Pattern
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

ISSN_PATTERN_STR = r'^[0-9]{4}-[0-9]{3}[0-9X]$'

class PublisherModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['publisher']
    id: str
    name: str
    alternate_names: Optional[List[str]] = Field(None, alias='alternate-names')
    variant_names: Optional[List[Union[str, Pattern]]] = Field(None, alias='variant-names')

class JournalModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['journal']
    id: str
    name: str
    alternate_names: Optional[List[str]] = Field(None, alias='alternate-names')
    variant_names: Optional[List[Union[str, Pattern]]] = Field(None, alias='variant-names')
    issn: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR)
    eissn: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR)
    issn_l: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR, alias='issn-l')

class JournalVolumeModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['journal-volume']
    id: Union[str, int]
    name: str

class JournalIssueModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['journal-ssue']
    id: Union[str, int]
    name: str
    publication_date: Optional[str] = None

class Item(object):

    def __init__(self, parent):
        self.parent = parent
        self.children = list()

    def path(self):
        raise NotImplementedError('Item::path')

class Publisher(Item):

    def __init__(self, root: Item, publisher_model):
        super().__init__(root)
        self.model = PublisherModel(**publisher_model)
        # Synonyms
        self.root = self.parent

    def journals(self):
        return self.children.filter(lambda c: isinstance(c, Journal))

    def path(self):
        return f'/{self.model.id}/index.html'

class Journal(Item):

    def __init__(self, publisher: Publisher, journal_model):
        super().__init__(publisher)
        self.model = JournalModel(**journal_model)
        # Synonyms
        self.publisher = self.parent

    def volumes(self):
        return self.children

    def path(self):
        return f'/{self.publisher.model.id}/{self.model.id}/index.html'

class JournalVolume(Item):

    def __init__(self, journal: Journal, journal_volume_model):
        super().__init__(journal)
        self.model = JournalVolumeModel(**journal_volume_model)
        # Synonyms
        self.journal = self.parent

    def issues(self):
        return self.children

    def path(self):
        return f'/{self.journal.publisher.model.id}/{self.journal.model.id}/{self.model.id}/index.html'

class JournalIssue(Item):

    def __init__(self, journal_volume: JournalVolume, journal_issue_model):
        super().__init__(journal_volume)
        self.model = JournalVolumeModel(**journal_issue_model)
        # Synonyms
        self.journal_volume = self.parent

    def articles(self):
        return self.children

    def path(self):
        return f'/{self.journal_volume.journal.publisher.model.id}/{self.journal_volume.journal.model.id}/{self.journal_volume.model.id}/{self.model.id}/index.html'

# PUBLISHER = 'publisher'
# JOURNAL = 'journal'
# VOLUME = 'volume'
# ISSUE = 'issue'
# ARTICLE = 'article'
#
# class Item(object):
#
#     kind = None
#
#     def __init__(self, parent):
#         super().__init__()
#         self.parent = parent
#         self.children = list()
#         self.name = None
#         self.subtitle = None
#         self.sortable = None
#         self.title = None
#
#     def add(self, child):
#         self.children.append(child)
#
#     def path(self):
#         raise NotImplementedError('Item::path')
#
# class Publisher(Item):
#
#     kind = PUBLISHER
#
#     def __init__(self):
#         super().__init__(None)
#         self.publisher_code = None
#
#     def path(self):
#         return f'/{self.publisher_code}/index.html'
#
# class Journal(Item):
#
#     kind = JOURNAL
#
#     def __init__(self, publisher):
#         super().__init__(publisher)
#         self.journal_code = None
#         self.issnl = None
#         self.issn = None
#         self.eissn = None
#
#     def path(self):
#         return f'/{self.parent.publisher_code}/{self.journal_code}/index.html'
#
# class Volume(Item):
#
#     kind = VOLUME
#
#     def __init__(self, journal):
#         super().__init__(journal)
#
#     def path(self):
#         return f'/{self.parent.parent.publisher_code}/{self.parent.journal_code}/{self.sortable}/index.html'
#
# class Issue(Item):
#
#     kind = ISSUE
#
#     def __init__(self, issue):
#         super().__init__(issue)
#
#     def path(self):
#         return f'/{self.parent.parent.parent.publisher_code}/{self.parent.parent.journal_code}/{self.parent.sortable}/{self.sortable}/index.html'
#
# class Article(Item):
#
#     kind = ARTICLE
#
#     def __init__(self, issue):
#         super().__init__(issue)
#         self.authors = list()
#         self.doi = None
#
#     def path(self):
#         return f'/{self.parent.parent.parent.parent.publisher_code}/{self.parent.parent.parent.journal_code}/{self.parent.parent.sortable}/{self.parent.sortable}/{self.sortable}/index.html'
#
# class Author(object):
#
#     def __init__(self, first_name=None, last_name=None):
#         super().__init__()
#         self.first_name = first_name
#         self.last_name = last_name

def load_sample_data():
    import json
    import os
    with open(f'{os.getcwd()}/2024_content_journal_data.json', 'r') as f:
        data = json.load(f)
    publishers = list()
    for data_provider in data['providers']:
        publisher = Publisher()
        publisher.name = data_provider['provider_name']
        publisher.title = publisher.name
        publisher.sortable = publisher.name
        publisher.publisher_code = 'emhsmp' ###FIXME
        publishers.append(publisher)
        for data_journal in data_provider['journals']:
            journal = Journal(publisher)
            journal.name = data_journal['journal_title']
            journal.title = journal.name
            journal.sortable = journal.name
            journal.issn = data_journal.get('issn')
            journal.eissn = data_journal.get('eissn')
            journal.journal_code = f'emhsmp{data_journal['journal_id'].lower()}' ###FIXME
            publisher.add(journal)
            for data_volume in data_journal['volumes']:
                volume = Volume(journal)
                volume_number_str = data_volume['volume_number']
                if not volume_number_str:
                    print('Null volume number')
                    continue
                volume.sortable = int(volume_number_str)
                volume.name = f'Volume {volume.sortable}'
                volume.title = f'{journal.name} {volume.name}'
                journal.add(volume)
                for data_issue in data_volume['issues']:
                    issue = Issue(volume)
                    issue_number_str = data_issue['issue_number']
                    if not issue_number_str:
                        print('Null issue number')
                        continue
                    issue.sortable = int(issue_number_str)
                    issue.name = f'Issue {issue.sortable}'
                    issue.title = f'{journal.name} {volume.name} {issue.name}'
                    volume.add(issue)
                    for data_article in data_issue['articles']:
                        article = Article(issue)
                        article.title = data_article['title']
                        article.name = article.title
                        article_id_str = data_article['article_id']
                        article.sortable = int(article_id_str)
                        article.doi = data_article.get('doi')
                        for data_author in data_article['authors']:
                            author = Author(last_name=data_author['last_name'], first_name=data_author['first_name'])
                            article.authors.append(author)
                        issue.add(article)
                    issue.children.sort(key=lambda a: a.sortable)
                volume.children.sort(key=lambda i: i.sortable)
            journal.children.sort(key=lambda v: v.sortable)
        publisher.children.sort(key=lambda j: j.sortable)
    publishers.sort(key=lambda p: p.sortable)
    return publishers

if __name__ == '__main__':
    publishers = load_sample_data()
