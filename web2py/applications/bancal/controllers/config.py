# -*- coding: utf-8 -*-


def alimentos():
    db.Alimento.id.readable=False
    search_text=request.get_vars.search_text 
    query=search_query(db.Alimento.id,search_text, [db.Alimento.Descripcion]) 

    grid = SQLFORM.grid(query, search_widget=search_form,editable=False, deletable=False, create=False,details=True,maxtextlength=40, orderby=db.Alimento.Codigo)

    #grid = SQLFORM.smartgrid(db.Alimento,editable=False, deletable=False, create=False,details=False,maxtextlength=40)
    #grid = SQLFORM.grid(db.Alimento)

    #from plugin_solidtable import SOLIDTABLE, OrderbySelector
    #rows = db().select(db.Alimento.ALL)
    #grid = SOLIDTABLE(rows,renderstyle=True, linkto=URL('show'))


    return locals()


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def search_form(self,url): 
    form = FORM('', 
  
INPUT(_name='search_text',_value=request.get_vars.keywords, 

               _style='width:200px;', 
               _id='searchText'), 
         INPUT(_type='submit',_value=T('Search')), 
         INPUT(_type='submit',_value=T('Clear'), 
         _onclick="jQuery('#keywords').val('');"), 

         _method="GET",_action=url) 

    return form 

def search_query(tableid,search_text,fields): 
    words= search_text.split(' ') if search_text else [] 
    query=tableid<0 #empty query 
    for field in fields: 
        new_query=tableid>0 
        for word in words: 
            new_query=new_query&field.contains(word) 
        query=query|new_query 
    return query 

