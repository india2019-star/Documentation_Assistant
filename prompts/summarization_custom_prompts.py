individual_summary_template=r'''Write a short and CONCISE SUMMARY of the following:
TEXT: `{text}`
CONCISE SUMMARY:
'''

combined_summary_template=r'''Write a {summary_type} summary of the  following text that covers all key points.
You must list all the import points in bullet point format.
Add a title to your summary.
START your summary with an INTRODUCTION PARAGRAPH that gives an overview of the summary. If possible try to end with
a CONCLUSION PARAGRAPH.
TEXT: `{text}`
'''