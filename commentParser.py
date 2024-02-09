import re

# Function to extract attachment references from comment body
def extract_attachment_references(comment_body):
    # Regular expression pattern to match attachment references
    pattern = r'!(.*?)\|thumbnail!'
    attachment_references = re.findall(pattern, comment_body)
    return attachment_references

def clean_comment(comment):
    # Remove [~ and ] from the mention

    # line_breaks = re.sub(r'\n', '<br>', comment)
    line_breaks = comment
    cleaned_comment = re.sub(r'\[~(.*?)\]', '', line_breaks)
    
    # Remove everything between ! and |thumbnail! and also remove |thumbnail!
    cleaned_comment = re.sub(r'!(.*?)\|thumbnail!', '', cleaned_comment)


    
    return cleaned_comment

    