from django.shortcuts import render,redirect
#from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
import pandas as pd
import numpy as np
from io import StringIO
import seaborn as sns
import matplotlib.pyplot as plt
import time
import os
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import math

def show(request):
    
    if request.method=='POST':
        file=request.FILES.get('csvfile')
        print(file)
        #a=pd.read_csv(file)
        #a.to_csv('analysis\HRDataset1.csv')
    
    class A:
        def __init__(self,df):
            self.df = df
            pass
       
        def head(self):
            df = self.df.head(5).to_html()
            return df
       
        def describe(self):
            df = self.df.describe().to_html()
            return df
       
        def process_content_info(self):
            content_info = StringIO()
            self.df.info(buf=content_info)
            str_ = content_info.getvalue()
    
            lines = str_.split("\n")
            table = StringIO("\n".join(lines[3:-3]))
            datatypes = pd.read_csv(table, delim_whitespace=True,
                           names=[" ","count", "__","_","dtype"])
            datatypes.set_index(" ", inplace=True)
    
            #info = "\n".join(lines[0:2] + lines[-2:-1])
            df = datatypes.to_html()
            return df
       
        
        def plotnull(self):
            df = self.df
            d = []
    
            for col in df:
                null_values = df[col].isnull().sum()
                if null_values !=0:
                    d.append([col,null_values])
    
            d.sort(key=lambda k:k[1],reverse=True)
            df_null = pd.DataFrame(d,columns=['col','null'])
            
            fig = px.bar(x=df_null.col, y=df_null.null)
            plot=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
            return plot
        # functions below needs to be called mandatorily while instantiating class for background images
    
        def countplotbg(self):
            df = self.df
            df_cat = df.select_dtypes(include = ['O'])
            col = []
            for i in df_cat:
                if len(df_cat[i].unique()) <=10:
                    col.append(i)
    
            df_cat = df_cat[col]
            #lets have a look at their distribution 
            fig ,axes = plt.subplots(round(len(df_cat.columns)/3),3,figsize=(15,20))
    
            for i, ax in enumerate(fig.axes):
                if i < len(df_cat.columns):
                    ax.set_xticklabels(ax.xaxis.get_majorticklabels(),rotation=45)
                    sns.countplot(x=df_cat.columns[i],data=df_cat,ax=ax)
    
            fig.tight_layout()# to have proper padding
            plt.savefig('analysis\static\images\countplotbg.png')
    #         plt.show()
            
        def correlation(self): #for background image
            df = self.df
            df_num = df.select_dtypes(include=['float','int64'])
            if len(df_num.columns)> 18:
                df_num = df_num.iloc[:,:18]
            plt.figure(figsize=(15,15))
            plt.xticks(rotation=45)
            corr = df.corr()
            sns.heatmap(corr,annot=True)
            plt.savefig('analysis\static\images\correlatedbg.png')
    
    if request.user.is_authenticated:         
        df = pd.read_csv(r'analysis\HRDataset.csv')
        ob = A(df)
        head1=ob.head()
        describe1=ob.describe()
        process_content_info1=ob.process_content_info()
        pltnull=ob.plotnull()
        
        ob.countplotbg()
        ob.correlation()
        
        dict={"head1":head1,"describe1":describe1,"process_content_info1":process_content_info1,"plot":pltnull}
        return render(request,'show.html',dict)
    else:
        messages.error(request,"Login your account to analyse your data")
        return redirect('login')


def countplot(request):
    
    class Countplot: # total six images are saved as six catagorical attr    
    #attr list ->  catagorical ['Position', 'Sex', 'EmploymentStatus', 'Department', 'RecruitmentSource', 'PerformanceScore']
        def __init__(self):
            self.df = pd.read_csv(r'analysis\HRDataset.csv')
            pass 
        
        def plot(self):
            df_cat = self.df.select_dtypes(include=['O'])
            attributes=df_cat.columns
        
            for attr in df_cat.columns:
                plt.figure(figsize=(16,14))
                sns.countplot(attr,data=df_cat)
                plt.xticks(rotation='45')
    
                time.sleep(0.5)
                plt.savefig(f'analysis\static\images\countplot\{attr}Countplot.png')
            return attributes
            
    ob = Countplot()
    attributes=ob.plot()
    images=os.listdir('analysis\static\images\countplot')
    return render(request,'countplot.html',{"attributes":attributes,"images":images})

def correlationplot(request):
    attr="Salary"
    df = pd.read_csv(r'analysis\HRDataset.csv')
    df_num = df.select_dtypes(include=['float','int64'])
    strongly_corr = df_num.corr()[attr][:]
    strongly_corr  = strongly_corr[abs(strongly_corr)>0.5].sort_values(ascending=False) # since series dont have sort()
    print('there are', len(strongly_corr)-1,' strongly correlated variables ')
    topcorrelation = [i for i in strongly_corr.index if i!=attr]
 
    return render(request,'correlationplot.html',{"topcorrelation":topcorrelation})

def return_insights():
    df=pd.read_csv(r'analysis\HRDataset.csv')
    
    dict1={}
    dict1["rows"]=df.shape[0]
    dict1["columns"]=df.shape[1]
    
    dict1["numerical"] = df.select_dtypes(include = ['float','int64']).shape[1]
    dict1["catagorical"] = df.select_dtypes(include = ['O']).shape[1]
    
    c,m,s= 0,0,''

    col = df.columns
    null_values = df[col].isnull().sum()
    for i ,j in zip(null_values,null_values.index):
        if i>0:
            c +=1
        if i>m:
            m,s= i,j
    s = s.upper()
    
    dict1["nullvalue"]=c
    dict1["maxnull"]= f'Attribute {s} with maximum NULL values ie {m}'
    
    cor_matrix = df.corr().abs()
    upper_tri = cor_matrix.where(np.triu(np.ones(cor_matrix.shape),k=1).astype(np.bool))
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > 0.65)]
    dict1["extra"] = f'Dataset consist of {len(to_drop)} highly correlated feautres ie {to_drop}'
    
    
    return dict1

def insights(request):
    dict=return_insights()
    return render(request,'insights.html',dict)


	
def allhistogramplot(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	attr = list(df.select_dtypes(include=['float','int64']).columns)
	attr.remove('EmpID')
	fig1 = make_subplots(rows=4, cols=1)
	j=1
	for i in attr:
		fig1.add_trace(go.Histogram(x=df[i]), row=j, col=1)
		fig = px.histogram(df,x=df[i],height=600)
		dict1[i]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
		j=j+1
	
	fig1.update_layout(height=1700, showlegend=False)
	#fig.update_yaxes(tick0=25, dtick=25)

	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	return render(request,'plot1.html',{"dict1":dict1,"plot":plot,"attributes":attr,"plot_name":"Histogram Plot"})
	
def allbarplot(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	attrx = list(df.select_dtypes(include = ['O']).columns)
	attry = list(df.select_dtypes(include=['float','int64']).columns)
	attry.remove('EmpID')
	rows=len(attrx)
	cols=len(attry)
	fig1 = make_subplots(rows=(rows*cols)//2, cols=2,subplot_titles=["bar plot between "+i+" and "+j for i in attrx for j in  attry])
	r=0
	c=1
	for i in attrx:
		for j in attry:
			fig1.add_trace(go.Bar(x=df[i], y=df[j]),row=c,col=(r%2)+1)
			fig = px.bar(df, x=i, y=j)
			dict1[i+"_"+j]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
			r+=1
			if(r%2==0):
				c+=1

	fig1.update_layout(height=8500, showlegend=False)
	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	
	return render(request,'plot2.html',{"dict1":dict1,"plot":plot,"attributes_x":attrx,"attributes_y":attry,"plot_name":"Bar Plot"})


def allboxplot(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	attrx = list(df.select_dtypes(include = ['O']).columns)
	attry = list(df.select_dtypes(include=['float','int64']).columns)
	attry.remove('EmpID')
	rows=len(attrx)
	cols=len(attry)
	fig1 = make_subplots(rows=(rows*cols)//2, cols=2,subplot_titles=["box plot between "+i+" and "+j for i in attrx for j in  attry])
	r=0
	c=1
	for i in attrx:
		for j in attry:
			fig1.add_trace(go.Box(x=df[i], y=df[j]),row=c,col=(r%2)+1)
			fig = px.box(df, x=i, y=j)
			fig.update_layout(height=600, showlegend=False)
			dict1[i+"_"+j]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
			r+=1
			if(r%2==0):
				c+=1

	fig1.update_layout(height=8500, showlegend=False)
	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	
	return render(request,'plot2.html',{"dict1":dict1,"plot":plot,"attributes_x":attrx,"attributes_y":attry,"plot_name":"Box Plot"})


def allpiechart(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	attrx = list(df.select_dtypes(include = ['O']).columns)
	attry = list(df.select_dtypes(include=['float','int64']).columns)
	attry.remove('EmpID')
	
	rows=len(attrx)
	cols=len(attry)
	domain=[[{"type":"domain"},{"type":"domain"}] for i in range((rows*cols)//2)]

	fig1 = make_subplots(rows=(rows*cols)//2, cols=2,specs=domain,subplot_titles=["Pie chart between "+i+" and "+j for i in attrx for j in  attry])
	r=0
	c=1
	for i in attrx:
		for j in attry:
			fig1.add_trace(go.Pie(values=df[j],labels=df[i]),row=c,col=(r%2)+1)
			fig = px.pie(df, values=j, names=i,height=600,template="plotly_dark")
			dict1[i+"_"+j]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
			r+=1
			if(r%2==0):
				c+=1
	
	fig1.update_layout(height=6500, showlegend=False)
	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	
	return render(request,'plot2.html',{"dict1":dict1,"plot":plot,"attributes_x":attrx,"attributes_y":attry,"plot_name":"Pie Chart"})


def allscatterplot(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	
	attrx = list(df.select_dtypes(include=['float','int64']).columns)
	attry = list(df.select_dtypes(include=['float','int64']).columns)
	attry.remove('EmpID')
	attrx.remove('EmpID')

	rows=len(attrx)
	cols=len(attry)
	fig1 = make_subplots(rows=(rows*cols)//2, cols=2,subplot_titles=["Scatter plot between "+i+" and "+j for i in attrx for j in  attry])
	r=0
	c=1
	for i in attrx:
		for j in attry:
			fig1.add_trace(go.Scatter(x=df[i], y=df[j],mode="markers"),row=c,col=(r%2)+1)
			fig = px.scatter(df, x=i, y=j)
			dict1[i+"_"+j]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
			r+=1
			if(r%2==0):
				c+=1

	fig1.update_layout(height=6500, showlegend=False)
	
	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	return render(request,'plot2.html',{"dict1":dict1,"plot":plot,"attributes_x":attrx,"attributes_y":attry,"plot_name":"Scatter Plot"})


	
def alllineplot(request):
	df = pd.read_csv(r'analysis\HRDataset.csv')
	dict1={}
	
	attrx = list(df.select_dtypes(include=['float','int64']).columns)
	attry = list(df.select_dtypes(include=['float','int64']).columns)
	attry.remove('EmpID')
	attrx.remove('EmpID')

	rows=len(attrx)
	cols=len(attry)
	fig1 = make_subplots(rows=(rows*cols)//2, cols=2,subplot_titles=["Line plot between "+i+" and "+j for i in attrx for j in  attry])
	r=0
	c=1
	for i in attrx:
		for j in attry:
			fig1.add_trace(go.Scatter(x=df[i], y=df[j]),row=c,col=(r%2)+1)
			fig = px.line(df,x=i,y=j,height=600)
			dict1[i+"_"+j]=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
			r+=1
			if(r%2==0):
				c+=1

	fig1.update_layout(height=6500, showlegend=False)
	plot=plotly.io.to_html(fig1, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	return render(request,'plot2.html',{"dict1":dict1,"plot":plot,"attributes_x":attrx,"attributes_y":attry,"plot_name":"Line Plot"})


def insights_for_report():
    dict1=return_insights()
    x=['Rows','Columns','Numerical Values','Catagorical Values','Attributes with Null Values']
    y=[dict1["rows"],dict1["columns"],dict1["numerical"],dict1["catagorical"],dict1["nullvalue"]]
    return x,y


def report(request):
    plot="<div style=\"height:200px;color:red;\" class=\"container\"><h1 align=\"center\">You didn't visit any plot</h1><h1 align=\"center\">Please visit some plots to generate report</h1></div>"
    if request.method == 'POST':
        ab=request.POST.get('allitem')
        if(len(ab)>2 or ab!="{}"):           
            dictionary = json.loads(ab)
            no_of_rows=0
            l=[]
            plotes=[]
            titles=[]
            l1=[]
            count=0
            l.append([{"colspan": 2}, None])
            titles.append("Some Basic Insights Of Your Data-")
            for key,value in dictionary.items():
                dictionary[key]=json.loads(dictionary[key])
                r=len(dictionary[key])
                for i in range(r):
                    if key=="Pie":
                        x="Pie Chart between "+dictionary[key][i][0]+" and "+dictionary[key][i][1]
                        if x not in titles:
                            titles.append(x)
                            dictionary[key][i].insert(0,key)
                            plotes.append(dictionary[key][i])
                            l1.append({"type":"pie"})
                            count+=1
                    else:
                        if(len(dictionary[key][i])==1):
                           x=key+" Plot of "+dictionary[key][i][0]
                        else:
                            x=key+" Plot between "+dictionary[key][i][0]+" and "+dictionary[key][i][1]
                        if x not in titles:
                            titles.append(x)
                            dictionary[key][i].insert(0,key)
                            plotes.append(dictionary[key][i])
                            l1.append({"type":"xy"})
                            count+=1
                    if(count==2):
                        l.append(l1)
                        l1=[]
                        count=0
            
            if(count==1):
                l1.append({"type":"xy"})
                l.append(l1)
            
            len1=len(plotes)
            no_of_rows=math.ceil(len1/2)
            df = pd.read_csv(r'analysis\HRDataset.csv')
            fig=make_subplots(rows=no_of_rows+1,vertical_spacing=0.09,cols=2,specs=l,subplot_titles=titles)
            
            x,y=insights_for_report()
            fig.add_trace(go.Bar(x=x, y=y),row=1,col=1)
            
            i=0        
            r=0
            c=2
            while(i<len1):
                if plotes[i][0]=="Scatter":
                    fig.add_trace(go.Scatter(x=df[plotes[i][1]], y=df[plotes[i][2]],mode="markers"),row=c,col=(r%2)+1)
                elif plotes[i][0]=="Line":
                    fig.add_trace(go.Scatter(x=df[plotes[i][1]], y=df[plotes[i][2]]),row=c,col=(r%2)+1)
                elif plotes[i][0]=="Pie":
                    fig.add_trace(go.Pie(values=df[plotes[i][2]],labels=df[plotes[i][1]]),row=c,col=(r%2)+1)
                elif plotes[i][0]=="Box":
                    fig.add_trace(go.Box(x=df[plotes[i][1]], y=df[plotes[i][2]]),row=c,col=(r%2)+1)
                elif plotes[i][0]=="Bar":
                    fig.add_trace(go.Bar(x=df[plotes[i][1]], y=df[plotes[i][2]]),row=c,col=(r%2)+1)
                elif plotes[i][0]=="Histogram":
                    fig.add_trace(go.Histogram(x=df[plotes[i][1]]), row=c, col=(r%2)+1)
				
                r+=1
                if(r%2==0):
                    c+=1
                i+=1
            
            fig.update_layout(height=3000,showlegend=False,title_text="Plotes you visited",title_font_size=30)
            plot=plotly.io.to_html(fig, config=None, auto_play=True, include_plotlyjs=True, include_mathjax=False, post_script=None, full_html=True, animation_opts=None, default_width='100%', default_height='100%', validate=True)
	
    return render(request, 'report.html',{"plot":plot})