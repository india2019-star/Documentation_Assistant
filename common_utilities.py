def format_source_documents(context):
        source_docs = set([item.metadata['source']  for item in context])
        if not source_docs:
            return ""
        source_docs_list = list(source_docs)
        source_docs_list.sort()
        source_docs_in_string_format = "Sources:\n"
        for index, item in enumerate(source_docs_list):
            item = str(item).replace("\\","/")
            item = str(item).replace("G:/","https://")
        source_docs_in_string_format += f"{index + 1}. {item}\n"
        return source_docs_in_string_format