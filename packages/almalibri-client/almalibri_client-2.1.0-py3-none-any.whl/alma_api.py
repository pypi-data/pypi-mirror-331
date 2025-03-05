#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import csv
import click
from datetime import datetime
import pandas as pd
import urllib.parse

API_HOST = 'https://almalibri.it/'
# Path API Elenco università
API_UNI_LIST_PATH = 'api/lista_uni/'
# Path API adozioni
API_ADOPTED_BOOKS_PATH = 'api/adozioni/?' 
# Path API programmi
API_SYLLABUS_PATH = 'api/biblio_request/?'
# ricerca full textr
API_FULLTEXT_PATH = 'api/ricerca/fulltext/?'

@click.group()
def cli():
    pass

class PublisherAdoptedBooks():
    def __init__(self, user_vars, json_file_name):
        self.json_file_name = json_file_name
        #self.ay = str(ay)
        self.user_vars  = user_vars

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def convert_json_to_csv(self, json_file_name, csv_file_name):
        with open(json_file_name, 'r', encoding='utf-8') as sh:
            data = json.load(sh)
        # va aperto con newline='' altrimenti il fine riga viene due volte
        with open(csv_file_name, 'w', newline='', encoding='utf-8') as dh:
            writer = writer = csv.writer(dh, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            if data:
                header = list(data[0].keys())
                writer.writerow(header)
            for d in data: writer.writerow(list(d.values()))

    def get_json(self, api_url):
        r = requests.get(api_url, stream=True)
        # Solleva un'eccezione se la richiesta http non è andata a buon fine
        r.raise_for_status()
        res = json.loads(r.content)
        # Controllo di eventuale messaggio di errore
        if res['request_status'] != 'ok':
            raise click.ClickException('Errore:','Forse è necessario controllare l\'autorizzazione all\'accesso ad Almalibri.')
            #raise Exception('Errore:', res['request_status']+'. Forse è necessario controllare l\'autorizzazione all\'accesso ad Almalibri.')
        return res

    def get_unicod_list(self):
        content = self.get_json(API_HOST + API_UNI_LIST_PATH)
        # content['data'] contiene un dictionary per ogni record, cioè {nome_campo1: valore, nome_campo2: valore, ecc.}
        res = [j['uni_cod'] for j in content['data']]
        return res

    def append_to_file(self, fh, data):
        if data:
            l = [json.dumps(j) for j in data]
            # Se l'offset corrente del file è maggiore di 1...
            if fh.tell() > 1:
                fh.write(', ')
            fh.write(', '.join(l))
    
    def get_syllabus(self):
        pass


    def get_all_adopted_books(self):
        adozioni = pd.DataFrame()
        if not self.user_vars['uni_cod']:
            del self.user_vars['uni_cod']
            # Chiama API elenco università
            uni_list = self.get_unicod_list()
            for uni_cod in uni_list:
                params = ['uni_cod='+uni_cod]
                for k in self.user_vars:
                    params.append(f"{k}={self.user_vars[k]}")                   
                content = self.get_json(API_HOST + API_ADOPTED_BOOKS_PATH + '&'.join(params))
                click.echo(content['request_op'])
                df = pd.json_normalize(content['data'])
                adozioni = pd.concat([adozioni, df], ignore_index=True)
                # I dati arrivano paginati a 1000 record alla volta
                # content['next_page_url'] contiene url per andare alla pagina successiva
                while content.get('next_page_url', '') != '':
                    content = self.get_json(content['next_page_url'])
                    df = pd.json_normalize(content['data'])
                    adozioni = pd.concat([adozioni, df], ignore_index=True)
        else:
            params = []
            for k in self.user_vars:
                params.append(f"{k}={self.user_vars[k]}")                   
            content = self.get_json(API_HOST + API_ADOPTED_BOOKS_PATH + '&'.join(params))
            click.echo(content['request_op'])
            df = pd.json_normalize(content['data'])
            adozioni = pd.concat([adozioni, df], ignore_index=True)
            # I dati arrivano paginati a 1000 record alla volta
            # content['next_page_url'] contiene url per andare alla pagina successiva
            while content.get('next_page_url', '') != '':
                content = self.get_json(content['next_page_url'])
                df = pd.json_normalize(content['data'])
                adozioni = pd.concat([adozioni, df], ignore_index=True)
        adozioni.to_csv(self.json_file_name+'.csv', index=False)

class FullTextBooks(PublisherAdoptedBooks):
    def __init__(self, user_vars, json_file_name):
        super().__init__(user_vars, json_file_name)
        self.api_url = API_HOST + API_FULLTEXT_PATH

    def get_data(self):
        ft = pd.DataFrame()
        if not self.user_vars['uni_cod']:
            del self.user_vars['uni_cod']
            # Chiama API elenco università
            uni_list = self.get_unicod_list()
            for uni_cod in uni_list:
                params = {'uni_cod': uni_cod}
                params.update(self.user_vars)
                encoded_params = urllib.parse.urlencode(params)
                content = self.get_json(self.api_url + encoded_params)
                click.echo(content['request_op'])
                df = pd.json_normalize(content['data'])
                ft = pd.concat([ft, df], ignore_index=True)
                # I dati arrivano paginati a 1000 record alla volta
                # content['next_page_url'] contiene url per andare alla pagina successiva
                while content.get('next_page_url', '') != '':
                    content = self.get_json(content['next_page_url'])
                    df = pd.json_normalize(content['data'])
                    ft = pd.concat([ft, df], ignore_index=True)
        else:
            params = self.user_vars
            encoded_params = urllib.parse.urlencode(params)
            content = self.get_json(self.api_url + encoded_params)
            click.echo(content['request_op'])
            df = pd.json_normalize(content['data'])
            ft = pd.concat([ft, df], ignore_index=True)
            # I dati arrivano paginati a 1000 record alla volta
            # content['next_page_url'] contiene url per andare alla pagina successiva
            while content.get('next_page_url', '') != '':
                content = self.get_json(content['next_page_url'])
                df = pd.json_normalize(content['data'])
                ft = pd.concat([ft, df], ignore_index=True)
        ft.to_csv(self.json_file_name+'.csv', index=False)

class SyllabiBooks(PublisherAdoptedBooks):
    def __init__(self, api_url, user_vars, json_file_name):
        super().__init__(user_vars, json_file_name)
        self.api_url = api_url

    def get_syllabus(self):
        syllabi = pd.DataFrame()
        if not self.user_vars['uni_cod']:
            del self.user_vars['uni_cod']
            # Chiama API elenco università
            uni_list = self.get_unicod_list()
            for uni_cod in uni_list:
                params = ['uni_cod='+uni_cod]
                for k in self.user_vars:
                    params.append(f"{k}={self.user_vars[k]}")                   
                content = self.get_json(self.api_url + '&'.join(params))
                click.echo(content['request_op'])
                df = pd.json_normalize(content['data'])
                syllabi = pd.concat([syllabi, df], ignore_index=True)
                # I dati arrivano paginati a 1000 record alla volta
                # content['next_page_url'] contiene url per andare alla pagina successiva
                while content.get('next_page_url', '') != '':
                    content = self.get_json(content['next_page_url'])
                    df = pd.json_normalize(content['data'])
                    syllabi = pd.concat([syllabi, df], ignore_index=True)
        else:
            params = []
            for k in self.user_vars:
                params.append(f"{k}={self.user_vars[k]}")                   
            content = self.get_json(self.api_url + '&'.join(params))
            click.echo(content['request_op'])
            df = pd.json_normalize(content['data'])
            syllabi = pd.concat([syllabi, df], ignore_index=True)
            # I dati arrivano paginati a 1000 record alla volta
            # content['next_page_url'] contiene url per andare alla pagina successiva
            while content.get('next_page_url', '') != '':
                content = self.get_json(content['next_page_url'])
                df = pd.json_normalize(content['data'])
                syllabi = pd.concat([syllabi, df], ignore_index=True)
        syllabi.to_csv(self.json_file_name+'.csv', index=False)


now = datetime.now()

@cli.command()
@click.argument('filename', required=False)
@click.option('--uni_cod')
@click.option('--a_a', required=True)
@click.option('--query', required=True)
def fulltext(filename, uni_cod, a_a, query):
    """
    Scarica i programmi e le bibliografie per università e anno accademico.
    """
    if not filename:
        filename = now.strftime("%Y%m%d_%H%M%S")
    else:
        filename = filename
    
    user_vars = {'uni_cod':uni_cod, 'a_a':a_a, 'query':query}
    api_url = 'https://almalibri.it/api/ricerca/fulltext/?'
    cc = FullTextBooks(user_vars, filename)
    cc.get_data()
    return None


@cli.command()
@click.argument('filename', required=False)
@click.option('--uni_cod')
@click.option('--a_a', required=True)
@click.option('--laurea_nome')
@click.option('--laurea_tipo')
@click.option('--laurea_classe_cod')
@click.option('--curr_nome')
@click.option('--materia_nome')
@click.option('--materia_ssd_cod')
@click.option('--curr_materia_anno')
@click.option('--curr_materia_periodo')
@click.option('--insegnamento_prof')
@click.option('--isbn')
@click.option('--autori')
@click.option('--titolo')
@click.option('--editore')
@click.option('--testo_obb')
@click.option('--page')
def programmi(filename, uni_cod, a_a, laurea_nome, laurea_tipo, 
        laurea_classe_cod, curr_nome, materia_nome, materia_ssd_cod, curr_materia_anno, 
        curr_materia_periodo, insegnamento_prof, isbn, autori, titolo, editore, testo_obb, page):
    """
    Scarica i libri di testo dei corsi di studio per università e anno accademico.
    """
    if not filename:
        filename = now.strftime("%Y%m%d_%H%M%S")
    else:
        filename = filename
    
    user_vars = {'uni_cod':uni_cod, 'a_a':a_a}
    if laurea_nome:
        user_vars['laurea_nome'] = laurea_nome
    if laurea_tipo:
        user_vars['laurea_tipo'] = laurea_tipo
    if laurea_classe_cod:
        user_vars['laurea_classe_cod'] = laurea_classe_cod
    if curr_nome:
        user_vars['curr_nome'] = curr_nome
    if materia_nome:
        user_vars['materia_nome'] = materia_nome
    if materia_ssd_cod: 
        user_vars['materia_ssd_cod'] = materia_ssd_cod
    if curr_materia_anno:
        user_vars['curr_materia_anno'] = curr_materia_anno
    if curr_materia_periodo:
        user_vars['curr_materia_periodo'] = curr_materia_periodo
    if insegnamento_prof:
        user_vars['insegnamento_prof'] = insegnamento_prof
    if isbn:
        user_vars['isbn'] = isbn
    if autori:
        user_vars['autori'] = autori
    if titolo:
        user_vars['titolo'] = titolo
    if editore:
        user_vars['editore'] = editore
    if testo_obb:
        user_vars['testo_obb'] = testo_obb
    if page:
        user_vars['page'] = page
    api_url = 'https://almalibri.it/api/biblio_request/?'
    cc = SyllabiBooks(api_url, user_vars, filename)
    cc.get_syllabus()
    #cc.convert_json_to_csv(filename, filename.replace('.json', '.csv'))
    return None


@click.command()
def unicod():
    """
    Scarica l'elenco delle università aggiornate all'anno accademico indicato.
    """
    api_url = 'https://almalibri.it/api/lista_uni/'
    p = PublisherAdoptedBooks({'a_a':'2023'}, 'uni_cod.json')
    res = p.get_json(api_url)
    with open('uni_cod.csv', 'w', newline='', encoding='utf-8') as dh:
        writer = writer = csv.writer(dh, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        if res['data']:
            header = list(res['data'][0].keys())
            writer.writerow(header)
        for d in res['data']: writer.writerow(list(d.values()))
    return None



@click.command()
@click.argument('filename', required=False)
@click.option('--uni_cod')
@click.option('--a_a', required=True)
@click.option('--laurea_nome')
@click.option('--laurea_tipo')
@click.option('--laurea_classe_cod')
@click.option('--curr_nome')
@click.option('--materia_nome')
@click.option('--materia_ssd_cod')
@click.option('--curr_materia_anno')
@click.option('--curr_materia_periodo')
@click.option('--insegnamento_prof')
@click.option('--isbn')
@click.option('--autori')
@click.option('--titolo')
@click.option('--editore')
@click.option('--testo_obb')
@click.option('--page')
@click.option('--ult_agg')
def adozioni(filename, uni_cod, a_a, laurea_nome, laurea_tipo, 
        laurea_classe_cod, curr_nome, materia_nome, materia_ssd_cod, curr_materia_anno, 
        curr_materia_periodo, insegnamento_prof, isbn, autori, titolo, editore, testo_obb, page, ult_agg):
    """
    Ecco un esempio di ricerca di adozioni per università, anno accademico e nome del docente.
    uni_cod=polito,
    a_a=2022,
    laurea_nome=nome,
    laurea_tipo=L,
    laurea_classe_cod=L-20,
    curr_nome=,
    materia_nome=didattica della chimica,
    materia_ssd_cod=M-FIL/05,
    curr_materia_anno=2,
    curr_materia_periodo=,
    insegnamento_prof=Mario Rossi,
    isbn=9788883534614,
    autori=Renzo Canestrari,
    titolo=bricolage
    editore=clueb,
    testo_obb=obb,
    page=1,
    """
    if not filename:
        filename = now.strftime("%Y%m%d_%H%M%S")
    else:
        filename = filename
    
    user_vars = {'uni_cod':uni_cod, 'a_a':a_a}
    if laurea_nome:
        user_vars['laurea_nome'] = laurea_nome
    if laurea_tipo:
        user_vars['laurea_tipo'] = laurea_tipo
    if laurea_classe_cod:
        user_vars['laurea_classe_cod'] = laurea_classe_cod
    if curr_nome:
        user_vars['curr_nome'] = curr_nome
    if materia_nome:
        user_vars['materia_nome'] = materia_nome
    if materia_ssd_cod: 
        user_vars['materia_ssd_cod'] = materia_ssd_cod
    if curr_materia_anno:
        user_vars['curr_materia_anno'] = curr_materia_anno
    if curr_materia_periodo:
        user_vars['curr_materia_periodo'] = curr_materia_periodo
    if insegnamento_prof:
        user_vars['insegnamento_prof'] = insegnamento_prof
    if isbn:
        user_vars['isbn'] = isbn
    if autori:
        user_vars['autori'] = autori
    if titolo:
        user_vars['titolo'] = titolo
    if editore:
        user_vars['editore'] = editore
    if testo_obb:
        user_vars['testo_obb'] = testo_obb
    if page:
        user_vars['page'] = page
    if ult_agg:
        user_vars['ult_agg'] = ult_agg
    cc = PublisherAdoptedBooks(user_vars, filename)
    cc.get_all_adopted_books()
    #cc.convert_json_to_csv(filename, filename.replace('.json', '.csv'))
    return None
    
cli.add_command(adozioni)
cli.add_command(programmi)
cli.add_command(fulltext)
cli.add_command(unicod)

if __name__ == '__main__':
    cli()

