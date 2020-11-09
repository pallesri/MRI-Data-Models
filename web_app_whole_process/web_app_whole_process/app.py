# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 09:54:43 2020

@author: Qinxin Xu
"""
# from flask import Flask
import json
import os
#import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from consts import SAMPLE, split_by_header, pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, readable_pdf_to_txt

# os.chdir(r'/Users/xuqinxin/PycharmProjects/web_app/')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# my_server = Flask('my_mri')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
        'background': '#111111',
        'text': '#7FDBFF'
        }

app.layout = html.Div(children=[
    html.H1(children='Medical Record Insights',
            style={
                    'textAlign':'center'
                    # 'colors': colors['text']
                    }
            ),
    
    html.Div([
            html.Div(
                dcc.RadioItems(
                    id='trans-type',
                    options=[{'label': i, 'value': i} for i in ['Select a sample file in dropdown', 'Upload other files']],
                    value='txt',
                    labelStyle={'display': 'list-item', 'margin': 10}),
                style={'width': '20%'}),
            
            html.Div(
                [
                    dcc.Dropdown(
                        id='doc-dropdown',
                        options=[{'label': i, 'value': i} for i in SAMPLE],
                        value = 'pdf',
                        placeholder="Select a file in fine samples",
                        style = {'textAlign':'center'}
                    ),
            
                    html.Div(
                            dcc.Upload(
                                id='upload-data',
                                children = html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select a file')]),
                                style={
                                        'lineHeight': '35px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                },
                                multiple = False),
                        style={'width':'100%', 'margin-top':10})
                ],
                style={'width': '80%'})
        ],
        style={'display':'flex', 'width': '48%'}),
    
    
    html.Div(
        [
            html.Div(
                [
                    html.H3(children='PDF',
                            style={'height': '5%'}),
                    html.Iframe(
                        id='pdf_view',
                        style={'width': '100%', 'height': '95%'})
                ],
                style={'width':'48%', 'height':800}
            ),

            html.Div(
                [
                    html.H3(children='RAW TEXT',
                            style={'height': '5%'}),
                    html.Pre(
                        id = 'txt_view',
                        style= {'width': '100%','height': '95%', 'display': 'inline-block',
                                'overflow': 'scroll'})
                ],
                style={'width': '48%', 'height': 800, 'margin-left': 10}
            )
        ],
        style={'display': 'flex', 'margin': 10}
    ),

    html.Div(
        [
            html.Div(
                [
                    html.H3(children='SEGMENTED TEXT',
                            style={'height': '5%'}),
                    html.Pre(
                        id = 'test-upload',
                        style={'width': '100%', 'height': '95%',
                            'overflow': 'scroll', 'margin':'1px'})
                ],
                style={'width':'48%', 'height': 800}
            ),

            html.Div(
                [
                    html.H3(children='NER ENTITY',
                            style={'height': '5%'}),
                    html.Div(
                        [
                            html.Div(
                                dcc.Tabs(
                                    id = 'ner-tabs',
                                    value='tab-4',
                                    children=[
                                        dcc.Tab(label='Disease&Symptom', value='tab-4'),
                                        dcc.Tab(label='Drug&Chem', value='tab-2'),
                                        dcc.Tab(label='Anatomy', value='tab-1'),
                                        dcc.Tab(label='Procedure', value='tab-3'),
                                        dcc.Tab(label='Demo_Date', value='tab-5')
                                    ]),
                                style={'height':'8%'}),

                            html.Div(
                                id ='ner_view',
                                style={'height': '92%'})
                        ],
                        style={'width': '100%', 'height': '95%'}
                    )
                ],
                style={'width': '48%', 'height': 800, 'margin-left':10})
        ],
        style={'display': 'flex', 'margin-top': 40, 'margin-left': 10, 'margin-right': 10}
    ),

    html.Div(id='intermediate-value',
             style={'display': 'none'})
    
    ])
              

#def parse_contents(contents, filename):
#    content_type, content_string = contents.split(',')
#    
##    try:
##        if 'txt' in filename:
##            decoded = base64.b64decode(content_string)
#    data = base64.b64decode(content_string).decode('latin-1')
##    except Exception as e:
##        print(e)
##        return html.Div(['Error: Not txt file.'])
##    
#    return data
    


#@app.callback(Output('pdf_view', 'src'), 
#              [Input('doc_dropdown', 'value')])
#def update_pdf(file):
#    if file != 'pdf':
#        return 'static/'+file+'.pdf'
#    else:
#        return 'static/pdf.png'


@app.callback(Output('pdf_view', 'src'),
               [Input('doc-dropdown', 'value'),
                Input('upload-data', 'contents'),
                Input('trans-type', 'value')],
              [State('upload-data', 'filename')])
def update_pdf(value, contents, folder, filename):
    if folder == 'Select a sample file in dropdown' and value != 'pdf':
        return r'/static/readable_sample/'+ value + '.pdf'
    elif folder == 'Upload other files' and contents is not None:
        return r'/static/other/'+ filename[:-4] + '.pdf'
    else:
        return r'/static/pdf.png'


@app.callback(Output('intermediate-value', 'children'),
              [Input('doc-dropdown', 'value'),
                Input('upload-data', 'contents'),
                Input('trans-type', 'value')],
               [State('upload-data', 'filename')])
def get_text(value, contents, folder, filename):
    if folder == 'Select a sample file in dropdown' and value != 'pdf':
        tmp = readable_pdf_to_txt(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Code\web_app_whole_process\web_app_whole_process\static\readable_sample\\'+ value + '.pdf')
        return json.dumps({'text': tmp})
    elif folder == 'Upload other files' and contents is not None:
        tmp = readable_pdf_to_txt(r'\Users\Sri\Google Drive\Icube\FloridaBlue\Code\web_app_whole_process\web_app_whole_process\static\other\\'+ filename[:-4]+ '.pdf')
        return json.dumps({'text': tmp})
    
    
#@app.callback(Output('txt_view', 'src'),
#              [Input('doc_dropdown','value')])
#def update_txt(file):  
#    if file != 'pdf':
#        return 'static/'+file+'.txt' 
#    else:
#        return 'static/txt.png'
@app.callback(Output('txt_view', 'children'),
               [Input('doc-dropdown', 'value'),
                Input('upload-data', 'contents'),
                Input('trans-type', 'value'),
                Input('intermediate-value', 'children')],
              [State('upload-data', 'filename')])
def update_txt(value, contents, folder, text, filename):
#    if folder == 'sample' and value != 'pdf':
##        return 'static/sample/' + value +'.txt'
#        return json.loads(text)['text']
#    elif folder =='other' and contents is not None:
#        return json.loads(text)['text']
    if text is not None:
        return json.loads(text)['text']
    else:
        return '\n\n raw text'

        
#@app.callback(Output('seg_view', 'src'),
#              [Input('doc_dropdown','value')])
#def update_seg(file):
#    if file != 'pdf':
#        return 'static/segm/'+file+'.txt' 
#    else:
#        return 'static/txt.png'
        
@app.callback(Output('test-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('doc-dropdown', 'value'),
               Input('trans-type', 'value'),
               Input('intermediate-value', 'children')],
              [State('upload-data', 'filename')])
def update_seg(contents, value, folder, text, filename):
    if contents is not None and folder == 'Upload other files':
#        rawtxt = parse_contents(contents, filename)
#        children = rawtxt
        rawtxt = json.loads(text)['text']
        header, result = split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt)
    #        return result
        return '\n==========\n'.join(result)
    elif value != 'pdf' and folder == 'Select a sample file in dropdown':
#        with open('static/sample/' + value +'.txt') as txt:
#            rawtxt = txt.read()
        rawtxt = json.loads(text)['text']
        header, result = split_by_header(pp_start, pp_end, header_lang, normal_lang, hp_list, match_list, rawtxt)
    #        return result
        return '\n==========\n'.join(result)
    else:
        return '\n\n segmented text'



@app.callback(Output('ner_view', 'children'),
              [Input('ner-tabs', 'value'),
               Input('upload-data', 'contents'),
               Input('doc-dropdown', 'value'),
               Input('trans-type', 'value')])
def update_ner(tab, contents, value, folder):
    if value != 'pdf' and folder == 'Select a sample file in dropdown':
        if tab == 'tab-1':
            return html.Div(
                html.Iframe(
                    id = 'ner-view-1',
                    src='/static/ner/' + value + '_0.txt',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
        if tab == 'tab-2':
            return html.Div(
                html.Iframe(
                    id = 'ner-view-2',
                    src='/static/ner/' + value + '_1.txt',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
        if tab == 'tab-3':
            return html.Div(
                html.Iframe(
                    id = 'ner-view-3',
                    src='/static/ner/' + value + '_2.txt',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
        if tab == 'tab-4':
            return html.Div(
                html.Iframe(
                    id = 'ner-view-4',
                    src='/static/ner/' + value + '_3.txt',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
        if tab == 'tab-5':
            return html.Div(
                html.Iframe(
                    id = 'ner-view-5',
                    src='/static/ner/' + value + '_4.txt',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
    else:
        return html.Div(
                html.Iframe(
                    id = 'ner-view-1',
                    src='/static/txt.png',
                    style={'width': '100%', 'height':'100%'}
                ), style={'width': '100%', 'height':'100%'}
            )
             

if __name__ == '__main__':
    #os.chdir(r'/Users/xuqinxin/PycharmProjects/web_app/')
    app.run_server(debug=True)