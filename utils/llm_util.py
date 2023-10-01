import openai
import tiktoken
from config import Config
class LLMUtil:
    OPENAI_API_KEY = Config.OPENAI_API_KEY
    # openai.organization = Config.OpenAI_ORG
    DAVINCI_MODEL_NAME = "text-davinci-003"
    TURBO_16k_MODEL_NAME = "gpt-3.5-turbo-16k"
    TURBO_MODEL_NAME = "gpt-3.5-turbo"
    GPT4_MODEL_NAME = "gpt-4"
    TURBO_0301_MODEL_NAME = "gpt-3.5-turbo-0301"
    ROLE_SYSTEM = 'system'
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    @staticmethod
    def get_tokens(prompt):
        prompt = str(prompt)
        embedding_encoding = Config.embedding_encoding
        encoding = tiktoken.get_encoding(embedding_encoding)
        tokens = encoding.encode(prompt, disallowed_special=())
        return tokens

    @staticmethod
    def get_top_k_tokens(prompt, k):
        embedding_encoding = Config.embedding_encoding
        encoding = tiktoken.get_encoding(embedding_encoding)
        tokens = encoding.encode(prompt, disallowed_special=())
        return tokens[:k]

    @staticmethod
    def calculate_token_nums_for_prompt(prompt):
        tokens = LLMUtil.get_tokens(prompt)

        return len(tokens)

    @staticmethod
    def ask_chat_turbo(message, model=TURBO_16k_MODEL_NAME, openai_key=OPENAI_API_KEY, temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=message,
            temperature=temperature,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            api_key=openai_key
        )
        return response.choices[0]["message"]["content"]

    @staticmethod
    def ask_non16k_chat_turbo(message, model=TURBO_MODEL_NAME, openai_key=OPENAI_API_KEY, temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=message,
            temperature=temperature,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            api_key=openai_key
        )
        return response.choices[0]["message"]["content"]

    @staticmethod
    def ask_turbo(prompt, model=TURBO_MODEL_NAME, temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return (response['choices'][0]['message']['content'])



    @staticmethod
    def ask_16k_turbo(prompt, model=TURBO_16k_MODEL_NAME, temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return (response['choices'][0]['message']['content'])


if __name__ == '__main__':
    system_prompt = '''
Developer {
    @persona {
        You are an expert Python programming language developer;
        You generate a new function in the .py file in the code repository;
    }

    @audience {
        Code Repository;
    }

    @terminology {
        function_description: The description of to_be_generated_function
        function_definition: The definition of to_be_generated_function
        py_file_path: The file path of the .py file
        variable_in_py_file: The variables in the .py file
        local_function_in_py_file: The functions in the .py file. All local_functions are already implemented. All local_functions are shown as fully qualified name, summary, and signature. If the local_function_in_py_file is an __init__ function, its source code is also displayed.
        to_be_generated_function: The source code of the to-be-generated new function in the .py file in the code repository.
        all_used_library_and_local_function: All used local_function_in_py_file and third party library for implementing the to_be_generated_function.
    }

    @context-control {
        The code you generate needs to satisfy function_description and function_definition, but it also needs to take into account the py_file_path, variable_in_py_file, and local_function_in_py_file.
    }

    @instruction {
        @rule1: Think about how to leverage py_file_path, variable_in_py_file, and local_function_in_py_file while implementing the to_be_generated_function code.
        @rule2: If you call any local_function_in_py_file, please import its fully qualified name.
        @rule3: You can add third-party libraries or define new functions yourself to implement to_be_generated_function.
        @rule4: If you use any third-party libraries, you need to add the import statement.
        @rule5: If you define any new function, you must implement it and not leave any function blank!
        @rule: Please follow the rules 1,2,3,4,5 strictly!

        @command {
            Think about the logic and steps required to implement the to_be_generated_function code based on function_description and function_definition.
            Implement the to_be_generated_function code according to the logic and steps.
        }

        @format {
            Present the all_used_apis;
            Present the source code of to_be_generated_function;
        }
    }
}
'''

    example_3_input = '''#function_description
    Checks to see if a table element contains bulleted text.
#end

#function_definition
    def _is_bulleted_table(tag_elem) -> bool
#end

#py_file_path
    unstructured-0.10.12/unstructured/documents/html.py
#end


#local_function_in_py_file
    class TagsMixin
        function1{
            fully qualified name: unstructured.documents.html.TagsMixin.__init__
            summary: Initialize an object with optional tag, ancestor tags, links, emphasized texts, and other arguments. If tag is None, raise a TypeError.
            source_code: def __init__(self, *args, tag: Optional[str]=None, ancestortags: Sequence[str]=(), links: Sequence[Link]=[], emphasized_texts: Sequence[dict]=[], **kwargs):
                if tag is None:
                    raise TypeError('tag argument must be passed and not None')
                else:
                    self.tag = tag
                self.ancestortags = ancestortags
                self.links = links
                self.emphasized_texts = emphasized_texts
                super().__init__(*args, **kwargs)
        }

    class HTMLDocument
        function2{
            fully qualified name: unstructured.documents.html.HTMLDocument.__init__
            summary: Initialize an object with optional stylesheet, parser, and assemble_articles parameters.
            source_code: def __init__(self, stylesheet: Optional[str]=None, parser: VALID_PARSERS=None, assemble_articles: bool=True):
                self.assembled_articles = assemble_articles
                super().__init__(stylesheet=stylesheet, parser=parser)
        }

        function3{
            fully qualified name: unstructured.documents.html.HTMLDocument._read
            summary: Read and structure an HTML document, looking for article tags and inserting page breaks between multiple article sections.
            signature: def _read(self) -> List[Page]
        }

        function4{
            fully qualified name: unstructured.documents.html.HTMLDocument.doc_after_cleaners
            summary: Filter elements in an HTML document based on specified criteria and return a new instance of the class.
            signature: def doc_after_cleaners(self, skip_headers_and_footers, skip_table_text, inplace) -> HTMLDocument
        }

    function5{
        fully qualified name: unstructured.documents.html._get_links_from_tag
        summary: Get all links from a given HTML tag element, including its descendants.
        signature: def _get_links_from_tag(tag_elem: etree.Element) -> List[Link]
    }

    function6{
        fully qualified name: unstructured.documents.html._get_emphasized_texts_from_tag
        summary: Get emphasized texts enclosed in specific HTML tags from a given tag element.
        signature: def _get_emphasized_texts_from_tag(tag_elem: etree.Element) -> List[dict]
    }

    function7{
        fully qualified name: unstructured.documents.html._parse_tag
        summary: Parse an etree element and convert it to a Text element if there is applicable text in the element. Keep ancestor tags for filtering or classification purposes.
        signature: def _parse_tag(tag_elem: etree.Element) -> Optional[Element]
    }

    function8{
        fully qualified name: unstructured.documents.html._text_to_element
        summary: Given the text, tag, ancestor tags, links, and emphasized texts, this function returns the appropriate HTML element based on the text's characteristics.
        signature: def _text_to_element(text: str, tag: str, ancestortags: Tuple[str, ...], links: List[Link], emphasized_texts: List[dict]) -> Optional[Element]
    }

    function9{
        fully qualified name: unstructured.documents.html._is_container_with_text
        summary: Check if a tag is a container that contains text.
        signature: def _is_container_with_text(tag_elem: etree.Element) -> bool
    }

    function10{
        fully qualified name: unstructured.documents.html.is_narrative_tag
        summary: Check if the given text is a narrative based on the tag information.
        signature: def is_narrative_tag(text: str, tag: str) -> bool
    }

    function11{
        fully qualified name: unstructured.documents.html._construct_text
        summary: Extract text from a text tag element, including tail text.
        signature: def _construct_text(tag_elem: etree.Element, include_tail_text: bool) -> str
    }

    function12{
        fully qualified name: unstructured.documents.html._is_text_tag
        summary: Check if a tag potentially contains narrative text.
        signature: def _is_text_tag(tag_elem: etree.Element, max_predecessor_len: int) -> bool
    }

    function13{
        fully qualified name: unstructured.documents.html._process_list_item
        summary: Process an etree element and extract relevant bulleted text to convert it into ListItem objects. Also returns the next html elements to skip processing if bullets are found in a div element.
        signature: def _process_list_item(tag_elem: etree.Element, max_predecessor_len: int) -> Tuple[Optional[Element], etree.Element]
    }

    function14{
        fully qualified name: unstructured.documents.html._get_bullet_descendants
        summary: Return a tuple of descendant elements of `next_element`
        signature: def _get_bullet_descendants(element, next_element) -> Tuple[etree.Element, ...]
    }

    function15{
        fully qualified name: unstructured.documents.html.is_list_item_tag
        summary: Check if a tag contains bulleted text.
        signature: def is_list_item_tag(tag_elem: etree.Element) -> bool
    }

    function16{
        fully qualified name: unstructured.documents.html._bulleted_text_from_table
        summary: Extract bulletized narrative text from a table, excluding non-bullet text.
        signature: def _bulleted_text_from_table(table) -> List[Element]
    }

    function17{
        fully qualified name: unstructured.documents.html._has_adjacent_bulleted_spans
        summary: Check if a div contains two or more adjacent spans beginning with a bullet, treating it as a single bulleted text element.
        signature: def _has_adjacent_bulleted_spans(tag_elem: etree.Element, children: List[etree.Element]) -> bool
    }

    function18{
        fully qualified name: unstructured.documents.html.has_table_ancestor
        summary: Check if an element has ancestors that are table elements.
        signature: def has_table_ancestor(element: TagsMixin) -> bool
    }

    function19{
        fully qualified name: unstructured.documents.html.in_header_or_footer
        summary: Check if an element is contained within a header or a footer tag.
        signature: def in_header_or_footer(element: TagsMixin) -> bool
    }

    function20{
        fully qualified name: unstructured.documents.html._find_main
        summary: Find the main tag of the HTML document, or return the whole document if it doesn't exist.
        signature: def _find_main(root: etree.Element) -> etree.Element
    }

    function21{
        fully qualified name: unstructured.documents.html._find_articles
        summary: Find and return distinct articles from an HTML document, or return the entire document as a single item list if there are no article tags.
        signature: def _find_articles(root: etree.Element, assemble_articles: bool) -> List[etree.Element]
    }
#end'''

    example_3_output = '''#all_used_library_and_local_function
re
unstructured.documents.html._construct_text._construct_text
#end

#to_be_generated_function
UNICODE_BULLETS_RE = re.compile(f"(?:{BULLETS_PATTERN})(?!{BULLETS_PATTERN})")
def _is_bulleted_table(tag_elem) -> bool:

    def is_bulleted_text(text: str) -> bool:
        """Checks to see if the section of text is part of a bulleted list."""
        return UNICODE_BULLETS_RE.match(text.strip()) is not None

    if tag_elem.tag != "table":
        return False

    rows = tag_elem.findall(".//tr")
    for row in rows:
        text = _construct_text(row)
        if text and not is_bulleted_text(text):
            return False

    return True
#end'''

    example_1_input = '''#function_description
    Fetches the file from the current filesystem and stores it locally.
#end

#function_definition
    def get_file(self)
    @Note: This function belongs to class FsspecIngestDoc
#end

#py_file_path
    unstructured-0.10.12/unstructured/ingest/connector/s3_2.py
#end

#variable_in_py_file
    SUPPORTED_REMOTE_FSSPEC_PROTOCOLS = [
    "s3",
    "s3a",
    "abfs",
    "az",
    "gs",
    "gcs",
    "box",
    "dropbox",
    ]
#end

#local_function_in_py_file
    class S3DestinationConnector
        function1{
            fully qualified name: unstructured.ingest.connector.s3_2.S3DestinationConnector.__init__
            summary: Initialize an object with write and connector configurations, with dependencies on 's3fs' and 'fsspec' libraries.
            source_code: @requires_dependencies(['s3fs', 'fsspec'], extras='s3')
            def __init__(self, write_config: WriteConfig, connector_config: BaseConnectorConfig):
                super().__init__(write_config=write_config, connector_config=connector_config)
        }

    class S3SourceConnector
        function2{
            fully qualified name: unstructured.ingest.connector.s3_2.S3SourceConnector.__init__
            summary: Initialize an object with read configuration, connector configuration, and partition configuration.
            source_code: @requires_dependencies(['s3fs', 'fsspec'], extras='s3')
            def __init__(self, read_config: ReadConfig, connector_config: BaseConnectorConfig, partition_config: PartitionConfig):
                super().__init__(read_config=read_config, connector_config=connector_config, partition_config=partition_config)
        }

    class FsspecDestinationConnector
        function3{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.__init__
            summary: Initialize an object with write and connector configurations, and set the filesystem attribute based on the connector protocol and access arguments.
            source_code: def __init__(self, write_config: WriteConfig, connector_config: BaseConnectorConfig):
                from fsspec import AbstractFileSystem, get_filesystem_class
                super().__init__(write_config=write_config, connector_config=connector_config)
                self.fs: AbstractFileSystem = get_filesystem_class(self.connector_config.protocol)(**self.connector_config.access_kwargs)
        }

        function4{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.initialize
            summary: Initialize the object, does nothing.
            signature: def initialize(self)
        }

        function5{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.write
            summary: Write a list of documents to a specified filesystem path.
            signature: def write(self, docs: t.List[BaseIngestDoc]) -> None
        }

    class FsspecIngestDoc
        function6{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._tmp_download_file
            summary: Return the temporary download file path by replacing the remote file path with the download directory path.
            signature: def _tmp_download_file(self)
        }

        function7{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._output_filename
            summary: Return the output filename based on the partition configuration and remote file path.
            signature: def _output_filename(self)
        }

        function8{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._create_full_tmp_dir_path
            summary: Create a full temporary directory path by creating parent directories if they don't exist.
            signature: def _create_full_tmp_dir_path(self)
        }

        function9{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc.filename
            summary: Return the filename of the downloaded file from the cloud.
            signature: def filename(self)
        }

    class SimpleFsspecConfig
        function10{
            fully qualified name: unstructured.ingest.connector.s3_2.SimpleFsspecConfig.__post_init__
            summary: Parse and initialize the protocol, directory path, and file path from a given path.
            signature: def __post_init__(self)
        }

    class S3IngestDoc
        function11{
            fully qualified name: unstructured.ingest.connector.s3_2.S3IngestDoc.get_file
            summary: Get a file using the `get_file` method from the parent class, with additional dependencies on 's3fs' and 'fsspec' for the 's3' extra.
            signature: def get_file(self)
        }

    class FsspecSourceConnector
        function12{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.__init__
            summary: Initialize an object with read configuration, connector configuration, and partition configuration. Set the filesystem attribute based on the connector protocol and access kwargs.
            source_code: def __init__(self, read_config: ReadConfig, connector_config: BaseConnectorConfig, partition_config: PartitionConfig):
                from fsspec import AbstractFileSystem, get_filesystem_class
                super().__init__(read_config=read_config, connector_config=connector_config, partition_config=partition_config)
                self.fs: AbstractFileSystem = get_filesystem_class(self.connector_config.protocol)(**self.connector_config.access_kwargs)
        }

        function13{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.initialize
            summary: Verify that metadata can be retrieved for an object and validate connection information. If no objects are found in the specified path, raise a ValueError.
            signature: def initialize(self)
        }

        function14{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector._list_files
            summary: List files in a directory, either recursively or non-recursively, and return the names of files with a size greater than 0.
            signature: def _list_files(self)
        }

        function15{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.get_ingest_docs
            summary: Return a list of ingest documents created using the given configurations and files.
            signature: def get_ingest_docs(self)
        }
#end'''

    example_1_output = '''
#all_used_library_and_local_function
fsspec.AbstractFileSystem
fsspec.get_filesystem_class
unstructured.ingest.connector.s3_2.FsspecIngestDoc._create_full_tmp_dir_path
unstructured.ingest.connector.s3_2.FsspecIngestDoc._tmp_download_file
#end

#to-be-generated-code
def get_file(self):

    self._create_full_tmp_dir_path()
    fs: AbstractFileSystem = get_filesystem_class(self.connector_config.protocol)(
        **self.connector_config.access_kwargs,
    )
    logger.debug(f"Fetching {self} - PID: {os.getpid()}")
    fs.get(rpath=self.remote_file_path, lpath=self._tmp_download_file().as_posix())
#end'''

    example_4_input = '''#function_description
    Checks to see if a table element contains bulleted text.
#end

#function_definition
    def _is_bulleted_table(tag_elem) -> bool
#end

#py_file_path
    unstructured-0.10.12/unstructured/documents/html.py
#end


#local_function_in_py_file
    class TagsMixin
        function1{
            fully qualified name: unstructured.documents.html.TagsMixin.__init__
            summary: Initialize an object with optional tag, ancestor tags, links, emphasized texts, and other arguments. If tag is None, raise a TypeError.
            source_code: def __init__(self, *args, tag: Optional[str]=None, ancestortags: Sequence[str]=(), links: Sequence[Link]=[], emphasized_texts: Sequence[dict]=[], **kwargs):
                if tag is None:
                    raise TypeError('tag argument must be passed and not None')
                else:
                    self.tag = tag
                self.ancestortags = ancestortags
                self.links = links
                self.emphasized_texts = emphasized_texts
                super().__init__(*args, **kwargs)
        }

    class HTMLDocument
        function2{
            fully qualified name: unstructured.documents.html.HTMLDocument.__init__
            summary: Initialize an object with optional stylesheet, parser, and assemble_articles parameters.
            source_code: def __init__(self, stylesheet: Optional[str]=None, parser: VALID_PARSERS=None, assemble_articles: bool=True):
                self.assembled_articles = assemble_articles
                super().__init__(stylesheet=stylesheet, parser=parser)
        }

        function3{
            fully qualified name: unstructured.documents.html.HTMLDocument._read
            summary: Read and structure an HTML document, looking for article tags and inserting page breaks between multiple article sections.
            signature: def _read(self) -> List[Page]
        }

        function4{
            fully qualified name: unstructured.documents.html.HTMLDocument.doc_after_cleaners
            summary: Filter elements in an HTML document based on specified criteria and return a new instance of the class.
            signature: def doc_after_cleaners(self, skip_headers_and_footers, skip_table_text, inplace) -> HTMLDocument
        }

    function5{
        fully qualified name: unstructured.documents.html._get_links_from_tag
        summary: Get all links from a given HTML tag element, including its descendants.
        signature: def _get_links_from_tag(tag_elem: etree.Element) -> List[Link]
    }

    function6{
        fully qualified name: unstructured.documents.html._get_emphasized_texts_from_tag
        summary: Get emphasized texts enclosed in specific HTML tags from a given tag element.
        signature: def _get_emphasized_texts_from_tag(tag_elem: etree.Element) -> List[dict]
    }

    function7{
        fully qualified name: unstructured.documents.html._parse_tag
        summary: Parse an etree element and convert it to a Text element if there is applicable text in the element. Keep ancestor tags for filtering or classification purposes.
        signature: def _parse_tag(tag_elem: etree.Element) -> Optional[Element]
    }

    function8{
        fully qualified name: unstructured.documents.html._text_to_element
        summary: Given the text, tag, ancestor tags, links, and emphasized texts, this function returns the appropriate HTML element based on the text's characteristics.
        signature: def _text_to_element(text: str, tag: str, ancestortags: Tuple[str, ...], links: List[Link], emphasized_texts: List[dict]) -> Optional[Element]
    }

    function9{
        fully qualified name: unstructured.documents.html._is_container_with_text
        summary: Check if a tag is a container that contains text.
        signature: def _is_container_with_text(tag_elem: etree.Element) -> bool
    }

    function10{
        fully qualified name: unstructured.documents.html.is_narrative_tag
        summary: Check if the given text is a narrative based on the tag information.
        signature: def is_narrative_tag(text: str, tag: str) -> bool
    }

    function11{
        fully qualified name: unstructured.documents.html._construct_text
        summary: Extract text from a text tag element, including tail text.
        signature: def _construct_text(tag_elem: etree.Element, include_tail_text: bool) -> str
    }

    function12{
        fully qualified name: unstructured.documents.html._is_text_tag
        summary: Check if a tag potentially contains narrative text.
        signature: def _is_text_tag(tag_elem: etree.Element, max_predecessor_len: int) -> bool
    }

    function13{
        fully qualified name: unstructured.documents.html._process_list_item
        summary: Process an etree element and extract relevant bulleted text to convert it into ListItem objects. Also returns the next html elements to skip processing if bullets are found in a div element.
        signature: def _process_list_item(tag_elem: etree.Element, max_predecessor_len: int) -> Tuple[Optional[Element], etree.Element]
    }

    function14{
        fully qualified name: unstructured.documents.html._get_bullet_descendants
        summary: Return a tuple of descendant elements of `next_element`
        signature: def _get_bullet_descendants(element, next_element) -> Tuple[etree.Element, ...]
    }

    function15{
        fully qualified name: unstructured.documents.html.is_list_item_tag
        summary: Check if a tag contains bulleted text.
        signature: def is_list_item_tag(tag_elem: etree.Element) -> bool
    }

    function16{
        fully qualified name: unstructured.documents.html._bulleted_text_from_table
        summary: Extract bulletized narrative text from a table, excluding non-bullet text.
        signature: def _bulleted_text_from_table(table) -> List[Element]
    }

    function17{
        fully qualified name: unstructured.documents.html._has_adjacent_bulleted_spans
        summary: Check if a div contains two or more adjacent spans beginning with a bullet, treating it as a single bulleted text element.
        signature: def _has_adjacent_bulleted_spans(tag_elem: etree.Element, children: List[etree.Element]) -> bool
    }

    function18{
        fully qualified name: unstructured.documents.html.has_table_ancestor
        summary: Check if an element has ancestors that are table elements.
        signature: def has_table_ancestor(element: TagsMixin) -> bool
    }

    function19{
        fully qualified name: unstructured.documents.html.in_header_or_footer
        summary: Check if an element is contained within a header or a footer tag.
        signature: def in_header_or_footer(element: TagsMixin) -> bool
    }

    function20{
        fully qualified name: unstructured.documents.html._find_main
        summary: Find the main tag of the HTML document, or return the whole document if it doesn't exist.
        signature: def _find_main(root: etree.Element) -> etree.Element
    }

    function21{
        fully qualified name: unstructured.documents.html._find_articles
        summary: Find and return distinct articles from an HTML document, or return the entire document as a single item list if there are no article tags.
        signature: def _find_articles(root: etree.Element, assemble_articles: bool) -> List[etree.Element]
    }
#end'''

    example_4_output = '''
#all_used_library_and_local_function
unstructured.documents.coordinates.convert_coordinate
#end

#to-be-generated-code
def convert_from_relative(
    self,
    x: Union[float, int],
    y: Union[float, int],
) -> Tuple[Union[float, int], Union[float, int]]:

    x_orientation, y_orientation = self.orientation.value
    new_x = convert_coordinate(x, 1, self.width, x_orientation)
    new_y = convert_coordinate(y, 1, self.height, y_orientation)
    return new_x, new_y
#end'''

    example_2_input = '''#function_description
    Replaces MIME encodings with their equivalent characters in the specified encoding.

    Example
    -------
    5 w=E2=80-99s -> 5 w’s
#end

#function_definition
    def replace_mime_encodings(text: str, encoding: str) -> str
#end

#py_file_path
    unstructured-0.10.12/unstructured/cleaners/core.py
#end

#variable_in_py_file
    tbl = dict.fromkeys(
    i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith("P")
    )
#end

#local_function_in_py_file
    function1{
        fully qualified name: unstructured.cleaners.core.clean_non_ascii_chars
        summary: Clean non-ascii characters from a unicode string.
        signature: def clean_non_ascii_chars(text) -> str
    }

    function2{
        fully qualified name: unstructured.cleaners.core.clean_bullets
        summary: Remove unicode bullets from a section of text.
        signature: def clean_bullets(text) -> str
    }

    function3{
        fully qualified name: unstructured.cleaners.core.clean_ordered_bullets
        summary: Clean the start of bulleted text sections by removing up to three "sub-section" bullets, accounting for numeric and alphanumeric types.
        signature: def clean_ordered_bullets(text) -> str
    }

    function4{
        fully qualified name: unstructured.cleaners.core.group_bullet_paragraph
        summary: Group paragraphs with bullets that have line breaks for visual/formatting purposes.
        signature: def group_bullet_paragraph(paragraph: str) -> list
    }

    function5{
        fully qualified name: unstructured.cleaners.core.group_broken_paragraphs
        summary: Group paragraphs with line breaks for visual/formatting purposes into single paragraphs.
        signature: def group_broken_paragraphs(text: str, line_split: re.Pattern, paragraph_split: re.Pattern) -> str
    }

    function6{
        fully qualified name: unstructured.cleaners.core.new_line_grouper
        summary: Concatenate text paragraphs separated by one-line breaks.
        signature: def new_line_grouper(text: str, paragraph_split: re.Pattern) -> str
    }

    function7{
        fully qualified name: unstructured.cleaners.core.blank_line_grouper
        summary: Concatenates text document with blank-line paragraph break pattern.
        signature: def blank_line_grouper(text: str, paragraph_split: re.Pattern) -> str
    }

    function8{
        fully qualified name: unstructured.cleaners.core.auto_paragraph_grouper
        summary: Group paragraphs in a text based on the ratio of new lines to total line count. If the ratio is below a threshold, use new-line grouping. Otherwise, use blank-line grouping.
        signature: def auto_paragraph_grouper(text: str, line_split: re.Pattern, max_line_count: int, threshold: float) -> str
    }

    function9{
        fully qualified name: unstructured.cleaners.core.replace_unicode_quotes
        summary: Replace unicode quotes and special characters in text with their expected characters.
        signature: def replace_unicode_quotes(text) -> str
    }

    function10{
        fully qualified name: unstructured.cleaners.core.remove_punctuation
        summary: Remove punctuation from a given string.
        signature: def remove_punctuation(s: str) -> str
    }

    function11{
        fully qualified name: unstructured.cleaners.core.clean_extra_whitespace
        summary: Clean extra whitespace characters in a given text.
        signature: def clean_extra_whitespace(text: str) -> str
    }

    function12{
        fully qualified name: unstructured.cleaners.core.clean_dashes
        summary: Remove dash characters from the given text.
        signature: def clean_dashes(text: str) -> str
    }

    function13{
        fully qualified name: unstructured.cleaners.core.clean_trailing_punctuation
        summary: Remove all trailing punctuation from the given text.
        signature: def clean_trailing_punctuation(text: str) -> str
    }
    
    function14{
        fully qualified name: unstructured.cleaners.core.clean_prefix
        summary: Remove prefixes from a string based on a specified pattern, with options to ignore case and strip leading whitespace.
        signature: def clean_prefix(text: str, pattern: str, ignore_case: bool, strip: bool) -> str
    }
    
    function15{
        fully qualified name: unstructured.cleaners.core.clean_postfix
        summary: Remove postfixes from a string based on a specified pattern, with options to ignore case and strip trailing whitespace.
        signature: def clean_postfix(text: str, pattern: str, ignore_case: bool, strip: bool) -> str
    }
    
    function16{
        fully qualified name: unstructured.cleaners.core.clean
        summary: Clean text by removing extra whitespace, dashes, bullets, trailing punctuation, and converting to lowercase if specified.
        signature: def clean(text: str, extra_whitespace: bool, dashes: bool, bullets: bool, trailing_punctuation: bool, lowercase: bool) -> str
    }
    
    function17{
        fully qualified name: unstructured.cleaners.core.bytes_string_to_string
        summary: Convert a string representation of a byte string to a regular string using the specified encoding.
        signature: def bytes_string_to_string(text: str, encoding: str)
    }
#end'''

    example_2_output = '''
#all_used_library_and_local_function
quopri
#end

#to-be-generated-code
def replace_mime_encodings(text: str, encoding: str) -> str:
    def format_encoding_str(encoding: str) -> str:

        formatted_encoding = encoding.lower().replace("_", "-")

        annotated_encodings = ["iso-8859-6-i", "iso-8859-6-e", "iso-8859-8-i", "iso-8859-8-e"]
        if formatted_encoding in annotated_encodings:
            formatted_encoding = formatted_encoding[:-2]  # remove the annotation

        return formatted_encoding


    formatted_encoding = format_encoding_str(encoding)
    return quopri.decodestring(text.encode(formatted_encoding)).decode(formatted_encoding)
#end'''


    User_Input1 = """#function_description
    Fetches the file from the current filesystem and stores it locally.
#end

#function_definition
    def get_file(self)
    @Note: This function belongs to class FsspecIngestDoc
#end

#py_file_path
    unstructured-0.10.12/unstructured/ingest/connector/s3_2.py
#end

#variable_in_py_file
    SUPPORTED_REMOTE_FSSPEC_PROTOCOLS = [
    "s3",
    "s3a",
    "abfs",
    "az",
    "gs",
    "gcs",
    "box",
    "dropbox",
    ]
#end

#local_function_in_py_file
    class S3DestinationConnector
        function1{
            fully qualified name: unstructured.ingest.connector.s3_2.S3DestinationConnector.__init__
            summary: Initialize an object with write and connector configurations, with dependencies on 's3fs' and 'fsspec' libraries.
            source_code: @requires_dependencies(['s3fs', 'fsspec'], extras='s3')
            def __init__(self, write_config: WriteConfig, connector_config: BaseConnectorConfig):
                super().__init__(write_config=write_config, connector_config=connector_config)
        }

    class S3SourceConnector
        function2{
            fully qualified name: unstructured.ingest.connector.s3_2.S3SourceConnector.__init__
            summary: Initialize an object with read configuration, connector configuration, and partition configuration.
            source_code: @requires_dependencies(['s3fs', 'fsspec'], extras='s3')
            def __init__(self, read_config: ReadConfig, connector_config: BaseConnectorConfig, partition_config: PartitionConfig):
                super().__init__(read_config=read_config, connector_config=connector_config, partition_config=partition_config)
        }

    class FsspecDestinationConnector
        function3{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.__init__
            summary: Initialize an object with write and connector configurations, and set the filesystem attribute based on the connector protocol and access arguments.
            source_code: def __init__(self, write_config: WriteConfig, connector_config: BaseConnectorConfig):
                from fsspec import AbstractFileSystem, get_filesystem_class
                super().__init__(write_config=write_config, connector_config=connector_config)
                self.fs: AbstractFileSystem = get_filesystem_class(self.connector_config.protocol)(**self.connector_config.access_kwargs)
        }

        function4{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.initialize
            summary: Initialize the object, does nothing.
            signature: def initialize(self)
        }

        function5{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecDestinationConnector.write
            summary: Write a list of documents to a specified filesystem path.
            signature: def write(self, docs: t.List[BaseIngestDoc]) -> None
        }

    class FsspecIngestDoc
        function6{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._tmp_download_file
            summary: Return the temporary download file path by replacing the remote file path with the download directory path.
            signature: def _tmp_download_file(self)
        }

        function7{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._output_filename
            summary: Return the output filename based on the partition configuration and remote file path.
            signature: def _output_filename(self)
        }

        function8{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc._create_full_tmp_dir_path
            summary: Create a full temporary directory path by creating parent directories if they don't exist.
            signature: def _create_full_tmp_dir_path(self)
        }

        function9{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecIngestDoc.filename
            summary: Return the filename of the downloaded file from the cloud.
            signature: def filename(self)
        }

    class SimpleFsspecConfig
        function10{
            fully qualified name: unstructured.ingest.connector.s3_2.SimpleFsspecConfig.__post_init__
            summary: Parse and initialize the protocol, directory path, and file path from a given path.
            signature: def __post_init__(self)
        }

    class S3IngestDoc
        function11{
            fully qualified name: unstructured.ingest.connector.s3_2.S3IngestDoc.get_file
            summary: Get a file using the `get_file` method from the parent class, with additional dependencies on 's3fs' and 'fsspec' for the 's3' extra.
            signature: def get_file(self)
        }

    class FsspecSourceConnector
        function12{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.__init__
            summary: Initialize an object with read configuration, connector configuration, and partition configuration. Set the filesystem attribute based on the connector protocol and access kwargs.
            source_code: def __init__(self, read_config: ReadConfig, connector_config: BaseConnectorConfig, partition_config: PartitionConfig):
                from fsspec import AbstractFileSystem, get_filesystem_class
                super().__init__(read_config=read_config, connector_config=connector_config, partition_config=partition_config)
                self.fs: AbstractFileSystem = get_filesystem_class(self.connector_config.protocol)(**self.connector_config.access_kwargs)
        }

        function13{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.initialize
            summary: Verify that metadata can be retrieved for an object and validate connection information. If no objects are found in the specified path, raise a ValueError.
            signature: def initialize(self)
        }

        function14{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector._list_files
            summary: List files in a directory, either recursively or non-recursively, and return the names of files with a size greater than 0.
            signature: def _list_files(self)
        }

        function15{
            fully qualified name: unstructured.ingest.connector.s3_2.FsspecSourceConnector.get_ingest_docs
            summary: Return a list of ingest documents created using the given configurations and files.
            signature: def get_ingest_docs(self)
        }
#end"""

    User_Input2 = """
#function_description
    Uses title elements to identify sections within the document for chunking. Splits
    off into a new section when a title is detection or if metadata changes, which happens
    when page numbers or sections change. Cuts off sections once they have exceeded
    a character length of new_after_n_chars.

    Parameters
    ----------
    elements
        A list of unstructured elements. Usually the ouput of a partition functions.
    multipage_sections
        If True, sections can span multiple pages. Defaults to True.
    combine_under_n_chars
        Combines elements (for example a series of titles) until a section reaches
        a length of n characters.
    new_after_n_chars
        Cuts off new sections once they reach a length of n characters
#end

#function_definition
    def chunk_by_title(elements: List[Element], multipage_sections: bool, combine_under_n_chars: int, new_after_n_chars: int) -> List[Element]
#end

#py_file_path
    unstructured-0.10.12/unstructured/chunking/title.py
#end

#local_function_in_py_file
    function1{
        fully qualified name: unstructured.chunking.title._split_elements_by_title_and_table
        summary: Split a list of elements into sections based on titles and tables, with options to combine sections under a certain character limit and create new sections after a certain character limit.
        signature: def _split_elements_by_title_and_table(elements: List[Element], multipage_sections: bool, combine_under_n_chars: int, new_after_n_chars: int) -> List[List[Element]]
    }

    function2{
        fully qualified name: unstructured.chunking.title._metadata_matches
        summary: Check if two metadata objects match, excluding extra metadata if specified.
        signature: def _metadata_matches(metadata1: ElementMetadata, metadata2: ElementMetadata, include_pages: bool) -> bool
    }

    function3{
        fully qualified name: unstructured.chunking.title._drop_extra_metadata
        summary: Drop specific keys from a metadata dictionary, including 'element_id' and 'type', and optionally 'page_number' if include_pages is False.
        signature: def _drop_extra_metadata(metadata_dict: dict, include_pages: bool) -> dict
    }
#end
"""

    User_Input3 = """#function_description
Partitions Microsoft PowerPoint Documents in .pptx format into its document elements.

Parameters
----------
filename
    A string defining the target filename path.
file
    A file-like object using "rb" mode --> open(filename, "rb").
include_page_breaks
    If True, includes a PageBreak element between slides
metadata_filename
    The filename to use for the metadata. Relevant because partition_ppt converts the
    document .pptx before partition. We want the original source filename in the
    metadata.
metadata_last_modified
    The last modified date for the document.


include_slide_notes
    If True, includes the slide notes as element
#end

#function_definition
def partition_pptx(filename: Optional[str], file: Optional[Union[IO[bytes], SpooledTemporaryFile]], include_page_breaks: bool, metadata_filename: Optional[str], include_metadata: bool, metadata_last_modified: Optional[str], include_slide_notes: bool) -> List[Element]
#end

#py_file_path
unstructured-0.10.12/unstructured/partition/pptx.py
#end

#Variables
OPENXML_SCHEMA_NAME = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
#end

#local_function_in_py_file
    function1{
        fully qualified name: unstructured.partition.pptx._order_shapes
        summary: Order the shapes from top to bottom and left to right.
        signature: def _order_shapes(shapes)
    }

    function2{
        fully qualified name: unstructured.partition.pptx._is_bulleted_paragraph
        summary: Check if a paragraph is bulleted by looking for a bullet character prefix.
        signature: def _is_bulleted_paragraph(paragraph) -> bool
    }
#end"""

    User_Input4 = """#function_description
    Args:
        boxes: (N, 4)
        indices: 递归过程中始终表示 box 在原始数据中的索引
        res: 保存输出结果
#end

#function_definition
def recursive_xy_cut(boxes: np.ndarray, indices: np.ndarray, res: List[int])
#end

#py_file_path
unstructured-0.10.12/unstructured/partition/utils/xycut.py
#end

#local_function_in_py_file
    function1{
        fully qualified name: unstructured.partition.utils.xycut.projection_by_bboxes
        summary: Calculate the projection histogram of a set of bounding boxes and output it in per-pixel form.
        signature: def projection_by_bboxes(boxes: np.ndarray, axis: int) -> np.ndarray
    }

    function2{
        fully qualified name: unstructured.partition.utils.xycut.split_projection_profile
        summary: Split a projection profile into groups based on a minimum value and minimum gap. Return the start and end indexes of each group.
        signature: def split_projection_profile(arr_values: np.ndarray, min_value: float, min_gap: float)
    }

    function3{
        fully qualified name: unstructured.partition.utils.xycut.points_to_bbox
        summary: Given a list of 8 points, calculate the bounding box coordinates.
        signature: def points_to_bbox(points)
    }

    function4{
        fully qualified name: unstructured.partition.utils.xycut.bbox2points
        summary: Convert a bounding box to a list of points.
        signature: def bbox2points(bbox)
    }

    function5{
        fully qualified name: unstructured.partition.utils.xycut.vis_polygon
        summary: Visualize a polygon on an image using OpenCV.
        signature: def vis_polygon(img, points, thickness, color)
    }

    function6{
        fully qualified name: unstructured.partition.utils.xycut.vis_points
        summary: Visualize points on an image with bounding boxes and text labels.
        signature: def vis_points(img: np.ndarray, points, texts: List[str], color) -> np.ndarray
    }

    function7{
        fully qualified name: unstructured.partition.utils.xycut.vis_polygons_with_index
        summary: Visualize polygons with corresponding indices on an image.
        signature: def vis_polygons_with_index(image, points)
    }
#end"""

    User_Input5 = """#function_description
    Partitions Microsoft Excel Documents in .xlsx format into its document elements.

    Parameters
    ----------
    filename
        A string defining the target filename path.
    file
        A file-like object using "rb" mode --> open(filename, "rb").
    include_metadata
        Determines whether or not metadata is included in the output.
    metadata_last_modified
        The day of the last modification
    include_header
        Determines whether or not header info info is included in text and medatada.text_as_html
#end

#function_definition
    def partition_xlsx(filename: Optional[str], file: Optional[Union[IO[bytes], SpooledTemporaryFile]], metadata_filename: Optional[str], include_metadata: bool, metadata_last_modified: Optional[str], include_header: bool) -> List[Element]
#end

#py_file_path
    unstructured-0.10.12/unstructured/partition/xlsx.py
#end"""

    # import pandas as pd
    # file_path = '../saved_results/repo_aware_SPL_5_result_three_shots.0.4_filtered.csv'
    # df = pd.read_csv(file_path)
    # last_row = df.iloc[-1]
    # user_input = eval(last_row['code_repo_aware_5_prompt'])
    # input_prompt = user_input[-1]['content']
    # input_prompt = input_prompt.replace('def is_list_item_tag(tag_elem: etree.Element) -> bool', 'def is_list_item_tag(tag_elem) -> bool')
    # user_input[-1] = {'role': 'user', 'content': input_prompt}
    # token_nums = LLMUtil.calculate_token_nums_for_prompt(user_input)
    # print('token nums: {}'.format(token_nums))
    #
    # print(LLMUtil.ask_chat_turbo(user_input))

    message = [{"role": "system"}]
    message[0]["content"] = system_prompt
    example1_user = {'role': 'user', 'content': example_1_input}
    example1_assistant = {'role': 'assistant', 'content': example_1_output}
    example2_user = {'role': 'user', 'content': example_2_input}
    example2_assistant = {'role': 'assistant', 'content': example_2_output}
    example3_user = {'role': 'user', 'content': example_3_input}
    example3_assistant = {'role': 'assistant', 'content': example_3_output}
    # example4_user = {'role': 'user', 'content': example_4_input}
    # example4_assistant = {'role': 'assistant', 'content': example_4_output}
    user = {'role': 'user', 'content': User_Input1}
    message.append(example1_user)
    message.append(example1_assistant)
    message.append(example2_user)
    message.append(example2_assistant)
    message.append(example3_user)
    message.append(example3_assistant)
    message.append(example3_user)
    message.append(example3_assistant)
    # message.append(example4_user)
    # message.append(example4_assistant)
    message.append(user)

    token_nums = LLMUtil.calculate_token_nums_for_prompt(message)
    print('token nums: {}'.format(token_nums))

    print(LLMUtil.ask_chat_turbo(message))
