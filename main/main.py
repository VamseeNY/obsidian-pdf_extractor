from bs4 import BeautifulSoup
import streamlit as st 
import ast 
from fpdf import FPDF
from io import StringIO

st.set_page_config(layout="wide",page_title="Obsidian Highlights and Annotations extractor")

header=st.container()

def pdf(title,bindings):
    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font('Arial','I',8)
            self.set_text_color(128)
            self.cell(0,10,str(self.page_no()),align='C')

    pdf = PDF('P','mm','A4')
    pdf.add_page()
    pdf.set_font("times",'', size = 15)
    pdf.set_auto_page_break(auto=True,margin=10)
    pdf.cell(0,20,title,ln=True,align='C')

    for i,j in bindings.items():
        if j!="":
            pdf.multi_cell(0,10,i)
            pdf.set_font('times','I',12)
            pdf.ln(1)
            pdf.multi_cell(0,10,"Annotation: "+j)
            pdf.ln(5)
            pdf.set_font("times",'', size = 15)
        else:
            pdf.multi_cell(0,7,i)
            pdf.ln(5)

    data=bytes(pdf.output(dest='S'))
    return(data)


def mkd(title,bindings):
    data=''
    for i,j in bindings.items():
        if j!="":
            data+="* "+i+"\n"
            data+=("\t"+f"***<font color='lightgreen'>{j}</font>***\n")
        else:
            data+="* "+i+"\n"

    return(bytes(data,encoding='utf8'))
    

def pre_proc(r,nm,choice):
    text = ''.join(BeautifulSoup(r).findAll(text=True))
    a=text.split("\n")
    di=[]
    for i in a:
        if "created" in i :
            di.append(i[1:])
    di=[ast.literal_eval(i) for i in di]
    title=di[0]['document']['title']
    if title=='':
        title=nm
    bindings={}
    for i in di:
        bindings[i['target'][0]['selector'][1]['exact']]=i['text'] if "text" in list(i.keys()) else ""
    methods={'.pdf':pdf,'.md':mkd}

    return(methods[choice](title,bindings))


with header:
    bytes_data=""
    txt, itms,inp = st.columns([1,1,1])
    with txt:
        st.header("Obsidian PDF Highlights and Annotations extractor")
        st.subheader("Export your highlights and annotations created using the Obsidian Plugin- Annotator to a PDF or markdown file.")
        st.subheader("Code")
        st.write("The source code of this webpage is available at: https://github.com/VamseeNY/obsidian-pdf_extractor.")

    with itms:
        string_data,name="",""
        st.subheader("Steps:")

        uploaded_file = st.file_uploader("Upload markdown file",type=['md'])
        form=st.selectbox('Select output format',('.pdf','.md'))

        if uploaded_file is not None:
            name=uploaded_file.name
            stringobj = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringobj.read()
            bytes_data = uploaded_file.getvalue()

            outputdata=pre_proc(string_data,name,form)
            st.download_button(label='Download: Extracted-'+name.split(".")[0]+form,data=outputdata,file_name="Extracted-"+name.split(".")[0]+form,disabled=uploaded_file is None)

    with inp:
        with st.expander("View input data"):
            st.write(bytes_data)
