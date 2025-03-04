import PyPDF2

def pdf_parser_by_pypdf2(pdf_file):
    '''
    This function is used to parse pdf file using PyPDF2 library.
    :param pdf_file: the path of pdf file
    '''
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text