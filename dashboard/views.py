from django.shortcuts import render
import calendar
from datetime import datetime
from django.contrib.auth.decorators import login_required , permission_required
from django.urls.base import translate_url
from requests.api import head
from pypi_simple import PyPISimple 
from dashboard.forms import Library_Form 
from dashboard.models import  Library
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
import vulners  
from django.core.mail import send_mail
import random
import pandas as pd
import requests
import json
from io import StringIO
import base64

from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
from time import sleep



@login_required
def dashboard_index(request):
    form = None
    url = "dashboard/index.html" 
    if request.method == 'POST':
        form = Library_Form(request.POST, request.FILES)
        if(form.is_valid()):
            data = form.save(commit=False)
        
            
            data.created_at = timezone.now()
            data.updated_at = timezone.now()
            data.created_by = request.user.id   
            data.save()
            messages.add_message(request, messages.INFO, 'File saved')
            return HttpResponseRedirect(reverse('dashboard:libraries'))
     
    else:
        form = Library_Form()
    
    context = {
         
        'title': "Upload Project  DataSet",
        'form':form
        
    } 
     
    return render(request , url , context)






def dashboard_libraries(request):
    libraries = Library.objects.all().order_by('-id')
    url = "dashboard/list_librabries.html" 
    # send_mail(
    #     'Payment',
    #     'find payment.',
    #     'kidkudzy@gmail.com',
    #     ['kmakufa@outlook.com', 'promiseksystems@gmail.com'],
    #     fail_silently=False,
    # )
    context = {
        
        'title': "DATA SETS",
        'libraries':libraries
        
    } 


    return render(request , url , context)



@login_required
def library_scan(request ,lib_id=None):
    library = Library.objects.filter(id=lib_id).order_by('-id')
    # f = open(library[0].library_list.path, "r")
    # print("------------------")

    # lines = f.readlines()


    
    # # for line in lines:
    # #     print(line)
    # # print("------------------")
    # f.close()

    # _________________________________
    df = pd.read_csv(library[0].library_list.path, delimiter=',')
    tuples = [tuple(x) for x in df.values]

   
    context = {
        "item":library[0], 
        "lines":tuples,
    }
    return render(request, 'dashboard/library_view.html', context)
    
    
@login_required
def process_data(request ,lib_id=None):
    library = Library.objects.get(id=lib_id)
    title = ""
    
    data = []
    age = []
    sales = []

    df1_age = []
    df1_sales = []

    df2_age = []
    df2_sales = []
    pie_data = []
    sleep(5)
    if library.data_mode  == "csv":
        filename = library.library_list

        df = pd.read_csv(filename.path, delimiter=',' )
        # 1 table description
        table_description = df.describe().to_html(justify='left').replace('<table border="1" class="dataframe">','<table class="table table-bordered dt-responsive nowrap" style="border-collapse: collapse; border-spacing: 0; width: 100%;">')
        print(df.describe().values[0].tolist())
        for item in df.describe().values.tolist()[:-1] :
            
            pie_data.append(item[0])
        print(pie_data)
        # 2 plot table data
        age = df['Age'].values.tolist()
        sales = df['Sales'].values.tolist()

        # kmeans

        km = KMeans(n_clusters=3)
        y_predicted = km.fit_predict(df[['Age','Sales']])
        df['cluster'] = y_predicted
        
        df1 = df[df.cluster==0]
        df2 = df[df.cluster==1]

        df1_age = df1['Age'].values.tolist()
        df1_sales = df1['Sales'].values.tolist()

        df2_age = df2['Age'].values.tolist()
        df2_sales = df2['Sales'].values.tolist()

        # table for clusters

        table_clusters = df.to_html(justify='left').replace('<table border="1" class="dataframe">','<table id="datatable" class="table table-bordered dt-responsive nowrap" style="border-collapse: collapse; border-spacing: 0; width: 100%;">')



       
        
        title = "Graphs for " +filename.path

    if library.data_mode  == "api":
        response = requests.get('https://api.openweathermap.org/data/2.5/forecast?id=890299&units=metric&appid=9b63dca2ced4e2d6ad7f4f01698d7a45')
        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
            result = response.json()
            data = result['list']


        else:
            print("error loading info")
        title = "Pulling 5 Day data focused for Harare before Hadoop implementation   "
    context = {
        'table_description':table_description ,
        'table_clusters':table_clusters,
        'age':age,
        'sales':sales,
        'df1_age':df1_age,
        'df1_sales':df1_sales,
        'df2_age':df2_age,
        'df2_sales':df2_sales,
        "item":library,
        "data":data ,
        "title":title,
        'pie_data':pie_data
       
    }
    return render(request, "dashboard/api_process.html", context)
@login_required
def delete_librabry(request ,librabry_id=None):
    library = Library.objects.get(pk=librabry_id)
    library.delete()
    messages.add_message(request, messages.INFO, 'Library deleted')
    return HttpResponseRedirect('/dashboard/libraries')
