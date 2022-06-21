#  created by - raju

from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.contrib.auth import authenticate,login
#from django.contrib.auth.forms import UserCreationForm

from .forms import resumesFroms, CreateUserForm
from .model import resumes

import spacy
import pickle
import random
import sys
import fitz
import csv
from pyresparser import ResumeParser

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        USER =authenticate(request , username= username, password=password)

        if USER is not None:
            login(request, USER)
            return redirect('upload_resume')
    return render(request, 'login.html')


def register_user(request):
    register_form = CreateUserForm()
    if request.method == 'POST':
        register_form = CreateUserForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return redirect('login_user')
    
    
    context={'form':register_form}
    return render(request,'register.html', context)



def upload_resume(request):
    if request.method == 'POST':
        form = resumesFroms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('resume_list')
    else:
        form = resumesFroms()
    return render(request, 'upload.html',{
        'form': form
    } )
   
def resume_list(request):
    resume = resumes.objects.all()
    for r in resume:
        resumepath = r.respdf.path
    

    # LOADING DATA FOR TRAINING 

    train_data = pickle.load(open(r'D:\CODE_STORAGE\PYTHON\PYCODES\DjangoProject\mySite\media\traindata\train_data.pkl','rb'))
    #print(train_data[0])


    #########################################  TRAINING THE MODEL  #############################################

    nlp = spacy.blank('en')

    def train_model(train_data):

        # create the built-in pipeline components and add them to the pipeline
        # nlp.create_pipe works for built-ins that are registered with spaCy  
        
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner, last = True) 

        # add labels

        for _, annotation in train_data:
            for ent in annotation['entities']:
                ner.add_label(ent[2])

        # get names of other pipes to disable them during training
        
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        with nlp.disable_pipes(*other_pipes):  # only train NER

            # reset and initialize the weights randomly – but only if we're
            # training a new model
            
            optimizer = nlp.begin_training()
            for itn in range(10):
                print("Starting iteration "+ str(itn))
                random.shuffle(train_data)
                losses = {}
                index = 0
            
                for text, annotation in train_data:
                    #print(index)
                    try:
                        nlp.update(
                            [text],  # batch of texts
                            [annotation],  # batch of annotations
                            drop=0.2,  # dropout - make it harder to memorise data
                            sgd = optimizer,
                            losses=losses,)
                    except Exception as e:
                        pass
                #print('losses' + losses)  


    # RUNNING THE MODEL AND SAVING THE MODEL 
        
    #train_model(train_data)      
    #nlp.to_disk('nlp_model_1')


    #################################   READING THE CV.PDF CONVERTING TO TEXT   #############################

    doc = fitz.open(resumepath)
    text =''
    for page in doc:
        text = text + str(page.getText())
    #print(text)
    tx = " ".join(text.split('\n'))
    #print(len(tx))


    ###################################  LOADING THE TRAINED MODEL  ##########################################

    nlp_train_model = spacy.load(r'D:\CODE_STORAGE\PYTHON\PYCODES\DjangoProject\mySite\media\nlp_model_1')
    doc1 = nlp_train_model(tx)



    ###################################  LOADING PRE-TRAINED MODEL  ###########################333#############

    from nltk.tokenize import word_tokenize #for word tokenization
    from nltk.corpus import stopwords   #for stopwords
    from spacy.matcher import Matcher   #for pattern matching


    nlp = spacy.load('en_core_web_sm')
    doc2 = nlp(tx)

    #Tokenizing the resume text
    tokens = word_tokenize(tx)
    # list that contains punctuation we wish to clean.
    punctuations = ['(',')',';',':','[',']',',']
    #list of words that don't hold much value as keywords.
    stop_words = stopwords.words('english')
    # returns a list of words that are NOT IN stop_words and NOT IN punctuations.
    keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
    #print(keywords)



    #########################################   NAME EXTTRACTION  ############################################


    #for ent in doc1.ents:
        #print(ent.label_)
        #print(f'{ent.label_:{20}}- {ent.text}')


    NAMES=[]
    for ent in doc1.ents:
        if ent.label_=='Name':
            NAMES.append(ent.text)

    data = ResumeParser(resumepath).get_extracted_data() #pre-trained resume parser
    NAMES.append(data.get("name"))
    #print(data.items())
    #for i in data.items():
    #print(i)

    #initialize matcher with a vocab
    matcher = Matcher(nlp.vocab)
    N=[]

    for i in NAMES:
        nlp_text = nlp(i)

        #First name and Last name are always Proper Nouns#
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        matcher.add('NAME', None, pattern) 
        matches = matcher(nlp_text)
        
        for match_id, start, end in matches:
            span = nlp_text[start:end]
            N.append(span.text)
    if len(N)==0:
        N.append("none")
    name = (list(dict.fromkeys(N))[0]).upper()
    #print(name)

    ########################################  SKILLS EXTRACTION  ##############################################

    SKILLS=[]

    #Checking for one-grams (example: python)
    for ent in doc1.ents:
        if ent.label_=='Skills':
            SKILLS.append(ent.text)

    x = data.get("skills")
    #print(x)
    for i in x:
        SKILLS.append(i)

    for i in keywords:
        SKILLS.append(i)

    #Checking for bi-grams and tri-grams (example: machine learning)
    for t in doc2.noun_chunks:
        t1 = t.text.lower().strip()
        SKILLS.append(t1.upper())
    #print(SKILLS)    

    #Opening .csv file of technical skills
    with open(r'D:\CODE_STORAGE\PYTHON\PYCODES\DjangoProject\mySite\media\Skills\techskill.csv') as f:
        input_data = []
        for row in csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE):
            input_data += row


    TECH_SKILLS=[]

    for i in SKILLS:
        for y in input_data:
            if y.upper() == i.upper():
                TECH_SKILLS.append(i.upper())

    #For empty skill list
    if len(TECH_SKILLS) == 0: 
        for i in x:
            TECH_SKILLS.append(i)
            
    #print((list(dict.fromkeys(TECH_SKILLS))))
    #print(f'{"NAME":{20}}- {name}')
    #print(f'{"EMAIL":{20}}- {data.get("email")}')
    #print(f'{"PHONE NUMBER":{20}}- {data.get("mobile_number")}')
    #print(f'{"SKILLS":{20}}- {list(dict.fromkeys(TECH_SKILLS))}')
    EMAIL = data.get("email")
    ph = data.get("mobile_number")
    sk = list(dict.fromkeys(TECH_SKILLS))

    context={'name':name , 'email':EMAIL , 'mobile_no':ph, 'skills':sk }

    return render(request,'resume_list.html',context)

def about_us(request):
    return render(request,'about.html')


      