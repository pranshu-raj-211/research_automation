# Data model for Research assistant

Based on the required data for each entity and proposed access pattern, an initial data model has been built as follows:


![data model](data_model.png)


## Collections:

### 1. User
Stores info of users registering onto the app. Useful only for the hosted version, local version will be based on single user access.


### 2. Topic
Topics are the research topics on which papers are being collected for analysis. Users group papers into topics, which are then used to provide analysis on the topic as a whole. Mixing papers of different topics is a bad idea, logically speaking, due to mixing of concerns.


### 3. Docs
A document is a pdf file of the paper that is to be analyzed uploaded to the system under a specific topic. This needs to be broken down in the ingestion pipeline and stored for retrieval and other downstream tasks such as search, question answering, structured info generation.

**Schema**:
- id: task_id (uuid)
- topic_id: foreign key referencing topic to which the document belongs
- user_id: foreign key referencing topic to which the document belongs
- text: list of ids of text entries (chunks and metadata)
- authors: authors of the given document, for structured info extraction
- citations: sources referenced in the document, for reference collection
- status: status of processing of document (one of `pending`, `failed` or `done`)
- schema_version: int specifying schema version to track changes

### 4. Text
Part of text from the document. Chunks are created in order to break down to smaller ideas, which leads to better semantic search. Each document contains the full text, vector embedding along with metadata on the text for reference.


**Schema**:
- id: ObjectID (primary key set by DB)
- doc_id: ID of document the text is from
- topic_id: ID of topic the document belongs to
- page_no: Page number of document text is from
- para_no: Paragraph number of page text is from. May not reference the actual paragraph number, depends on chunking
- text: Full text of chunk
- embedding: Vector made by embedding the chunk text
- schema_version: int specifying schema version to track changes

### 5. Chat
Chat on documents inside a topic, question answering with source citations.