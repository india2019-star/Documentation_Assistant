individual_summary_template=r'''Write a short and CONCISE SUMMARY of the following:
TEXT: `{text}`
CONCISE SUMMARY:
'''

combined_summary_template=r'''The following is a set of summaries:
{docs}
Take these and distill it into a final, {summary_type} summary
of the main themes. You must list all the import points in bullet point format.
Add a title to your summary.
START your summary with an INTRODUCTION that gives an overview of the summary. If possible try to end with
a CONCLUSION.
'''


